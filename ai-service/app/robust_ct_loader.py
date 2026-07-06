"""健壮 DICOM 序列加载器。

- 按 ImagePositionPatient (IPP) + ImageOrientationPatient (IOP) 排序
- 回退到 InstanceNumber 或文件名顺序
- 过滤 ImageType 含 LOCALIZER / SCOUT 的定位像
- 计算 spacing (z, y, x)
"""
from __future__ import annotations

import io
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pydicom

from .hu_utils import pixel_array_to_hu


@dataclass
class VolumeMeta:
    """3D 体数据及其元数据。"""
    volume: np.ndarray          # (Z, H, W) HU float32
    spacing: Tuple[float, float, float]  # (z, y, x) mm
    rows: int
    cols: int
    slice_count: int
    sort_method: str            # "ipp" | "instance_number" | "filename"
    removed_localizers: int = 0
    # 排序后 volume[z] 对应 MinIO 文件序号（0-based，即 1.dcm -> 0）
    file_slice_indices: List[int] = field(default_factory=list)


def _get_ipp(ds: pydicom.Dataset) -> Optional[Tuple[float, float, float]]:
    """提取 ImagePositionPatient，返回 (x, y, z) 或 None。"""
    ipp = getattr(ds, "ImagePositionPatient", None)
    if ipp is None:
        return None
    try:
        vals = [float(v) for v in ipp]
        if len(vals) >= 3:
            return (vals[0], vals[1], vals[2])
    except (TypeError, ValueError):
        pass
    return None


def _get_iop(ds: pydicom.Dataset) -> Optional[Tuple[float, ...]]:
    """提取 ImageOrientationPatient。"""
    iop = getattr(ds, "ImageOrientationPatient", None)
    if iop is None:
        return None
    try:
        vals = [float(v) for v in iop]
        if len(vals) >= 6:
            return tuple(vals[:6])
    except (TypeError, ValueError):
        pass
    return None


def _is_localizer(ds: pydicom.Dataset) -> bool:
    """检查 ImageType 是否含 LOCALIZER 或 SCOUT。"""
    it = getattr(ds, "ImageType", None)
    if it is None:
        return False
    if isinstance(it, (list, tuple)):
        text = " ".join(str(v).upper() for v in it)
    else:
        text = str(it).upper()
    return "LOCALIZER" in text or "SCOUT" in text


def _sort_key_ipp(
    ds: pydicom.Dataset,
) -> Tuple[int, float]:
    """按 IPP 的 z 分量排序；回退到 InstanceNumber。"""
    ipp = _get_ipp(ds)
    if ipp is not None:
        return (0, ipp[2])  # (priority=0, z_value)
    inum = getattr(ds, "InstanceNumber", None)
    if inum is not None:
        try:
            return (1, float(inum))
        except (TypeError, ValueError):
            pass
    return (2, 0.0)


def filter_localizer(datasets: List[pydicom.Dataset]) -> Tuple[List[pydicom.Dataset], int]:
    """过滤定位像，返回 (保留的 datasets, 移除数量)。"""
    kept = []
    removed = 0
    for ds in datasets:
        if _is_localizer(ds):
            removed += 1
        else:
            kept.append(ds)
    return kept, removed


def sort_by_ipp(datasets: List[pydicom.Dataset]) -> Tuple[List[pydicom.Dataset], str]:
    """按 IPP z 排序；返回 (排序后的 datasets, sort_method)。"""
    # 检查是否所有切片都有 IPP
    ipp_count = sum(1 for ds in datasets if _get_ipp(ds) is not None)
    if ipp_count >= len(datasets) // 2:
        datasets.sort(key=_sort_key_ipp)
        return datasets, "ipp"

    # 回退到 InstanceNumber
    inum_count = sum(1 for ds in datasets if getattr(ds, "InstanceNumber", None) is not None)
    if inum_count >= len(datasets) // 2:
        datasets.sort(key=lambda ds: (0, int(getattr(ds, "InstanceNumber", 1))))
        return datasets, "instance_number"

    return datasets, "filename"


def _to_hu(ds: pydicom.Dataset, arr: np.ndarray) -> np.ndarray:
    return pixel_array_to_hu(ds, arr)


def _extract_spacing(datasets: List[pydicom.Dataset]) -> Tuple[float, float, float]:
    """从 DICOM 元数据提取 spacing (z, y, x)。"""
    spacing_z = 1.0
    spacing_y, spacing_x = 1.0, 1.0

    if len(datasets) >= 2:
        ipp0 = _get_ipp(datasets[0])
        ipp1 = _get_ipp(datasets[-1])
        if ipp0 is not None and ipp1 is not None:
            dz = abs(ipp1[2] - ipp0[2]) / max(len(datasets) - 1, 1)
            if dz > 0:
                spacing_z = dz

    if spacing_z == 1.0:
        for ds in datasets:
            st = getattr(ds, "SpacingBetweenSlices", None)
            if st is not None:
                spacing_z = float(st)
                break
            st = getattr(ds, "SliceThickness", None)
            if st is not None:
                spacing_z = float(st)
                break

    for ds in datasets:
        ps = getattr(ds, "PixelSpacing", None)
        if ps is not None and len(ps) >= 2:
            spacing_y = float(ps[0])
            spacing_x = float(ps[1])
            break

    return (spacing_z, spacing_y, spacing_x)


def load_series_dicoms(raw_list: List[bytes]) -> VolumeMeta:
    """从 DICOM 字节列表构建排序后的 3D 体数据。

    Args:
        raw_list: 从 MinIO 下载的 DICOM 字节列表（未排序）。

    Returns:
        VolumeMeta: 排序后的体数据及元数据。
    """
    datasets: List[pydicom.Dataset] = []
    file_indices: List[int] = []
    for file_idx, raw in enumerate(raw_list):
        try:
            ds = pydicom.dcmread(io.BytesIO(raw), force=True)
            if not hasattr(ds, "pixel_array") and not hasattr(ds, "PixelData"):
                try:
                    _ = ds.pixel_array
                except Exception:
                    continue
            if _is_localizer(ds):
                continue
            datasets.append(ds)
            file_indices.append(file_idx)
        except Exception:
            continue

    if not datasets:
        raise RuntimeError("序列中全是定位像，无可用于识别的轴位切片")

    removed = len(raw_list) - len(datasets)

    # IPP 排序（同时重排 file_indices）
    paired = list(zip(file_indices, datasets))
    ipp_count = sum(1 for _, ds in paired if _get_ipp(ds) is not None)
    if ipp_count >= len(paired) // 2:
        paired.sort(key=lambda p: _sort_key_ipp(p[1]))
        sort_method = "ipp"
    else:
        inum_count = sum(1 for _, ds in paired if getattr(ds, "InstanceNumber", None) is not None)
        if inum_count >= len(paired) // 2:
            paired.sort(key=lambda p: (0, int(getattr(p[1], "InstanceNumber", 1))))
            sort_method = "instance_number"
        else:
            sort_method = "filename"
    file_indices = [p[0] for p in paired]
    datasets = [p[1] for p in paired]

    # 提取 spacing
    spacing = _extract_spacing(datasets)

    # 构建 3D 体
    slices_hu = []
    for ds in datasets:
        arr = ds.pixel_array
        hu = _to_hu(ds, arr)
        slices_hu.append(hu)

    volume = np.stack(slices_hu, axis=0).astype(np.float32)
    rows, cols = volume.shape[1], volume.shape[2]

    return VolumeMeta(
        volume=volume,
        spacing=spacing,
        rows=rows,
        cols=cols,
        slice_count=len(datasets),
        sort_method=sort_method,
        removed_localizers=removed,
        file_slice_indices=file_indices,
    )
