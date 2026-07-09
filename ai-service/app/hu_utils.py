"""HU 转换与肺实质 mask 工具（各方案共用）。"""
from __future__ import annotations

from typing import List, Tuple

import numpy as np
import pydicom
from pydicom.pixel_data_handlers.util import apply_modality_lut
from scipy import ndimage
from skimage.measure import find_contours


def pixel_array_to_hu(ds: pydicom.Dataset, arr: np.ndarray) -> np.ndarray:
    """按每张 DICOM 的 RescaleSlope/Intercept（或 Modality LUT）转 HU。"""
    slope = float(getattr(ds, "RescaleSlope", 1) or 1)
    intercept = float(getattr(ds, "RescaleIntercept", 0) or 0)
    if slope == 1 and intercept == 0:
        try:
            return apply_modality_lut(arr, ds).astype(np.float32)
        except Exception:
            pass
    return (arr.astype(np.float32) * slope + intercept).astype(np.float32)


def slice_spacing_z(ds: pydicom.Dataset) -> float:
    for attr in ("SpacingBetweenSlices", "SliceThickness"):
        val = getattr(ds, attr, None)
        if val is not None:
            try:
                v = float(val)
                if v > 0:
                    return v
            except (TypeError, ValueError):
                pass
    return 1.0


def lung_parenchyma_2d(slice_hu: np.ndarray) -> np.ndarray:
    """肺实质：排除空气(-1000)、软组织与骨。"""
    body = slice_hu > -900
    return body & (slice_hu > -950) & (slice_hu < -250)


def lung_parenchyma_3d(volume: np.ndarray) -> np.ndarray:
    body = volume > -900
    return body & (volume > -950) & (volume < -250)


def refine_lung_mask(lung_mask: np.ndarray, volume: np.ndarray, dilate_iters: int = 1) -> np.ndarray:
    """轻量膨胀后回缩，避免 mask 覆盖胸壁/皮下脂肪。"""
    mask = lung_mask.astype(bool)
    if dilate_iters > 0:
        structure = np.ones((3, 3, 3), dtype=bool) if mask.ndim == 3 else np.ones((3, 3), dtype=bool)
        mask = ndimage.binary_dilation(mask, structure=structure, iterations=dilate_iters)
    structure = np.ones((3, 3, 3), dtype=bool) if mask.ndim == 3 else np.ones((3, 3), dtype=bool)
    mask = ndimage.binary_erosion(mask, structure=structure, iterations=1)
    parenchyma = lung_parenchyma_3d(volume) if volume.ndim == 3 else lung_parenchyma_2d(volume)
    return mask & parenchyma


def _hu_channel_windows(spacing_z: float) -> Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]]:
    if spacing_z >= 5.0:
        return (-780.0, -300.0), (15.0, 85.0), (85.0, 280.0)
    if spacing_z >= 3.0:
        return (-820.0, -280.0), (12.0, 90.0), (90.0, 300.0)
    return (-850.0, -320.0), (15.0, 80.0), (80.0, 280.0)


def ggo_hu_window(spacing_z: float) -> Tuple[float, float]:
    if spacing_z >= 5.0:
        return -780.0, -300.0
    if spacing_z >= 3.0:
        return -820.0, -280.0
    return -850.0, -320.0


def ggo_candidate_mask(
    lung_mask: np.ndarray,
    hu: np.ndarray,
    spacing_z: float,
) -> np.ndarray:
    """仅 GGO 密度窗（层厚自适应）。"""
    lung = lung_mask.astype(bool)
    ggo, _, _ = _hu_channel_windows(spacing_z)
    return lung & (hu >= ggo[0]) & (hu <= ggo[1])


def nodule_candidate_mask(
    lung_mask: np.ndarray,
    hu: np.ndarray,
    spacing_z: float,
) -> np.ndarray:
    """双通道 + 高密度：磨玻璃 / 实性结节 / 钙化灶（参考临床 HU 表）。"""
    lung = lung_mask.astype(bool)
    ggo, solid, calc = _hu_channel_windows(spacing_z)
    ggo_m = lung & (hu >= ggo[0]) & (hu <= ggo[1])
    solid_m = lung & (hu >= solid[0]) & (hu <= solid[1])
    calc_m = lung & (hu >= calc[0]) & (hu <= calc[1])
    return ggo_m | solid_m | calc_m


def classify_nodule_hu(mean_hu: float) -> Tuple[str, str, bool]:
    """返回 (type, label_cn, is_valid)。无效 HU（空气/脂肪/骨）返回 is_valid=False。"""
    if mean_hu < -920 or mean_hu > 350:
        return "排除", "非结节密度", False
    if -850 <= mean_hu <= -280:
        return "磨玻璃结节", "疑似磨玻璃结节", True
    if 12 <= mean_hu <= 90:
        return "肺结节", "疑似实性结节", True
    if 80 <= mean_hu <= 280:
        return "高密度结节", "疑似高密度结节", True
    if -280 < mean_hu < 12:
        return "磨玻璃结节", "疑似磨玻璃结节", True
    return "排除", "密度不符", False


def is_valid_nodule_hu(mean_hu: float) -> bool:
    return classify_nodule_hu(mean_hu)[2]


def touches_image_border(mask: np.ndarray, margin: int = 2) -> bool:
    if not mask.any():
        return True
    coords = np.argwhere(mask)
    if mask.ndim == 2:
        h, w = mask.shape
        rows, cols = coords[:, 0], coords[:, 1]
        return (
            rows.min() <= margin or cols.min() <= margin
            or rows.max() >= h - 1 - margin or cols.max() >= w - 1 - margin
        )
    z, y, x = coords[:, 0], coords[:, 1], coords[:, 2]
    d, h, w = mask.shape
    return (
        y.min() <= margin or x.min() <= margin
        or y.max() >= h - 1 - margin or x.max() >= w - 1 - margin
    )


def mean_hu_in_mask(hu: np.ndarray, mask: np.ndarray) -> float:
    sel = hu[mask.astype(bool)]
    if sel.size == 0:
        return float("nan")
    return float(np.median(sel))


def extract_contour_normalized(
    sl_mask: np.ndarray,
    y_offset: int,
    x_offset: int,
    rows: int,
    cols: int,
    max_points: int = 64,
) -> List[dict]:
    if sl_mask is None or not sl_mask.any():
        return []
    h, w = sl_mask.shape[:2]
    if h < 2 or w < 2:
        return []
    contours = find_contours(sl_mask.astype(float), 0.5)
    if not contours:
        return []
    contour = max(contours, key=len)
    if len(contour) < 4:
        return []
    step = max(1, len(contour) // max_points)
    points: List[dict] = []
    for row, col in contour[::step]:
        gx = float(x_offset + col)
        gy = float(y_offset + row)
        points.append({
            "x": round(min(max(gx / cols, 0.0), 1.0), 5),
            "y": round(min(max(gy / rows, 0.0), 1.0), 5),
        })
    if len(points) >= 3:
        points.append(points[0])
    return points
