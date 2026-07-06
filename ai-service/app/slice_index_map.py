"""将体数据层索引映射为前端 DICOM 文件序号（0-based）。"""
from __future__ import annotations

from typing import Any, Dict, List


def map_lesions_to_file_slices(
    lesions: List[Dict[str, Any]],
    file_slice_indices: List[int],
) -> List[Dict[str, Any]]:
    if not file_slice_indices:
        return lesions
    for item in lesions:
        vi = item.get("sliceIndex")
        if vi is None:
            continue
        idx = int(vi)
        if 0 <= idx < len(file_slice_indices):
            item["sliceIndex"] = int(file_slice_indices[idx])
    return lesions


def map_ggo_to_file_slices(
    regions: List[Dict[str, Any]],
    file_slice_indices: List[int],
) -> List[Dict[str, Any]]:
    if not file_slice_indices:
        return regions
    for item in regions:
        vi = item.get("sliceIndex")
        if vi is None:
            continue
        idx = int(vi)
        if 0 <= idx < len(file_slice_indices):
            item["sliceIndex"] = int(file_slice_indices[idx])
    return regions
