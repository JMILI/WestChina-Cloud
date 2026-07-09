"""方案 A：肺区智能筛查。

全序列（series）：TotalSegmentator 肺 mask + 3D 连通域 + solidity/体积过滤
              + 肺门区抑制 + 跨层连续性验证（P2）。
当前层（single）：lung_segment_2d + 2D 连通域 + 面积/圆度过滤 + 肺门区抑制。
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Tuple

import numpy as np
from scipy import ndimage
from skimage.measure import find_contours, label, regionprops

from .config import settings
from .hu_utils import (
    classify_nodule_hu,
    extract_contour_normalized,
    mean_hu_in_mask,
    nodule_candidate_mask,
    refine_lung_mask,
    touches_image_border,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# P2: 血管/肺门抑制规则
# ---------------------------------------------------------------------------

def _is_hilar_region(cy: float, cx: float, rows: int, cols: int, zi: int, z_count: int) -> bool:
    """判断重心是否在肺门高危区（中央区域 + 序列中段层面）。

    肺门区血管密集，假阳性多来自血管断面/淋巴结。
    此区域内的候选降低置信度但不直接剔除。
    """
    y_center = abs(cy / max(rows, 1) - 0.5)
    x_center = abs(cx / max(cols, 1) - 0.5)
    z_mid = abs(zi / max(z_count, 1) - 0.5)
    return y_center < 0.25 and x_center < 0.25 and z_mid < 0.35


def _is_hilar_region_2d(cy: float, cx: float, rows: int, cols: int) -> bool:
    """2D 版肺门区判断（无 z 轴信息，更宽松）。"""
    y_center = abs(cy / max(rows, 1) - 0.5)
    x_center = abs(cx / max(cols, 1) - 0.5)
    return y_center < 0.25 and x_center < 0.22


def _has_3d_continuity(
    region_label: int,
    labeled: np.ndarray,
    z0: int, z1: int,
    y0: int, y1: int,
    x0: int, x1: int,
    min_continuous: int = 2,
) -> bool:
    """检查 3D 连通域在 z 方向是否跨足够多层面连续出现。

    真结节通常跨 2+ 层面连续，血管断面/噪声在层面间跳跃。
    """
    if z1 - z0 < min_continuous:
        return False
    continuous = 0
    for z in range(z0, z1):
        sl = labeled[z, y0:y1, x0:x1] == region_label
        if sl.sum() > 0:
            continuous += 1
            if continuous >= min_continuous:
                return True
        else:
            continuous = 0
    return continuous >= min_continuous


# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------


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
    return extract_contour_normalized(sl_mask, y_offset, x_offset, rows, cols, max_points)


def _adaptive_hu_range(spacing_z: float) -> Tuple[float, float]:
    """返回双通道合并范围（仅用于日志展示）。"""
    if spacing_z >= 5.0:
        return -750.0, 110.0
    if spacing_z >= 3.0:
        return -800.0, 120.0
    return settings.ggo_hu_min, settings.solid_hu_max


def _adaptive_continuity_min(spacing_z: float) -> int:
    """厚层序列单层即可成灶，降低跨层连续性要求。"""
    if spacing_z >= 5.0:
        return 1
    if spacing_z >= 3.0:
        return max(1, settings.continuity_min_slices - 1)
    return settings.continuity_min_slices


def _adaptive_solidity_min(mean_hu: float, spacing_z: float) -> float:
    """磨玻璃结节 solidity 偏低，厚层时进一步放宽。"""
    base = settings.solidity_min
    if mean_hu < -100:
        base = min(base, 0.50)
    if spacing_z >= 5.0:
        base = min(base, 0.45)
    return base


def detect_series(
    volume: np.ndarray,
    spacing: Tuple[float, float, float],
    rows: int,
    cols: int,
    lung_mask: np.ndarray,
) -> Dict[str, Any]:
    """对全序列 3D 体数据进行候选筛选。

    P2 新增：肺门区置信度惩罚 + 跨层连续性验证。
    """
    spacing_z, spacing_y, spacing_x = spacing
    voxel_vol_mm3 = spacing_z * spacing_y * spacing_x
    z_count = int(volume.shape[0])

    lung_mask = refine_lung_mask(lung_mask.astype(bool), volume, dilate_iters=settings.lung_dilate_radius)

    hu_min, hu_max = _adaptive_hu_range(spacing_z)
    continuity_min = _adaptive_continuity_min(spacing_z)
    candidate = nodule_candidate_mask(lung_mask, volume, spacing_z)
    candidate = ndimage.binary_opening(candidate, iterations=1)

    labeled = label(candidate)
    all_regions = regionprops(labeled, intensity_image=volume)
    lesions: List[Dict[str, Any]] = []

    hilar_suppressed = 0
    continuity_rejected = 0
    volume_rejected = 0
    solidity_rejected = 0

    border_rejected = 0
    hu_rejected = 0

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

        vol_mm3 = float(region.area) * voxel_vol_mm3
        if vol_mm3 < settings.volume_min_mm3 or vol_mm3 > settings.volume_max_mm3:
            volume_rejected += 1
            continue

        slice_areas = []
        for z in range(z0, z1):
            sl = labeled[z, y0:y1, x0:x1] == region.label
            slice_areas.append(sl.sum())
        best_rel = int(np.argmax(slice_areas))
        slice_index = z0 + best_rel

        sl_mask = labeled[slice_index, y0:y1, x0:x1] == region.label
        if not sl_mask.any():
            continue
        if touches_image_border(sl_mask, margin=3):
            border_rejected += 1
            continue

        mean_hu = mean_hu_in_mask(volume[slice_index, y0:y1, x0:x1], sl_mask)
        roi_hu = volume[slice_index, y0:y1, x0:x1][sl_mask]
        hu_min = float(roi_hu.min()) if roi_hu.size else mean_hu
        hu_max = float(roi_hu.max()) if roi_hu.size else mean_hu
        lesion_type, label_cn, hu_ok = classify_nodule_hu(mean_hu)
        if not hu_ok:
            hu_rejected += 1
            continue

        solidity = float(region.solidity) if region.solidity is not None else 0.7
        if solidity < _adaptive_solidity_min(mean_hu, spacing_z):
            solidity_rejected += 1
            continue

        # P2: 跨层连续性过滤（厚层自适应降低要求）
        if settings.continuity_enabled and z_count > 1:
            if not _has_3d_continuity(
                region.label, labeled, z0, z1, y0, y1, x0, x1,
                min_continuous=continuity_min,
            ):
                continuity_rejected += 1
                continue

        extent_z = max((z1 - z0) * spacing_z, spacing_z)
        extent_y = max((y1 - y0) * spacing_y, spacing_y)
        extent_x = max((x1 - x0) * spacing_x, spacing_x)
        long_axis = max(extent_x, extent_y, extent_z)
        short_axis = min(extent_x, extent_y, extent_z)
        diameter_mm = (long_axis + short_axis) / 2.0

        in_hilar = settings.hilar_suppress_enabled and _is_hilar_region(
            cy, cx, rows, cols, zi, z_count
        )
        if in_hilar:
            hilar_suppressed += 1

        yy, xx = np.where(sl_mask)
        min_y, max_y = y0 + yy.min(), y0 + yy.max()
        min_x, max_x = x0 + xx.min(), x0 + xx.max()

        bbox = {
            "x": float(min_x) / cols,
            "y": float(min_y) / rows,
            "width": float(max(1, max_x - min_x)) / cols,
            "height": float(max(1, max_y - min_y)) / rows,
        }
        contour = _extract_contour(sl_mask, y0, x0, rows, cols)

        area_mm2 = float(sl_mask.sum()) * spacing_y * spacing_x

        base_conf = _confidence(mean_hu, solidity, diameter_mm)
        final_conf = round(base_conf * 0.6, 3) if in_hilar else base_conf

        lesions.append({
            "id": f"A{idx + 1}",
            "label": label_cn,
            "type": lesion_type,
            "confidence": final_conf,
            "sliceIndex": int(slice_index),
            "bbox": bbox,
            "contour": contour,
            "diameterMm": round(diameter_mm, 1),
            "longAxisMm": round(long_axis, 1),
            "shortAxisMm": round(short_axis, 1),
            "areaMm2": round(area_mm2, 1),
            "volumeMm3": round(vol_mm3, 1),
            "hu": round(mean_hu, 1),
            "huMean": round(mean_hu, 1),
            "huMin": round(hu_min, 1),
            "huMax": round(hu_max, 1),
        })

    lesions.sort(key=lambda x: x["confidence"], reverse=True)
    logger.info(
        "[scheme-a] 3D: candidates=%d vol_rej=%d solid_rej=%d cont_rej=%d hilar=%d kept=%d",
        len(all_regions), volume_rejected, solidity_rejected,
        continuity_rejected, hilar_suppressed, len(lesions),
    )
    return {
        "lesions": lesions,
        "stats": {
            "candidates": len(all_regions),
            "lesionCount": len(lesions),
            "lungVoxels": int(lung_mask.sum()),
            "huThreshold": hu_min,
            "huMax": hu_max,
            "continuityMinSlices": continuity_min,
            "spacingZMm": spacing_z,
            "volumeMinMm3": settings.volume_min_mm3,
            "volumeMaxMm3": settings.volume_max_mm3,
            "solidityMin": settings.solidity_min,
            "hilarSuppressed": hilar_suppressed,
            "continuityRejected": continuity_rejected,
            "volumeRejected": volume_rejected,
            "solidityRejected": solidity_rejected,
            "borderRejected": border_rejected,
            "huRejected": hu_rejected,
        },
    }


# ---------------------------------------------------------------------------
# 当前层 2D 检测
# ---------------------------------------------------------------------------

def detect_single_slice(
    slice_hu: np.ndarray,
    spacing_y: float,
    spacing_x: float,
    slice_index: int,
    lung_mask: np.ndarray,
    spacing_z: float = 1.0,
) -> Dict[str, Any]:
    """对单层 CT 进行 2D 候选筛选。

    P2 新增：肺门区置信度惩罚。
    """
    rows, cols = slice_hu.shape
    pixel_area_mm2 = spacing_y * spacing_x

    lung_mask = refine_lung_mask(lung_mask.astype(bool), slice_hu, dilate_iters=0)
    candidate = nodule_candidate_mask(lung_mask, slice_hu, spacing_z)
    candidate = ndimage.binary_opening(candidate, iterations=1)

    labeled = label(candidate)
    regions = regionprops(labeled, intensity_image=slice_hu)
    lesions: List[Dict[str, Any]] = []

    hilar_suppressed = 0
    area_rejected = 0
    solidity_rejected = 0

    border_rejected = 0
    hu_rejected = 0

    for idx, region in enumerate(regions):
        if len(lesions) >= settings.max_lesions:
            break

        min_row, min_col, max_row, max_col = region.bbox
        cy, cx = region.centroid
        yi, xi = int(cy), int(cx)
        if yi < 0 or xi < 0 or yi >= rows or xi >= cols:
            continue
        if not lung_mask[yi, xi]:
            continue

        area_mm2 = float(region.area) * pixel_area_mm2
        if area_mm2 < settings.volume_min_mm3 / 3.0:
            area_rejected += 1
            continue

        sl_mask = labeled[min_row:max_row, min_col:max_col] == region.label
        if not sl_mask.any():
            continue
        if touches_image_border(sl_mask, margin=3):
            border_rejected += 1
            continue

        mean_hu = mean_hu_in_mask(slice_hu[min_row:max_row, min_col:max_col], sl_mask)
        roi_hu = slice_hu[min_row:max_row, min_col:max_col][sl_mask]
        hu_min = float(roi_hu.min()) if roi_hu.size else mean_hu
        hu_max = float(roi_hu.max()) if roi_hu.size else mean_hu
        lesion_type, label_cn, hu_ok = classify_nodule_hu(mean_hu)
        if not hu_ok:
            hu_rejected += 1
            continue

        solidity = float(region.solidity) if region.solidity is not None else 0.7
        if solidity < _adaptive_solidity_min(mean_hu, spacing_z):
            solidity_rejected += 1
            continue

        extent_y = max((max_row - min_row) * spacing_y, spacing_y)
        extent_x = max((max_col - min_col) * spacing_x, spacing_x)
        long_axis = max(extent_x, extent_y)
        short_axis = min(extent_x, extent_y)
        diameter_mm = (long_axis + short_axis) / 2.0

        in_hilar = settings.hilar_suppress_enabled and _is_hilar_region_2d(
            cy, cx, rows, cols
        )
        if in_hilar:
            hilar_suppressed += 1

        sl_mask = labeled[min_row:max_row, min_col:max_col] == region.label
        if not sl_mask.any():
            continue

        bbox = {
            "x": float(min_col) / cols,
            "y": float(min_row) / rows,
            "width": float(max(1, max_col - min_col)) / cols,
            "height": float(max(1, max_row - min_row)) / rows,
        }
        contour = _extract_contour(sl_mask, min_row, min_col, rows, cols)

        base_conf = _confidence(mean_hu, solidity, diameter_mm)
        final_conf = round(base_conf * 0.6, 3) if in_hilar else base_conf

        lesions.append({
            "id": f"S{idx + 1}",
            "label": label_cn,
            "type": lesion_type,
            "confidence": final_conf,
            "sliceIndex": int(slice_index),
            "bbox": bbox,
            "contour": contour,
            "diameterMm": round(diameter_mm, 1),
            "longAxisMm": round(long_axis, 1),
            "shortAxisMm": round(short_axis, 1),
            "areaMm2": round(area_mm2, 1),
            "hu": round(mean_hu, 1),
            "huMean": round(mean_hu, 1),
            "huMin": round(hu_min, 1),
            "huMax": round(hu_max, 1),
        })

    lesions.sort(key=lambda x: x["confidence"], reverse=True)
    logger.info(
        "[scheme-a] 2D slice=%d: candidates=%d area_rej=%d solid_rej=%d hilar=%d kept=%d",
        slice_index, len(regions), area_rejected, solidity_rejected,
        hilar_suppressed, len(lesions),
    )
    return {
        "lesions": lesions,
        "stats": {
            "candidates": len(regions),
            "lesionCount": len(lesions),
            "lungVoxels": int(lung_mask.sum()),
            "sliceIndex": int(slice_index),
            "detectMode": "single",
            "huThreshold": _adaptive_hu_range(spacing_z)[0],
            "spacingZMm": spacing_z,
            "borderRejected": border_rejected,
            "huRejected": hu_rejected,
        },
    }
