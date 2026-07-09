"""方案 B 病灶富化：框内 HU 分割、临床 HU 分类、标记样式、GGO 合并去重。"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from scipy import ndimage
from skimage.measure import label, regionprops

from .lesion_morphology import (
    compute_mask_morphology,
    compute_pleural_distance_mm,
    detect_cavitation_hint,
    pleural_hint,
)
from .lobe_locator import locate_lobe, lobe_hint_text
from .hu_utils import (
    classify_nodule_hu,
    extract_contour_normalized,
    ggo_candidate_mask,
    ggo_hu_window,
    nodule_candidate_mask,
)

GGO_MIN_AREA_MM2 = 80.0
GGO_MIN_Z_EXTENT = 2
GGO_MIN_Z_EXTENT_THICK = 1
GGO_CIRCULARITY_MIN = 0.35
MERGE_IOU_THRESHOLD = 0.30


def _solid_hu_window(spacing_z: float) -> Tuple[float, float]:
    if spacing_z >= 5.0:
        return 15.0, 85.0
    if spacing_z >= 3.0:
        return 12.0, 90.0
    return 15.0, 80.0


def smooth_slice_mask(sl_mask: np.ndarray) -> np.ndarray:
    if not sl_mask.any():
        return sl_mask
    m = ndimage.binary_fill_holes(sl_mask)
    m = ndimage.binary_closing(m, iterations=1)
    return m.astype(bool)


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


def refine_mask_in_bbox(
    volume: np.ndarray,
    lung_mask: np.ndarray,
    slice_index: int,
    min_y: int,
    max_y: int,
    min_x: int,
    max_x: int,
    spacing_z: float,
) -> np.ndarray:
    """在检测框内用 HU 候选 mask 提取真实病灶区域。"""
    rows, cols = volume.shape[1], volume.shape[2]
    zi = max(0, min(volume.shape[0] - 1, int(slice_index)))
    roi_hu = volume[zi, min_y:max_y, min_x:max_x]
    roi_lung = lung_mask[zi, min_y:max_y, min_x:max_x]
    cand = nodule_candidate_mask(roi_lung, roi_hu, spacing_z)
    if not cand.any():
        cand = ggo_candidate_mask(roi_lung, roi_hu, spacing_z)
    if not cand.any():
        cand = roi_lung & (roi_hu > -900) & (roi_hu < 200)
    if not cand.any():
        h, w = max_y - min_y, max_x - min_x
        fallback = np.zeros((h, w), dtype=bool)
        fallback[:] = True
        return fallback

    labeled = label(cand)
    if labeled.max() == 0:
        return cand

    cy = (max_y + min_y) / 2.0
    cx = (max_x + min_x) / 2.0
    best_label = 0
    best_dist = float("inf")
    for region in regionprops(labeled):
        ry, rx = region.centroid
        dist = (ry + min_y - cy) ** 2 + (rx + min_x - cx) ** 2
        if dist < best_dist:
            best_dist = dist
            best_label = region.label
    if best_label:
        result = labeled == best_label
    else:
        result = cand

    from .contour_refiner import refine_mask_with_watershed
    return refine_mask_with_watershed(roi_hu, result, spacing_z)


def compute_hu_stats(volume: np.ndarray, slice_index: int, sl_mask: np.ndarray,
                     y0: int, x0: int) -> Dict[str, float]:
    zi = max(0, min(volume.shape[0] - 1, int(slice_index)))
    roi = volume[zi, y0:y0 + sl_mask.shape[0], x0:x0 + sl_mask.shape[1]]
    sel = roi[sl_mask]
    if sel.size == 0:
        return {"huMean": float("nan"), "huMin": float("nan"), "huMax": float("nan"), "hu": float("nan")}
    median = float(np.median(sel))
    return {
        "huMean": round(median, 1),
        "huMin": round(float(sel.min()), 1),
        "huMax": round(float(sel.max()), 1),
        "hu": round(median, 1),
    }


def detect_mixed_subtype(
    volume: np.ndarray,
    slice_index: int,
    sl_mask: np.ndarray,
    y0: int,
    x0: int,
    spacing_z: float,
) -> str:
    """区分 pureGGO / mixedGGO / solid / calcified / other。"""
    zi = max(0, min(volume.shape[0] - 1, int(slice_index)))
    roi = volume[zi, y0:y0 + sl_mask.shape[0], x0:x0 + sl_mask.shape[1]]
    sel = roi[sl_mask]
    if sel.size == 0:
        return "other"

    ggo_lo, ggo_hi = ggo_hu_window(spacing_z)
    solid_lo, solid_hi = _solid_hu_window(spacing_z)
    n = sel.size
    ggo_frac = float(((sel >= ggo_lo) & (sel <= ggo_hi)).sum()) / n
    solid_frac = float(((sel >= solid_lo) & (sel <= solid_hi)).sum()) / n
    core_frac = float((sel > -100).sum()) / n

    if solid_frac >= 0.35 and ggo_frac >= 0.15:
        return "mixedGGO"
    if ggo_frac >= 0.5 and core_frac < 0.25:
        return "pureGGO"
    if solid_frac >= 0.4:
        return "solid"
    if float((sel >= 80).sum()) / n >= 0.3:
        return "calcified"
    if ggo_frac >= 0.35:
        return "pureGGO"
    return "other"


def classification_confidence(mean_hu: float, sub_type: str) -> float:
    if np.isnan(mean_hu):
        return 0.4
    if sub_type == "pureGGO" and -850 <= mean_hu <= -280:
        return 0.92
    if sub_type == "mixedGGO":
        return 0.78
    if sub_type == "solid" and 12 <= mean_hu <= 90:
        return 0.88
    if sub_type == "calcified" and mean_hu >= 80:
        return 0.85
    if -280 < mean_hu < 12:
        return 0.55
    return 0.5


def marker_style(lesion_type: str, sub_type: str) -> Tuple[str, str]:
    if sub_type == "mixedGGO":
        return "mixed", "contour+circle"
    if sub_type == "pureGGO" or lesion_type == "磨玻璃结节":
        return "ggo", "contour"
    if sub_type == "calcified" or lesion_type == "高密度结节":
        return "calcified", "diamond"
    if sub_type == "solid" or lesion_type == "肺结节":
        return "solid", "circle"
    return "unknown", "contour"


def bbox_iou(a: Dict[str, float], b: Dict[str, float]) -> float:
    ax1, ay1 = a.get("x", 0), a.get("y", 0)
    ax2, ay2 = ax1 + a.get("width", 0), ay1 + a.get("height", 0)
    bx1, by1 = b.get("x", 0), b.get("y", 0)
    bx2, by2 = bx1 + b.get("width", 0), by1 + b.get("height", 0)
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    if ix2 <= ix1 or iy2 <= iy1:
        return 0.0
    inter = (ix2 - ix1) * (iy2 - iy1)
    area_a = max(a.get("width", 0) * a.get("height", 0), 1e-9)
    area_b = max(b.get("width", 0) * b.get("height", 0), 1e-9)
    return inter / (area_a + area_b - inter)


def enrich_lesion(
    lesion: Dict[str, Any],
    volume: np.ndarray,
    lung_mask: np.ndarray,
    spacing: Tuple[float, float, float],
    rows: int,
    cols: int,
    source: str = "dl_high",
    lobe_masks: Optional[Dict[str, np.ndarray]] = None,
) -> Optional[Dict[str, Any]]:
    """框内分割 + 临床 HU 分类 + 标记字段。"""
    spacing_z, spacing_y, spacing_x = spacing
    bbox = lesion.get("bbox") or {}
    slice_index = int(lesion.get("sliceIndex", 0))
    min_y, max_y, min_x, max_x = _bbox_pixels(bbox, rows, cols)

    sl_mask = refine_mask_in_bbox(
        volume, lung_mask, slice_index, min_y, max_y, min_x, max_x, spacing_z
    )
    sl_mask = smooth_slice_mask(sl_mask)

    yy, xx = np.where(sl_mask)
    if yy.size == 0:
        return None

    abs_min_y = min_y + int(yy.min())
    abs_max_y = min_y + int(yy.max()) + 1
    abs_min_x = min_x + int(xx.min())
    abs_max_x = min_x + int(xx.max()) + 1

    crop = sl_mask[yy.min():yy.max() + 1, xx.min():xx.max() + 1]
    contour = []
    try:
        contour = extract_contour_normalized(crop, abs_min_y, abs_min_x, rows, cols)
    except Exception:
        contour = []

    hu_stats = compute_hu_stats(volume, slice_index, crop, abs_min_y, abs_min_x)
    mean_hu = hu_stats["huMean"]
    lesion_type, label_cn, hu_ok = classify_nodule_hu(mean_hu)
    if not hu_ok:
        return None

    sub_type = detect_mixed_subtype(volume, slice_index, crop, abs_min_y, abs_min_x, spacing_z)
    if lesion_type == "磨玻璃结节" and sub_type == "other":
        sub_type = "pureGGO"
    elif lesion_type == "肺结节" and sub_type == "other":
        sub_type = "solid"
    elif lesion_type == "高密度结节" and sub_type == "other":
        sub_type = "calcified"

    color_key, marker_type = marker_style(lesion_type, sub_type)
    det_conf = float(lesion.get("detectionConfidence") or lesion.get("confidence") or 0.5)
    cls_conf = classification_confidence(mean_hu, sub_type)

    long_mm = max((abs_max_x - abs_min_x) * spacing_x, spacing_x)
    short_mm = max((abs_max_y - abs_min_y) * spacing_y, spacing_y)
    if lesion.get("longAxisMm"):
        long_mm = max(long_mm, float(lesion["longAxisMm"]))
    if lesion.get("shortAxisMm"):
        short_mm = min(short_mm, float(lesion["shortAxisMm"])) if short_mm else float(lesion["shortAxisMm"])

    area_mm2 = float(crop.sum()) * spacing_y * spacing_x
    diameter_mm = (long_mm + short_mm) / 2.0

    cy = (abs_min_y + abs_max_y) / 2.0
    cx = (abs_min_x + abs_max_x) / 2.0
    lobe_label = locate_lobe(lobe_masks or {}, slice_index, cy, cx, rows, cols)
    morphology = compute_mask_morphology(crop)
    cavitation_hint = None
    if sub_type in ("solid", "mixedGGO"):
        cavitation_hint = detect_cavitation_hint(
            volume, slice_index, crop, abs_min_y, abs_min_x, mean_hu,
        )
    if cavitation_hint:
        morphology = {**morphology, "cavitationHint": cavitation_hint}
    position_hint = lobe_hint_text(lobe_label)

    pleural_mm = None
    pleural_hint_text = None
    if slice_index < lung_mask.shape[0]:
        full_sl = np.zeros((rows, cols), dtype=bool)
        full_sl[abs_min_y:abs_max_y, abs_min_x:abs_max_x] = crop
        pleural_mm = compute_pleural_distance_mm(
            full_sl, lung_mask[slice_index], spacing_y, spacing_x,
        )
        pleural_hint_text = pleural_hint(pleural_mm)

    from .lesion_classifier import classify_lesion_multiclass
    det_class, det_class_label, class_conf = classify_lesion_multiclass(
        lesion_type,
        sub_type,
        mean_hu,
        morphology,
        dl_model_class=lesion.get("dlModelClass"),
    )
    cls_conf = max(cls_conf, class_conf)

    out = dict(lesion)
    out.update({
        "label": label_cn if hu_ok else (lesion.get("label") or label_cn),
        "type": lesion_type,
        "bbox": {
            "x": float(abs_min_x) / cols,
            "y": float(abs_min_y) / rows,
            "width": float(max(1, abs_max_x - abs_min_x)) / cols,
            "height": float(max(1, abs_max_y - abs_min_y)) / rows,
        },
        "contour": contour if len(contour) >= 3 else lesion.get("contour"),
        "diameterMm": round(diameter_mm, 1),
        "longAxisMm": round(long_mm, 1),
        "shortAxisMm": round(short_mm, 1),
        "areaMm2": round(area_mm2, 1),
        "volumeMm3": round(area_mm2 * spacing_z, 1),
        "huMean": hu_stats["huMean"],
        "huMin": hu_stats["huMin"],
        "huMax": hu_stats["huMax"],
        "hu": hu_stats["hu"],
        "subType": sub_type,
        "colorKey": color_key,
        "markerType": marker_type,
        "detectionConfidence": round(min(max(det_conf, 0.05), 0.99), 3),
        "classificationConfidence": round(cls_conf, 3),
        "confidence": round(min(max(det_conf, 0.05), 0.99), 3),
        "source": source,
        "lobeLabel": lobe_label,
        "positionHint": position_hint,
        "morphology": morphology,
        "lobulationHint": morphology.get("lobulationHint"),
        "spiculationHint": morphology.get("spiculationHint"),
        "cavitationHint": morphology.get("cavitationHint"),
        "detectionClass": det_class,
        "detectionClassLabel": det_class_label,
        "pleuralDistanceMm": pleural_mm,
        "pleuralHint": pleural_hint_text,
    })
    return out


def merge_lesion_lists(
    primary: List[Dict[str, Any]],
    supplemental: List[Dict[str, Any]],
    iou_threshold: float = MERGE_IOU_THRESHOLD,
) -> Tuple[List[Dict[str, Any]], int]:
    """合并列表，supplemental 与 primary 同层 IoU 超阈值则跳过。"""
    merged = list(primary)
    skipped = 0
    for cand in supplemental:
        cb = cand.get("bbox") or {}
        cs = cand.get("sliceIndex")
        duplicate = False
        for kept in merged:
            if kept.get("sliceIndex") != cs:
                continue
            if bbox_iou(cb, kept.get("bbox") or {}) >= iou_threshold:
                duplicate = True
                break
        if duplicate:
            skipped += 1
            continue
        merged.append(cand)
    return merged, skipped


def ggo_region_to_lesion(
    region: Dict[str, Any],
    idx: int,
    volume: np.ndarray,
    lung_mask: np.ndarray,
    spacing: Tuple[float, float, float],
    rows: int,
    cols: int,
    lobe_masks: Optional[Dict[str, np.ndarray]] = None,
) -> Optional[Dict[str, Any]]:
    """将 GGO 启发式区域转为标准 lesion。"""
    points = region.get("points") or region.get("contour") or []
    if len(points) < 3:
        return None

    xs = [p["x"] if isinstance(p, dict) else p[0] for p in points]
    ys = [p["y"] if isinstance(p, dict) else p[1] for p in points]
    min_x = int(max(0, round(min(xs) * cols)))
    max_x = int(min(cols, round(max(xs) * cols)))
    min_y = int(max(0, round(min(ys) * rows)))
    max_y = int(min(rows, round(max(ys) * rows)))
    if max_x <= min_x or max_y <= min_y:
        return None

    slice_index = int(region.get("sliceIndex", 0))
    bbox = {
        "x": float(min_x) / cols,
        "y": float(min_y) / rows,
        "width": float(max(1, max_x - min_x)) / cols,
        "height": float(max(1, max_y - min_y)) / rows,
    }
    base = {
        "id": region.get("id") or f"G{idx + 1}",
        "label": "疑似磨玻璃结节",
        "type": "磨玻璃结节",
        "confidence": 0.45,
        "detectionConfidence": 0.45,
        "sliceIndex": slice_index,
        "bbox": bbox,
        "contour": points,
        "diameterMm": region.get("diameterMm", 0),
        "longAxisMm": region.get("longAxisMm", 0),
        "shortAxisMm": region.get("shortAxisMm", 0),
        "areaMm2": region.get("areaMm2", 0),
        "volumeMm3": region.get("volumeMm3"),
        "source": "ggo_heuristic",
    }
    return enrich_lesion(
        base, volume, lung_mask, spacing, rows, cols,
        source="ggo_heuristic", lobe_masks=lobe_masks,
    )
