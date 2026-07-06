"""单层 DICOM 2D 病灶候选检测（启发式）。"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

import numpy as np
from scipy import ndimage
from skimage.measure import label, regionprops

from .chest_detector import _confidence, _extract_contour, _lesion_type
from .config import settings


def _segment_lungs_2d(slice_hu: np.ndarray) -> np.ndarray:
    body = slice_hu > -900
    lung_like = (slice_hu < -400) & (slice_hu > -950)
    mask = lung_like & body

    structure = np.ones((3, 3), dtype=bool)
    mask = ndimage.binary_opening(mask, structure=structure, iterations=1)
    mask = ndimage.binary_closing(mask, structure=structure, iterations=2)

    labeled = label(mask)
    if labeled.max() == 0:
        return mask

    counts = np.bincount(labeled.ravel())
    counts[0] = 0
    keep_ids = np.argsort(counts)[-2:]
    lung = np.isin(labeled, keep_ids)
    return ndimage.binary_dilation(lung, iterations=1)


def detect_slice_lesions(
    slice_hu: np.ndarray,
    spacing_y: float,
    spacing_x: float,
    slice_index: int,
) -> Dict[str, Any]:
    rows, cols = slice_hu.shape
    pixel_area_mm2 = spacing_y * spacing_x

    lung_mask = _segment_lungs_2d(slice_hu)
    lung_region = lung_mask
    candidate = lung_mask & (slice_hu > -200) & (slice_hu < 100)
    candidate = ndimage.binary_opening(candidate, iterations=1)

    labeled = label(candidate)
    regions = regionprops(labeled, intensity_image=slice_hu)
    lesions: List[Dict[str, Any]] = []

    for idx, region in enumerate(regions):
        if len(lesions) >= settings.max_lesions:
            break

        min_row, min_col, max_row, max_col = region.bbox
        cy, cx = region.centroid
        if not lung_mask[int(cy), int(cx)]:
            continue

        extent_y = max((max_row - min_row) * spacing_y, spacing_y)
        extent_x = max((max_col - min_col) * spacing_x, spacing_x)
        long_axis = max(extent_x, extent_y)
        short_axis = min(extent_x, extent_y)
        diameter_mm = (long_axis + short_axis) / 2.0

        if diameter_mm < settings.min_nodule_mm or diameter_mm > settings.max_nodule_mm:
            continue

        sl_mask = labeled[min_row:max_row, min_col:max_col] == region.label
        if not sl_mask.any():
            continue

        mean_hu = float(region.mean_intensity)
        lesion_type, label_cn = _lesion_type(mean_hu)
        solidity = float(region.solidity) if region.solidity is not None else 0.7

        bbox = {
            "x": float(min_col) / cols,
            "y": float(min_row) / rows,
            "width": float(max(1, max_col - min_col)) / cols,
            "height": float(max(1, max_row - min_row)) / rows,
        }
        contour = _extract_contour(sl_mask, min_row, min_col, rows, cols)
        area_mm2 = float(region.area) * pixel_area_mm2

        lesions.append(
            {
                "id": f"S{idx + 1}",
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
                "volumeMm3": round(area_mm2 * max(settings.min_nodule_mm, 1.0), 1),
                "hu": round(mean_hu, 1),
            }
        )

    lesions.sort(key=lambda x: x["confidence"], reverse=True)
    return {
        "lesions": lesions,
        "stats": {
            "candidates": len(regions),
            "lesionCount": len(lesions),
            "lungVoxels": int(lung_mask.sum()),
            "volumeShape": [1, rows, cols],
            "sliceIndex": int(slice_index),
            "detectMode": "single",
        },
    }
