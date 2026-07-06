"""全序列体数据降采样（CPU 大序列加速）。"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

import numpy as np


def subsample_volume_z(
    volume: np.ndarray,
    spacing: Tuple[float, float, float],
    max_slices: int,
) -> Tuple[np.ndarray, Tuple[float, float, float], Dict[int, int], Dict[str, Any]]:
    """沿 z 轴均匀降采样，返回 (新体, 新 spacing, 层索引映射, 统计)。

    slice_remap: 降采样后 sliceIndex -> 原始 sliceIndex
    """
    z_count = int(volume.shape[0])
    if max_slices <= 0 or z_count <= max_slices:
        identity = {i: i for i in range(z_count)}
        return volume, spacing, identity, {
            "subsampled": False,
            "original_slices": z_count,
            "used_slices": z_count,
        }

    indices = np.linspace(0, z_count - 1, max_slices, dtype=int)
    indices = np.unique(indices)
    new_volume = volume[indices]
    factor = z_count / max(len(indices), 1)
    new_spacing = (spacing[0] * factor, spacing[1], spacing[2])
    slice_remap = {i: int(indices[i]) for i in range(len(indices))}
    return new_volume, new_spacing, slice_remap, {
        "subsampled": True,
        "original_slices": z_count,
        "used_slices": len(indices),
        "z_spacing_factor": round(factor, 3),
    }


def remap_lesions_slice_index(lesions: List[Dict[str, Any]], slice_remap: Dict[int, int]) -> List[Dict[str, Any]]:
    """将病灶 sliceIndex 从降采样坐标映射回原始序列层号。"""
    if not slice_remap or all(k == v for k, v in slice_remap.items()):
        return lesions
    for item in lesions:
        si = item.get("sliceIndex")
        if si is not None and int(si) in slice_remap:
            item["sliceIndex"] = slice_remap[int(si)]
    return lesions


def remap_ggo_regions(ggo_regions: List[Dict[str, Any]], slice_remap: Dict[int, int]) -> List[Dict[str, Any]]:
    if not slice_remap or all(k == v for k, v in slice_remap.items()):
        return ggo_regions
    out = []
    for region in ggo_regions:
        r = dict(region)
        si = r.get("sliceIndex")
        if si is not None and int(si) in slice_remap:
            r["sliceIndex"] = slice_remap[int(si)]
        out.append(r)
    return out
