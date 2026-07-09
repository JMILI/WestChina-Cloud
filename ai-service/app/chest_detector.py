"""
胸部 CT 肺结节检测（3D 连通域 + HU 窗宽窗位启发式）。

说明：此为可本地 GPU/CPU 运行的实用算法，适合 MVP 与演示；
后续可替换为 TotalSegmentator / 深度学习模型而不改 API 契约。
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

import numpy as np
from scipy import ndimage
from skimage.measure import find_contours, label, regionprops

from .config import settings


CHEST_KEYWORDS = ("CHEST", "THORAX", "THORACIC", "LUNG", "胸", "肺")


def is_chest_body_part(body_part: str) -> bool:
    if not body_part:
        return False
    upper = body_part.upper()
    return any(k in upper or k in body_part for k in CHEST_KEYWORDS)


def _segment_lungs(volume: np.ndarray) -> np.ndarray:
    """粗分割肺区：体素 HU 在肺实质常见范围内。"""
    body = volume > -900
    lung_like = (volume < -400) & (volume > -950)
    mask = lung_like & body

    structure = np.ones((3, 3, 3), dtype=bool)
    mask = ndimage.binary_opening(mask, structure=structure, iterations=1)
    mask = ndimage.binary_closing(mask, structure=structure, iterations=2)

    labeled = label(mask)
    if labeled.max() == 0:
        return mask

    # 保留最大的两个连通域（左右肺）
    counts = np.bincount(labeled.ravel())
    counts[0] = 0
    keep_ids = np.argsort(counts)[-2:]
    lung = np.isin(labeled, keep_ids)
    lung = ndimage.binary_dilation(lung, iterations=1)
    return lung


def _lesion_type(mean_hu: float) -> Tuple[str, str]:
    if mean_hu < -100:
        return "磨玻璃结节", "疑似磨玻璃结节"
    if mean_hu < 50:
        return "肺结节", "疑似肺结节"
    return "高密度结节", "疑似高密度结节"


def _confidence(mean_hu: float, solidity: float, diameter_mm: float) -> float:
    hu_score = 1.0 - min(abs(mean_hu + 50) / 250.0, 1.0)
    size_score = 1.0 if 4 <= diameter_mm <= 20 else 0.65
    shape_score = min(max(solidity, 0.0), 1.0)
    return round(float(0.35 * hu_score + 0.35 * size_score + 0.30 * shape_score), 3)


def _extract_contour(
    sl_mask: np.ndarray,
    y_offset: int,
    x_offset: int,
    rows: int,
    cols: int,
    max_points: int = 48,
) -> List[Dict[str, float]]:
    """从分割 mask 提取不规则轮廓，坐标归一化到 [0,1]。"""
    if sl_mask is None or not sl_mask.any():
        return []
    h, w = sl_mask.shape[:2]
    if h < 2 or w < 2:
        return []

    contours = find_contours(sl_mask.astype(float), 0.5)
    if not contours:
        return []

    contour = max(contours, key=len)
    step = max(1, int(len(contour) / max_points))
    sampled = contour[::step]
    points: List[Dict[str, float]] = []
    for row, col in sampled:
        gx = float(x_offset + col)
        gy = float(y_offset + row)
        points.append(
            {
                "x": round(min(max(gx / cols, 0.0), 1.0), 5),
                "y": round(min(max(gy / rows, 0.0), 1.0), 5),
            }
        )
    if len(points) >= 3:
        points.append(points[0])
    return points


def detect_chest_lesions(
    volume: np.ndarray,
    spacing: Tuple[float, float, float],
    rows: int,
    cols: int,
    lung_mask: np.ndarray | None = None,
) -> Dict[str, Any]:
    spacing_z, spacing_y, spacing_x = spacing
    voxel_vol_mm3 = spacing_z * spacing_y * spacing_x

    if lung_mask is None:
        lung_mask = _segment_lungs(volume)
    else:
        lung_mask = lung_mask.astype(bool)
    lung_region = lung_mask
    candidate = lung_mask & (volume > -200) & (volume < 100)
    candidate = ndimage.binary_opening(candidate, iterations=1)

    labeled = label(candidate)
    all_regions = regionprops(labeled, intensity_image=volume)
    lesions: List[Dict[str, Any]] = []

    for idx, region in enumerate(all_regions):
        if len(lesions) >= settings.max_lesions:
            break

        z0, y0, x0, z1, y1, x1 = region.bbox
        cz, cy, cx = region.centroid
        zi, yi, xi = int(cz), int(cy), int(cx)
        if zi < 0 or yi < 0 or xi < 0:
            continue
        if zi >= volume.shape[0] or yi >= volume.shape[1] or xi >= volume.shape[2]:
            continue
        if not lung_mask[zi, yi, xi]:
            continue

        extent_z = max((z1 - z0) * spacing_z, spacing_z)
        extent_y = max((y1 - y0) * spacing_y, spacing_y)
        extent_x = max((x1 - x0) * spacing_x, spacing_x)
        long_axis = max(extent_x, extent_y, extent_z)
        short_axis = min(extent_x, extent_y, extent_z)
        diameter_mm = (long_axis + short_axis) / 2.0

        if diameter_mm < settings.min_nodule_mm or diameter_mm > settings.max_nodule_mm:
            continue

        # 取面积最大的层面作为展示层（0-based）
        slice_areas = []
        for z in range(z0, z1):
            sl = labeled[z, y0:y1, x0:x1] == region.label
            slice_areas.append(sl.sum())
        best_rel = int(np.argmax(slice_areas))
        slice_index = z0 + best_rel

        sl_mask = labeled[slice_index, y0:y1, x0:x1] == region.label
        if not sl_mask.any():
            continue

        yy, xx = np.where(sl_mask)
        min_y, max_y = y0 + yy.min(), y0 + yy.max()
        min_x, max_x = x0 + xx.min(), x0 + xx.max()

        # 归一化 bbox（相对图像宽高）
        bbox = {
            "x": float(min_x) / cols,
            "y": float(min_y) / rows,
            "width": float(max(1, max_x - min_x)) / cols,
            "height": float(max(1, max_y - min_y)) / rows,
        }
        contour = _extract_contour(sl_mask, y0, x0, rows, cols)

        mean_hu = float(region.mean_intensity)
        lesion_type, label_cn = _lesion_type(mean_hu)
        area_mm2 = float(region.area) * spacing_y * spacing_x
        volume_mm3 = float(region.area) * voxel_vol_mm3
        solidity = float(region.solidity) if region.solidity is not None else 0.7

        lesions.append(
            {
                "id": f"L{idx + 1}",
                "label": label_cn,
                "type": lesion_type,
                "confidence": _confidence(mean_hu, solidity, diameter_mm),
                "sliceIndex": int(slice_index),
                "bbox": bbox,
                "contour": contour,
                "diameterMm": round(diameter_mm, 1),
                "longAxisMm": round(long_axis, 1),
                "shortAxisMm": round(short_axis, 1),
                "areaMm2": round(area_mm2, 1),
                "volumeMm3": round(volume_mm3, 1),
                "hu": round(mean_hu, 1),
            }
        )

    lesions.sort(key=lambda x: x["confidence"], reverse=True)
    return {
        "lesions": lesions,
        "stats": {
            "candidates": len(all_regions),
            "lesionCount": len(lesions),
            "lungVoxels": int(lung_mask.sum()),
            "volumeShape": [int(volume.shape[0]), rows, cols],
        },
    }


def gpu_available() -> bool:
    try:
        import torch

        return bool(torch.cuda.is_available())
    except Exception:
        return False
