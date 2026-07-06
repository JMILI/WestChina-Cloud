"""方案 B：融合精准分析。

TotalSegmentator 肺叶+血管 + nnDetection / MONAI RetinaNet + HU 启发式 GGO。
子引擎：detectSubEngine ∈ {auto, monai, nndet}。
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Tuple

import numpy as np
from scipy import ndimage
from skimage.measure import find_contours, label, regionprops

from .monai_bundle_manager import is_monai_available, is_monai_bundle_ready
from .nndet_wrapper import is_nndet_available, is_nndet_weights_ready

GGO_HU_MIN = -750.0
GGO_HU_MAX = -300.0
GGO_MIN_AREA_MM2 = 80.0
VESSEL_IOU_MAX = 0.10
MAX_GGO_REGIONS = 30


def is_gpu_available() -> bool:
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


# is_nndet_available() / is_nndet_weights_ready() 已迁移至 nndet_wrapper.py


def is_candidate_detector_available() -> bool:
    return is_nndet_available() or (is_monai_available() and is_monai_bundle_ready())


def detect_fusion(
    volume: np.ndarray,
    spacing: Tuple[float, float, float],
    rows: int,
    cols: int,
    sub_engine: str = "auto",
) -> Dict[str, Any]:
    """全序列融合检测。

    Args:
        volume: (Z, H, W) HU float32
        spacing: (z, y, x) mm
        rows, cols: 图像尺寸
        sub_engine: "auto"(自动优先级) / "monai"(强制MONAI) / "nndet"(强制nnDetection)

    Returns:
        {"lesions": [...], "ggoRegions": [...], "stats": {...}}
    """
    if not is_gpu_available():
        return {
            "lesions": [],
            "ggoRegions": [],
            "stats": {
                "reason": "GPU_UNAVAILABLE",
                "message": "方案 B 需要 GPU，当前环境 torch.cuda.is_available() = False",
            },
        }

    if not is_candidate_detector_available():
        return {
            "lesions": [],
            "ggoRegions": [],
            "stats": {
                "reason": "DETECTOR_UNAVAILABLE",
                "message": (
                    "候选检测器不可用。请安装 nnDetection 或 MONAI bundle："
                    " pip install -r requirements-monai.txt"
                ),
            },
        }

    from .totalsegmentator_lung import get_lung_vessel_mask_3d

    lung_mask, vessel_mask = get_lung_vessel_mask_3d(volume, spacing)

    raw_lesions, candidate_source, nndet_candidates = _run_candidate_detector(
        volume, spacing, rows, cols, sub_engine=sub_engine
    )

    lesions, filter_stats = _filter_lesions(raw_lesions, lung_mask, vessel_mask, rows, cols)
    ggo_regions = _detect_ggo_regions(volume, lung_mask, spacing, rows, cols)

    return {
        "lesions": lesions,
        "ggoRegions": ggo_regions,
        "stats": {
            "lung_voxels": int(lung_mask.sum()),
            "vessel_voxels": int(vessel_mask.sum()) if vessel_mask is not None else 0,
            "nndet_candidates": nndet_candidates,
            "raw_lesion_count": len(raw_lesions),
            "fusion_filtered": len(lesions),
            "fusion_rejected": max(0, len(raw_lesions) - len(lesions)),
            "filter_lung_rejected": filter_stats.get("lung_rejected", 0),
            "filter_vessel_rejected": filter_stats.get("vessel_rejected", 0),
            "ggo_regions": len(ggo_regions),
            "candidate_source": candidate_source,
            "sub_engine": sub_engine,
        },
    }


def _run_candidate_detector(
    volume: np.ndarray,
    spacing: Tuple[float, float, float],
    rows: int,
    cols: int,
    sub_engine: str = "auto",
) -> Tuple[List[Dict[str, Any]], str, int]:
    """返回 (lesions, source_label, raw_candidate_count)。

    sub_engine：
      "auto"  → nnDetection(权重就绪) → MONAI(回退)
      "monai" → 强制 MONAI
      "nndet" → 强制 nnDetection（权重未就绪时报错回退）
    """
    # ── 强制 nnDetection ──
    if sub_engine == "nndet":
        if not is_nndet_available() or not is_nndet_weights_ready():
            raise RuntimeError(
                "nnDetection 权重未就绪。请设置 NNDET_LUNA16_WEIGHT_DIR 指向包含 "
                "plan_inference.pkl + config.yaml + *.ckpt 的训练目录。"
            )
        from .nndet_wrapper import detect_lesions_nndet
        result = detect_lesions_nndet(volume, spacing, rows, cols)
        lesions = result.get("lesions", [])
        count = int(result.get("stats", {}).get("candidates", len(lesions)))
        return lesions, "nndetection", count

    # ── 强制 MONAI ──
    if sub_engine == "monai":
        if not (is_monai_available() and is_monai_bundle_ready()):
            raise RuntimeError("MONAI RetinaNet bundle 未就绪。请执行 pip install -r requirements-monai.txt")
        from .monai_nnunet_detector import detect_lesions_monai_nnunet
        result = detect_lesions_monai_nnunet(volume, spacing, rows, cols)
        lesions = result.get("lesions", [])
        count = int(result.get("stats", {}).get("candidates", len(lesions)))
        import logging
        logging.getLogger(__name__).info("[scheme-b] 子引擎: monai")
        return lesions, "monai-retinanet", count

    # ── 自动优先级：nnDetection → MONAI → 空 ──
    if is_nndet_available() and is_nndet_weights_ready():
        from .nndet_wrapper import detect_lesions_nndet
        result = detect_lesions_nndet(volume, spacing, rows, cols)
        lesions = result.get("lesions", [])
        count = int(result.get("stats", {}).get("candidates", len(lesions)))
        return lesions, "nndetection", count

    if is_monai_available() and is_monai_bundle_ready():
        from .monai_nnunet_detector import detect_lesions_monai_nnunet
        result = detect_lesions_monai_nnunet(volume, spacing, rows, cols)
        lesions = result.get("lesions", [])
        count = int(result.get("stats", {}).get("candidates", len(lesions)))
        import logging
        logging.getLogger(__name__).info("[scheme-b] 子引擎: monai (auto)")
        return lesions, "monai-retinanet", count

    return [], "none", 0


def _lesion_center_in_lung(
    lesion: Dict[str, Any],
    lung_mask: np.ndarray,
    rows: int,
    cols: int,
) -> bool:
    """bbox 与肺野 mask 重叠比例 >= 30% 即视为在肺内（中心点法对厚层/偏移框过严）。"""
    bbox = lesion.get("bbox") or {}
    si = int(lesion.get("sliceIndex", 0))
    if si < 0 or si >= lung_mask.shape[0]:
        return False
    min_x = int(max(0, round(bbox.get("x", 0) * cols)))
    min_y = int(max(0, round(bbox.get("y", 0) * rows)))
    max_x = int(min(cols, round((bbox.get("x", 0) + bbox.get("width", 0)) * cols)))
    max_y = int(min(rows, round((bbox.get("y", 0) + bbox.get("height", 0)) * rows)))
    if max_x <= min_x or max_y <= min_y:
        return False
    box_mask = np.zeros((rows, cols), dtype=bool)
    box_mask[min_y:max_y, min_x:max_x] = True
    lung_sl = lung_mask[si]
    overlap = int((box_mask & lung_sl).sum())
    box_area = int(box_mask.sum())
    if box_area <= 0:
        return False
    if overlap / box_area >= 0.30:
        return True
    # 回退：中心点在肺内
    cx = int(round((bbox.get("x", 0) + bbox.get("width", 0) / 2) * cols))
    cy = int(round((bbox.get("y", 0) + bbox.get("height", 0) / 2) * rows))
    cx = max(0, min(cols - 1, cx))
    cy = max(0, min(rows - 1, cy))
    return bool(lung_sl[cy, cx])


def _lesion_vessel_iou(
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
    min_x = int(max(0, round(bbox.get("x", 0) * cols)))
    min_y = int(max(0, round(bbox.get("y", 0) * rows)))
    max_x = int(min(cols, round((bbox.get("x", 0) + bbox.get("width", 0)) * cols)))
    max_y = int(min(rows, round((bbox.get("y", 0) + bbox.get("height", 0)) * rows)))
    if max_x <= min_x or max_y <= min_y:
        return 0.0
    box_mask = np.zeros((rows, cols), dtype=bool)
    box_mask[min_y:max_y, min_x:max_x] = True
    vessel_sl = vessel_mask[si]
    inter = int((box_mask & vessel_sl).sum())
    union = int((box_mask | vessel_sl).sum())
    return inter / union if union > 0 else 0.0


def _filter_lesions(
    lesions: List[Dict[str, Any]],
    lung_mask: np.ndarray,
    vessel_mask: np.ndarray | None,
    rows: int,
    cols: int,
) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    """过滤候选：肺内重叠 + 与血管 IoU 低于阈值。"""
    kept: List[Dict[str, Any]] = []
    lung_rejected = 0
    vessel_rejected = 0
    for lesion in lesions:
        if not _lesion_center_in_lung(lesion, lung_mask, rows, cols):
            lung_rejected += 1
            continue
        if _lesion_vessel_iou(lesion, vessel_mask, rows, cols) > VESSEL_IOU_MAX:
            vessel_rejected += 1
            continue
        kept.append(lesion)
    return kept, {"lung_rejected": lung_rejected, "vessel_rejected": vessel_rejected}


def _extract_contour(
    sl_mask: np.ndarray,
    y_offset: int,
    x_offset: int,
    rows: int,
    cols: int,
    max_points: int = 48,
) -> List[Dict[str, float]]:
    if not sl_mask.any():
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
        points.append({
            "x": round(min(max(gx / cols, 0.0), 1.0), 5),
            "y": round(min(max(gy / rows, 0.0), 1.0), 5),
        })
    if len(points) >= 3:
        points.append(points[0])
    return points


def _detect_ggo_regions(
    volume: np.ndarray,
    lung_mask: np.ndarray,
    spacing: Tuple[float, float, float],
    rows: int,
    cols: int,
) -> List[Dict[str, Any]]:
    """HU 启发式 GGO 区域（COVID-Seg 未集成时的辅助展示）。"""
    spacing_z, spacing_y, spacing_x = spacing
    pixel_area_mm2 = spacing_y * spacing_x

    ggo_vol = lung_mask & (volume > GGO_HU_MIN) & (volume < GGO_HU_MAX) & (volume > -950) & (volume < -250)
    ggo_vol = ndimage.binary_opening(ggo_vol, iterations=1)

    regions: List[Dict[str, Any]] = []
    for z in range(volume.shape[0]):
        sl = ggo_vol[z]
        if not sl.any():
            continue
        labeled = label(sl)
        for region in regionprops(labeled):
            area_mm2 = float(region.area) * pixel_area_mm2
            if area_mm2 < GGO_MIN_AREA_MM2:
                continue
            min_row, min_col, max_row, max_col = region.bbox
            sl_mask = labeled == region.label
            points = _extract_contour(
                sl_mask[min_row:max_row, min_col:max_col],
                min_row,
                min_col,
                rows,
                cols,
            )
            if len(points) < 3:
                continue
            regions.append({
                "sliceIndex": int(z),
                "points": points,
                "areaMm2": round(area_mm2, 1),
            })
            if len(regions) >= MAX_GGO_REGIONS:
                return regions
    return regions
