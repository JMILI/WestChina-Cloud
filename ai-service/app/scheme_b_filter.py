"""方案 B P1：融合过滤（肺野/血管/形态/HU 均匀度/肺门降权）。"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from skimage.measure import label, regionprops

from .config import settings
from .hu_utils import classify_nodule_hu, ggo_hu_window


def _bbox_pixels(bbox: Dict[str, float], rows: int, cols: int) -> Tuple[int, int, int, int]:
    min_x = int(max(0, round(bbox.get("x", 0) * cols)))
    min_y = int(max(0, round(bbox.get("y", 0) * rows)))
    max_x = int(min(cols, round((bbox.get("x", 0) + bbox.get("width", 0)) * cols)))
    max_y = int(min(rows, round((bbox.get("y", 0) + bbox.get("height", 0)) * rows)))
    if max_x <= min_x:
        max_x = min(cols, min_x + 1)
    if max_y <= min_y:
        max_y = min(rows, min_y + 1)
    return min_y, max_y, min_x, max_x


def is_hilar_region(cy: float, cx: float, rows: int, cols: int, zi: int, z_count: int) -> bool:
    """肺门高危区：中央 + 序列中段。"""
    y_center = abs(cy / max(rows, 1) - 0.5)
    x_center = abs(cx / max(cols, 1) - 0.5)
    z_mid = abs(zi / max(z_count, 1) - 0.5)
    return y_center < 0.25 and x_center < 0.25 and z_mid < 0.35


def lesion_center_in_lung(
    lesion: Dict[str, Any],
    lung_mask: np.ndarray,
    rows: int,
    cols: int,
) -> bool:
    bbox = lesion.get("bbox") or {}
    si = int(lesion.get("sliceIndex", 0))
    if si < 0 or si >= lung_mask.shape[0]:
        return False
    min_y, max_y, min_x, max_x = _bbox_pixels(bbox, rows, cols)
    box_mask = np.zeros((rows, cols), dtype=bool)
    box_mask[min_y:max_y, min_x:max_x] = True
    lung_sl = lung_mask[si]
    overlap = int((box_mask & lung_sl).sum())
    box_area = int(box_mask.sum())
    if box_area <= 0:
        return False
    if overlap / box_area >= 0.30:
        return True
    cx = int(round((bbox.get("x", 0) + bbox.get("width", 0) / 2) * cols))
    cy = int(round((bbox.get("y", 0) + bbox.get("height", 0) / 2) * rows))
    cx = max(0, min(cols - 1, cx))
    cy = max(0, min(rows - 1, cy))
    return bool(lung_sl[cy, cx])


def lesion_vessel_iou(
    lesion: Dict[str, Any],
    vessel_mask: np.ndarray | None,
    rows: int,
    cols: int,
) -> float:
    if vessel_mask is None or not vessel_mask.any():
        return 0.0
    bbox = lesion.get("bbox") or {}
    si = int(lesion.get("sliceIndex", 0))
    if si < 0 or si >= vessel_mask.shape[0]:
        return 0.0
    min_y, max_y, min_x, max_x = _bbox_pixels(bbox, rows, cols)
    box_mask = np.zeros((rows, cols), dtype=bool)
    box_mask[min_y:max_y, min_x:max_x] = True
    vessel_sl = vessel_mask[si]
    inter = int((box_mask & vessel_sl).sum())
    union = int((box_mask | vessel_sl).sum())
    return inter / union if union > 0 else 0.0


def _roi_shape_metrics(
    volume: np.ndarray,
    lesion: Dict[str, Any],
    spacing: Tuple[float, float, float],
    rows: int,
    cols: int,
) -> Dict[str, float]:
    spacing_z, spacing_y, spacing_x = spacing
    bbox = lesion.get("bbox") or {}
    si = int(lesion.get("sliceIndex", 0))
    min_y, max_y, min_x, max_x = _bbox_pixels(bbox, rows, cols)
    if si < 0 or si >= volume.shape[0]:
        return {"solidity": 0.0, "sphericity": 0.0, "huStddev": 999.0, "meanHu": float("nan")}

    roi = volume[si, min_y:max_y, min_x:max_x]
    sl_mask = np.ones(roi.shape, dtype=bool)
    if roi.size == 0:
        return {"solidity": 0.0, "sphericity": 0.0, "huStddev": 999.0, "meanHu": float("nan")}

    mean_hu = float(np.median(roi))
    hu_std = float(np.std(roi))

    labeled = label(sl_mask)
    region = regionprops(labeled)[0]
    solidity = float(region.solidity) if region.solidity is not None else 0.85

    w_mm = max((max_x - min_x) * spacing_x, spacing_x)
    h_mm = max((max_y - min_y) * spacing_y, spacing_y)
    d_mm = spacing_z
    dims = sorted([w_mm, h_mm, d_mm], reverse=True)
    if dims[0] <= 0:
        sphericity = 0.0
    else:
        sphericity = float(dims[2] / dims[0])

    return {
        "solidity": solidity,
        "sphericity": sphericity,
        "huStddev": hu_std,
        "meanHu": mean_hu,
    }


def _is_ggo_like(mean_hu: float, spacing_z: float) -> bool:
    ggo_lo, ggo_hi = ggo_hu_window(spacing_z)
    return ggo_lo <= mean_hu <= ggo_hi


def filter_lesions_p1(
    lesions: List[Dict[str, Any]],
    volume: np.ndarray,
    lung_mask: np.ndarray,
    vessel_mask: np.ndarray | None,
    spacing: Tuple[float, float, float],
    rows: int,
    cols: int,
    *,
    vessel_iou_max: Optional[float] = None,
    allow_low_conf_ggo: bool = False,
) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    """P1 融合过滤：解剖 + 形态 + HU 均匀度 + 肺门降权。"""
    vessel_iou_max = vessel_iou_max if vessel_iou_max is not None else settings.scheme_b_vessel_iou_max
    spacing_z = spacing[0]
    z_count = volume.shape[0]

    stats = {
        "lung_rejected": 0,
        "vessel_rejected": 0,
        "solidity_rejected": 0,
        "sphericity_rejected": 0,
        "hu_stddev_rejected": 0,
        "hilar_downweighted": 0,
        "hu_range_rejected": 0,
        "air_rejected": 0,
    }
    kept: List[Dict[str, Any]] = []

    for lesion in lesions:
        if not lesion_center_in_lung(lesion, lung_mask, rows, cols):
            stats["lung_rejected"] += 1
            continue

        vessel_iou = lesion_vessel_iou(lesion, vessel_mask, rows, cols)
        if vessel_iou > vessel_iou_max:
            stats["vessel_rejected"] += 1
            continue

        metrics = _roi_shape_metrics(volume, lesion, spacing, rows, cols)
        mean_hu = metrics["meanHu"]
        if not (-920 < mean_hu < 350):
            stats["hu_range_rejected"] += 1
            continue
        _, _, hu_ok = classify_nodule_hu(mean_hu)
        if not hu_ok:
            stats["hu_range_rejected"] += 1
            continue
        si = int(lesion.get("sliceIndex", 0))
        min_y, max_y, min_x, max_x = _bbox_pixels(lesion.get("bbox") or {}, rows, cols)
        if 0 <= si < volume.shape[0]:
            roi = volume[si, min_y:max_y, min_x:max_x]
            if roi.size > 0 and float((roi < -900).sum()) / roi.size > 0.45:
                stats["air_rejected"] += 1
                continue
        is_ggo = _is_ggo_like(mean_hu, spacing_z)
        solidity_min = (
            settings.scheme_b_ggo_solidity_min if is_ggo else settings.scheme_b_solidity_min
        )
        stddev_max = (
            settings.scheme_b_ggo_hu_stddev_max if is_ggo else settings.scheme_b_hu_stddev_max
        )

        if not allow_low_conf_ggo:
            if metrics["solidity"] < solidity_min:
                stats["solidity_rejected"] += 1
                continue
            if metrics["sphericity"] < settings.scheme_b_sphericity_min:
                stats["sphericity_rejected"] += 1
                continue
            if metrics["huStddev"] > stddev_max:
                stats["hu_stddev_rejected"] += 1
                continue

        item = dict(lesion)
        bbox = item.get("bbox") or {}
        cx = (bbox.get("x", 0) + bbox.get("width", 0) / 2) * cols
        cy = (bbox.get("y", 0) + bbox.get("height", 0) / 2) * rows

        if settings.scheme_b_hilar_downweight_enabled and is_hilar_region(cy, cx, rows, cols, si, z_count):
            conf = float(item.get("detectionConfidence") or item.get("confidence") or 0.5)
            conf *= settings.scheme_b_hilar_conf_factor
            item["detectionConfidence"] = round(conf, 3)
            item["confidence"] = round(conf, 3)
            stats["hilar_downweighted"] += 1

        kept.append(item)

    return kept, stats


def is_low_conf_ggo_candidate(
    lesion: Dict[str, Any],
    volume: np.ndarray,
    spacing: Tuple[float, float, float],
    rows: int,
    cols: int,
) -> bool:
    """低置信候选是否落在 GGO HU 窗内。"""
    metrics = _roi_shape_metrics(volume, lesion, spacing, rows, cols)
    if not _is_ggo_like(metrics["meanHu"], spacing[0]):
        return False
    _, _, hu_ok = classify_nodule_hu(metrics["meanHu"])
    return hu_ok
