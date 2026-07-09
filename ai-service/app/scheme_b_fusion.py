"""方案 B：融合精准分析。

TotalSegmentator 肺叶+血管 + nnDetection / MONAI RetinaNet + HU 启发式 GGO（合并进 lesions）。
子引擎：detectSubEngine ∈ {auto, monai, nndet}。
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

import numpy as np

from .lesion_enrichment import (
    enrich_lesion,
    ggo_region_to_lesion,
    merge_lesion_lists,
)
from .ggo_segmentation import detect_ggo_regions
from .config import settings
from .scheme_b_filter import filter_lesions_p1, is_low_conf_ggo_candidate
from .monai_bundle_manager import is_monai_available, is_monai_bundle_ready
from .nndet_wrapper import is_nndet_available, is_nndet_weights_ready

MAX_GGO_SUPPLEMENT = 12


def is_gpu_available() -> bool:
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


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

    Returns:
        {"lesions": [...], "ggoRegions": [], "stats": {...}}
        ggoRegions 保留空列表以兼容旧客户端；GGO 已合并进 lesions。
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

    lung_mask, vessel_mask, seg_meta, lobe_masks = get_lung_vessel_mask_3d(volume, spacing)

    raw_lesions, low_conf_lesions, candidate_source, nndet_candidates = _run_candidate_detector(
        volume, spacing, rows, cols, sub_engine=sub_engine
    )

    filtered, filter_stats = filter_lesions_p1(
        raw_lesions, volume, lung_mask, vessel_mask, spacing, rows, cols
    )

    low_conf_filtered, _ = filter_lesions_p1(
        low_conf_lesions,
        volume,
        lung_mask,
        vessel_mask,
        spacing,
        rows,
        cols,
        allow_low_conf_ggo=True,
    )
    low_conf_ggo: List[Dict[str, Any]] = []
    for lesion in low_conf_filtered:
        if not is_low_conf_ggo_candidate(lesion, volume, spacing, rows, cols):
            continue
        lesion = dict(lesion)
        lesion["source"] = "dl_low"
        lesion["detectionConfidence"] = round(
            float(lesion.get("detectionConfidence") or lesion.get("confidence") or 0.03), 3
        )
        lesion["confidence"] = lesion["detectionConfidence"]
        low_conf_ggo.append(lesion)

    enriched: List[Dict[str, Any]] = []
    enrich_rejected = 0
    for lesion in filtered:
        item = enrich_lesion(
            lesion, volume, lung_mask, spacing, rows, cols,
            source=lesion.get("source", "dl_high"),
            lobe_masks=lobe_masks,
        )
        if item is None:
            enrich_rejected += 1
            continue
        enriched.append(item)

    for lesion in low_conf_ggo:
        item = enrich_lesion(lesion, volume, lung_mask, spacing, rows, cols, source="dl_low", lobe_masks=lobe_masks)
        if item:
            enriched.append(item)

    ggo_raw, ggo_backend = detect_ggo_regions(
        volume, lung_mask, vessel_mask, spacing, rows, cols,
    )
    ggo_lesions: List[Dict[str, Any]] = []
    for idx, region in enumerate(ggo_raw[:MAX_GGO_SUPPLEMENT]):
        item = ggo_region_to_lesion(region, idx, volume, lung_mask, spacing, rows, cols, lobe_masks=lobe_masks)
        if item:
            ggo_lesions.append(item)

    merged, ggo_skipped = merge_lesion_lists(enriched, ggo_lesions)
    merged.sort(key=lambda x: float(x.get("detectionConfidence") or x.get("confidence") or 0), reverse=True)

    merged = merged[: settings.max_lesions]

    return {
        "lesions": merged,
        "ggoRegions": [],
        "stats": {
            "lung_voxels": int(lung_mask.sum()),
            "vessel_voxels": int(vessel_mask.sum()) if vessel_mask is not None else 0,
            "vesselMaskMissing": seg_meta.get("vesselMaskMissing", False),
            "lungSegSource": seg_meta.get("lungSegSource"),
            "segmentationMs": seg_meta.get("segmentationMs"),
            "lobeVoxels": seg_meta.get("lobeVoxels"),
            "nndet_candidates": nndet_candidates,
            "raw_lesion_count": len(raw_lesions),
            "fusion_filtered": len(enriched),
            "fusion_rejected": max(0, len(raw_lesions) - len(filtered)),
            "filter_lung_rejected": filter_stats.get("lung_rejected", 0),
            "filter_vessel_rejected": filter_stats.get("vessel_rejected", 0),
            "filter_solidity_rejected": filter_stats.get("solidity_rejected", 0),
            "filter_sphericity_rejected": filter_stats.get("sphericity_rejected", 0),
            "filter_hu_stddev_rejected": filter_stats.get("hu_stddev_rejected", 0),
            "filter_hilar_downweighted": filter_stats.get("hilar_downweighted", 0),
            "low_conf_ggo_count": len(low_conf_ggo),
            "enrich_rejected": enrich_rejected,
            "ggo_heuristic_count": len(ggo_raw),
            "ggoBackend": ggo_backend,
            "ggo_merged_count": len(ggo_lesions) - ggo_skipped,
            "ggo_merge_skipped": ggo_skipped,
            "candidate_source": candidate_source,
            "sub_engine": sub_engine,
        },
    }


def _parse_detector_result(result: Dict[str, Any], source_label: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], str, int]:
    lesions = result.get("lesions", [])
    low_conf = result.get("lowConfLesions", [])
    count = int(result.get("stats", {}).get("candidates", len(lesions)))
    return lesions, low_conf, source_label, count


def _run_candidate_detector(
    volume: np.ndarray,
    spacing: Tuple[float, float, float],
    rows: int,
    cols: int,
    sub_engine: str = "auto",
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], str, int]:
    """返回 (lesions, low_conf_lesions, source_label, raw_candidate_count)。"""
    nndet_ready = is_nndet_available() and is_nndet_weights_ready()
    monai_ready = is_monai_available() and is_monai_bundle_ready()

    if sub_engine == "nndet":
        if not nndet_ready:
            raise RuntimeError(
                "nnDetection 权重未就绪。请设置 NNDET_LUNA16_WEIGHT_DIR 指向包含 "
                "plan_inference.pkl + config.yaml + *.ckpt 的训练目录。"
            )
        from .nndet_wrapper import detect_lesions_nndet
        return _parse_detector_result(
            detect_lesions_nndet(volume, spacing, rows, cols), "nndetection",
        )

    if sub_engine == "monai":
        if not monai_ready:
            raise RuntimeError("MONAI RetinaNet bundle 未就绪。请执行 pip install -r requirements-monai.txt")
        from .monai_nnunet_detector import detect_lesions_monai_nnunet
        return _parse_detector_result(
            detect_lesions_monai_nnunet(volume, spacing, rows, cols), "monai-retinanet",
        )

    if nndet_ready:
        from .nndet_wrapper import detect_lesions_nndet
        return _parse_detector_result(
            detect_lesions_nndet(volume, spacing, rows, cols), "nndetection",
        )

    if monai_ready:
        from .monai_nnunet_detector import detect_lesions_monai_nnunet
        return _parse_detector_result(
            detect_lesions_monai_nnunet(volume, spacing, rows, cols), "monai-retinanet",
        )

    return [], [], "none", 0
