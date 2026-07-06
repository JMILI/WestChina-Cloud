"""使用 TotalSegmentator 进行肺叶/血管分割，供结节候选筛选使用。"""
from __future__ import annotations

import os
import tempfile
from typing import Tuple

import numpy as np

# 肺叶 ROI（方案 A/B 共用）
LUNG_LOBE_ROIS = [
    "lung_upper_lobe_left",
    "lung_lower_lobe_left",
    "lung_upper_lobe_right",
    "lung_middle_lobe_right",
    "lung_lower_lobe_right",
]

# 血管 mask 使用独立 task=lung_vessels（非 total 任务内的 ROI）
VESSEL_TASK = "lung_vessels"


def is_totalsegmentator_available() -> bool:
    try:
        import totalsegmentator  # noqa: F401
        return True
    except Exception:
        return False


def _cuda_available() -> bool:
    try:
        import torch
        return torch.cuda.is_available()
    except Exception:
        return False


def segment_rois_dict(
    volume: np.ndarray,
    spacing: Tuple[float, float, float],
    roi_subset: list,
) -> dict[str, np.ndarray]:
    """一次 TS 调用，返回各 ROI 的 bool mask 字典。"""
    import nibabel as nib
    from totalsegmentator.python_api import totalsegmentator

    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("MKL_NUM_THREADS", "1")

    spacing_z, spacing_y, spacing_x = spacing
    data = np.ascontiguousarray(volume.transpose(2, 1, 0).astype(np.float32))
    affine = np.array(
        [
            [spacing_x, 0, 0, 0],
            [0, spacing_y, 0, 0],
            [0, 0, spacing_z, 0],
            [0, 0, 0, 1],
        ],
        dtype=np.float64,
    )

    masks: dict[str, np.ndarray] = {}
    with tempfile.TemporaryDirectory(prefix="ts_lung_") as tmp:
        inp = os.path.join(tmp, "input.nii.gz")
        out_dir = os.path.join(tmp, "seg")
        os.makedirs(out_dir, exist_ok=True)
        nib.save(nib.Nifti1Image(data, affine), inp)

        totalsegmentator(
            inp,
            out_dir,
            fast=True,
            ml=False,
            task="total",
            roi_subset=roi_subset,
            nr_thr_resamp=1,
            nr_thr_saving=1,
            quiet=True,
            device="gpu" if _cuda_available() else "cpu",
        )

        for roi in roi_subset:
            seg_path = os.path.join(out_dir, f"{roi}.nii.gz")
            if not os.path.exists(seg_path):
                continue
            seg = nib.load(seg_path).get_fdata()
            if seg.ndim != 3:
                continue
            seg_zyx = (seg > 0).transpose(2, 1, 0)
            if seg_zyx.shape != volume.shape:
                continue
            masks[roi] = seg_zyx

    return masks


def segment_lungs_totalsegmentator(
    volume: np.ndarray,
    spacing: Tuple[float, float, float],
    roi_subset: list | None = None,
) -> np.ndarray:
    """
    返回与 volume 同形状的 bool 肺 mask。

    Args:
        volume: (Z, H, W) HU 值
        spacing: (z, y, x) mm
        roi_subset: 要分割的 ROI 列表，默认 LUNG_LOBE_ROIS

    Returns:
        bool mask，与 volume 同形状。
    """
    if roi_subset is None:
        roi_subset = LUNG_LOBE_ROIS

    masks = segment_rois_dict(volume, spacing, roi_subset)
    combined = np.zeros(volume.shape, dtype=bool)
    for roi_mask in masks.values():
        combined |= roi_mask

    if not combined.any():
        raise RuntimeError("TotalSegmentator 未能分割出肺区，请检查序列是否为胸部 CT")
    return combined


def segment_lung_vessels_mask(
    volume: np.ndarray,
    spacing: Tuple[float, float, float],
) -> np.ndarray:
    """方案 B：独立 lung_vessels 任务分割肺血管 mask。"""
    import nibabel as nib
    from totalsegmentator.python_api import totalsegmentator

    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("MKL_NUM_THREADS", "1")

    spacing_z, spacing_y, spacing_x = spacing
    data = np.ascontiguousarray(volume.transpose(2, 1, 0).astype(np.float32))
    affine = np.array(
        [
            [spacing_x, 0, 0, 0],
            [0, spacing_y, 0, 0],
            [0, 0, spacing_z, 0],
            [0, 0, 0, 1],
        ],
        dtype=np.float64,
    )

    with tempfile.TemporaryDirectory(prefix="ts_vessel_") as tmp:
        inp = os.path.join(tmp, "input.nii.gz")
        out_dir = os.path.join(tmp, "seg")
        os.makedirs(out_dir, exist_ok=True)
        nib.save(nib.Nifti1Image(data, affine), inp)

        totalsegmentator(
            inp,
            out_dir,
            fast=False,
            ml=False,
            task=VESSEL_TASK,
            nr_thr_resamp=1,
            nr_thr_saving=1,
            quiet=True,
            device="gpu" if _cuda_available() else "cpu",
        )

        seg_path = os.path.join(out_dir, f"{VESSEL_TASK}.nii.gz")
        if not os.path.exists(seg_path):
            return np.zeros(volume.shape, dtype=bool)
        seg = nib.load(seg_path).get_fdata()
        if seg.ndim != 3:
            return np.zeros(volume.shape, dtype=bool)
        seg_zyx = (seg > 0).transpose(2, 1, 0)
        if seg_zyx.shape != volume.shape:
            return np.zeros(volume.shape, dtype=bool)
        return seg_zyx.astype(bool)


def get_lung_mask_3d(
    volume: np.ndarray,
    spacing: Tuple[float, float, float],
) -> np.ndarray:
    """方案 A 用：仅肺叶 mask。"""
    return segment_lungs_totalsegmentator(volume, spacing, roi_subset=LUNG_LOBE_ROIS)


def get_lung_vessel_mask_3d(
    volume: np.ndarray,
    spacing: Tuple[float, float, float],
) -> Tuple[np.ndarray, np.ndarray]:
    """方案 B 用：肺叶 mask + lung_vessels 任务血管 mask。"""
    import os

    lung_mask = segment_lungs_totalsegmentator(volume, spacing, roi_subset=LUNG_LOBE_ROIS)
    from .hu_utils import refine_lung_mask
    lung_mask = refine_lung_mask(lung_mask, volume, dilate_iters=1)
    if os.getenv("SCHEME_B_SKIP_VESSEL_SEG", "").lower() in ("1", "true", "yes"):
        return lung_mask, np.zeros(volume.shape, dtype=bool)
    try:
        vessel_mask = segment_lung_vessels_mask(volume, spacing)
    except Exception:
        vessel_mask = np.zeros(volume.shape, dtype=bool)
    return lung_mask, vessel_mask
