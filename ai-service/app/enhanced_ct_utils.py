"""增强 CT ΔHU 分析（方案 B 7-P2-01，需配对增强序列）。"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import numpy as np


def align_volume_z(plain: np.ndarray, enhanced: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """按层数对齐平扫与增强体数据（取较短序列，均匀索引映射）。"""
    z_plain, z_enh = plain.shape[0], enhanced.shape[0]
    if z_plain == z_enh:
        return plain, enhanced
    z = min(z_plain, z_enh)
    if z_plain > z:
        idx = np.linspace(0, z_plain - 1, z, dtype=int)
        plain = plain[idx]
    if z_enh > z:
        idx = np.linspace(0, z_enh - 1, z, dtype=int)
        enhanced = enhanced[idx]
    return plain, enhanced


def compute_lesion_delta_hu(
    plain: np.ndarray,
    enhanced: np.ndarray,
    lesion: Dict[str, Any],
    rows: int,
    cols: int,
) -> Tuple[Optional[float], Optional[str]]:
    """计算病灶 ROI 内增强 ΔHU（增强 - 平扫 median）。"""
    bbox = lesion.get("bbox") or {}
    zi = int(lesion.get("sliceIndex", 0))
    if zi < 0 or zi >= min(plain.shape[0], enhanced.shape[0]):
        return None, None

    min_x = int(max(0, round(float(bbox.get("x", 0)) * cols)))
    max_x = int(min(cols, round((float(bbox.get("x", 0)) + float(bbox.get("width", 0))) * cols)))
    min_y = int(max(0, round(float(bbox.get("y", 0)) * rows)))
    max_y = int(min(rows, round((float(bbox.get("y", 0)) + float(bbox.get("height", 0))) * rows)))
    if max_x <= min_x or max_y <= min_y:
        return None, None

    plain_roi = plain[zi, min_y:max_y, min_x:max_x]
    enh_roi = enhanced[zi, min_y:max_y, min_x:max_x]
    if plain_roi.size == 0:
        return None, None

    delta = float(np.median(enh_roi) - np.median(plain_roi))
    delta = round(delta, 1)

    hint = None
    if delta >= 20:
        hint = "明显强化（ΔHU≥20）"
    elif delta >= 15:
        hint = "中度强化（ΔHU≥15）"
    elif delta >= 5:
        hint = "轻度强化"
    else:
        hint = "强化不明显"

    return delta, hint


def apply_enhancement_to_lesions(
    lesions: List[Dict[str, Any]],
    plain: np.ndarray,
    enhanced: np.ndarray,
    rows: int,
    cols: int,
) -> List[Dict[str, Any]]:
    plain_a, enh_a = align_volume_z(plain, enhanced)
    out: List[Dict[str, Any]] = []
    for lesion in lesions:
        item = dict(lesion)
        delta, hint = compute_lesion_delta_hu(plain_a, enh_a, item, rows, cols)
        if delta is not None:
            item["deltaHu"] = delta
            item["enhancementHint"] = hint
        out.append(item)
    return out
