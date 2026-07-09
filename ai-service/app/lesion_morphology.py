"""病灶形态学特征（轮廓圆度/分叶倾向，方案 B P2）。"""
from __future__ import annotations

from typing import Any, Dict, Optional

import numpy as np
from scipy import ndimage
from skimage.measure import label, regionprops


def compute_pleural_distance_mm(
    sl_mask: np.ndarray,
    lung_mask_sl: np.ndarray,
    spacing_y: float,
    spacing_x: float,
) -> Optional[float]:
    """病灶 mask 到肺野边界的最近距离（mm），用于胸膜下结节提示。"""
    if sl_mask is None or lung_mask_sl is None:
        return None
    if not np.any(sl_mask) or not np.any(lung_mask_sl):
        return None

    structure = np.ones((3, 3), dtype=bool)
    lung_inner = ndimage.binary_erosion(lung_mask_sl.astype(bool), structure=structure, iterations=2)
    boundary = lung_mask_sl.astype(bool) & ~lung_inner
    if not boundary.any():
        boundary = lung_mask_sl.astype(bool)

    dist = ndimage.distance_transform_edt(~boundary)
    vals = dist[sl_mask.astype(bool)]
    if vals.size == 0:
        return None
    spacing_mm = (spacing_y + spacing_x) / 2.0
    return round(float(vals.min()) * spacing_mm, 1)


def pleural_hint(distance_mm: Optional[float]) -> Optional[str]:
    if distance_mm is None:
        return None
    if distance_mm <= 3.0:
        return "胸膜下/贴胸膜"
    if distance_mm <= 8.0:
        return "近胸膜"
    return None


def compute_mask_morphology(sl_mask: np.ndarray) -> Dict[str, Any]:
    """从 2D mask 估算形态指标。"""
    if sl_mask is None or not np.any(sl_mask):
        return {}

    labeled = label(sl_mask.astype(bool))
    if labeled.max() == 0:
        return {}

    region = max(regionprops(labeled), key=lambda r: r.area)
    area = float(region.area)
    perimeter = float(region.perimeter) if region.perimeter else 0.0
    if area <= 0 or perimeter <= 0:
        return {}

    circularity = float(4.0 * np.pi * area / (perimeter ** 2))
    circularity = max(0.0, min(1.0, circularity))

    solidity = float(region.solidity) if region.solidity is not None else 1.0
    lobulation_index = round(max(0.0, 1.0 - solidity), 3)

    # 周长²/面积 越大，边界越不规则（毛刺倾向）
    irregularity = float((perimeter ** 2) / (4.0 * np.pi * area)) if area > 0 else 1.0

    spiculation_hint = "未见明显"
    if irregularity >= 1.8 and circularity < 0.65:
        spiculation_hint = "边界欠规则"
    if irregularity >= 2.2 and lobulation_index >= 0.15:
        spiculation_hint = "分叶/毛刺倾向"

    lobulation_hint = "光滑" if lobulation_index < 0.08 else (
        "轻度分叶" if lobulation_index < 0.18 else "分叶倾向"
    )

    return {
        "circularity": round(circularity, 3),
        "solidity": round(solidity, 3),
        "lobulationIndex": lobulation_index,
        "lobulationHint": lobulation_hint,
        "spiculationHint": spiculation_hint,
        "irregularity": round(irregularity, 3),
    }


def detect_cavitation_hint(
    volume: np.ndarray,
    slice_index: int,
    crop: np.ndarray,
    abs_min_y: int,
    abs_min_x: int,
    mean_hu: float,
) -> Optional[str]:
    """框内低密度小腔（空泡征倾向），适用于偏实性结节。"""
    if mean_hu < -150:
        return None
    if slice_index < 0 or slice_index >= volume.shape[0]:
        return None
    if crop is None or not np.any(crop):
        return None

    h, w = crop.shape
    roi = volume[slice_index, abs_min_y:abs_min_y + h, abs_min_x:abs_min_x + w]
    if roi.shape != crop.shape:
        return None

    lesion_vals = roi[crop]
    if lesion_vals.size < 12:
        return None

    # 腔隙：明显低于结节主体、但仍高于纯空气
    pocket_thresh = min(float(np.percentile(lesion_vals, 25)) - 80, -350)
    pockets = crop & (roi < pocket_thresh) & (roi > -900)
    if not pockets.any():
        return None

    labeled = label(pockets)
    lesion_area = float(crop.sum())
    for region in regionprops(labeled):
        if region.area < 4:
            continue
        if region.area / max(lesion_area, 1.0) < 0.04:
            continue
        # 需被较高密度包绕（非开放到肺野）
        cy, cx = region.centroid
        cy_i, cx_i = int(round(cy)), int(round(cx))
        ring_y0 = max(0, cy_i - 2)
        ring_y1 = min(h, cy_i + 3)
        ring_x0 = max(0, cx_i - 2)
        ring_x1 = min(w, cx_i + 3)
        ring = crop[ring_y0:ring_y1, ring_x0:ring_x1].copy()
        ring[cy_i - ring_y0:cy_i - ring_y0 + 1, cx_i - ring_x0:cx_i - ring_x0 + 1] = False
        if not ring.any():
            continue
        ring_hu = roi[ring_y0:ring_y1, ring_x0:ring_x1][ring]
        if ring_hu.size and float(ring_hu.mean()) > pocket_thresh + 40:
            return "可见空泡征倾向"
    return None
