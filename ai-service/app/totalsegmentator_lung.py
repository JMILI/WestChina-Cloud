"""使用 TotalSegmentator 进行肺叶/血管分割，供结节候选筛选使用。"""
from __future__ import annotations

import os
import time
from typing import Dict, Tuple

import numpy as np

from .config import settings

# 肺叶 ROI（方案 A/B 共用）
LUNG_LOBE_ROIS = [
    "lung_upper_lobe_left",
    "lung_lower_lobe_left",
    "lung_upper_lobe_right",
    "lung_middle_lobe_right",
    "lung_lower_lobe_right",
]

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


def _use_hu_lung_fallback() -> bool:
    mode = os.getenv("SCHEME_B_LUNG_SEG", "").lower()
    return mode in ("hu", "fallback", "2d", "stack2d", "stack", "monai")


def _lung_seg_backend() -> str:
    return os.getenv("SCHEME_B_LUNG_SEG", "totalsegmentator").lower()


def _ts_parallel_enabled() -> bool:
    return os.getenv("SCHEME_B_TS_PARALLEL", "true").lower() in ("1", "true", "yes")


def segment_rois_dict(volume, spacing, roi_subset) -> dict[str, np.ndarray]:
    """一次 TS 调用，返回各 ROI 的 bool mask 字典。"""
    import nibabel as nib
    from .log_paths import ai_temp_directory
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
    with ai_temp_directory("ts_lung_") as tmp:
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


def segment_lungs_totalsegmentator(volume, spacing, roi_subset=None) -> np.ndarray:
    if roi_subset is None:
        roi_subset = LUNG_LOBE_ROIS

    masks = segment_rois_dict(volume, spacing, roi_subset)
    combined = np.zeros(volume.shape, dtype=bool)
    for roi_mask in masks.values():
        combined |= roi_mask

    if not combined.any():
        raise RuntimeError("TotalSegmentator 未能分割出肺区，请检查序列是否为胸部 CT")
    return combined


def segment_lung_vessels_mask(volume, spacing) -> np.ndarray:
    import nibabel as nib
    from .log_paths import ai_temp_directory
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

    with ai_temp_directory("ts_vessel_") as tmp:
        inp = os.path.join(tmp, "input.nii.gz")
        out_dir = os.path.join(tmp, "seg")
        os.makedirs(out_dir, exist_ok=True)
        nib.save(nib.Nifti1Image(data, affine), inp)

        totalsegmentator(
            inp,
            out_dir,
            fast=os.getenv("TS_VESSEL_FAST", "true").lower() in ("1", "true", "yes"),
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


def get_lung_mask_3d(volume, spacing) -> np.ndarray:
    return segment_lungs_totalsegmentator(volume, spacing, roi_subset=LUNG_LOBE_ROIS)


def get_lung_vessel_mask_3d(
    volume: np.ndarray,
    spacing: Tuple[float, float, float],
) -> Tuple[np.ndarray, np.ndarray, dict, Dict[str, np.ndarray]]:
    """方案 B：肺叶 mask + 血管 mask + 元信息 + 各肺叶 mask 字典。"""
    from .hu_utils import refine_lung_mask
    from .lobe_locator import summarize_lobe_masks

    meta: dict = {
        "vesselMaskMissing": False,
        "lungSegSource": "totalsegmentator",
    }
    lobe_masks: Dict[str, np.ndarray] = {}
    t0 = time.time()

    use_hu = _lung_seg_backend() != "totalsegmentator" or not is_totalsegmentator_available()
    backend = _lung_seg_backend()

    if use_hu:
        from .lung_segment_monai import segment_lungs_by_backend
        lung_mask = segment_lungs_by_backend(volume, spacing, backend)
        meta["lungSegSource"] = backend if backend != "totalsegmentator" else "hu_fallback"
    elif _ts_parallel_enabled() and not settings.scheme_b_skip_vessel_seg:
        from concurrent.futures import ThreadPoolExecutor

        with ThreadPoolExecutor(max_workers=2) as pool:
            fut_lobes = pool.submit(segment_rois_dict, volume, spacing, LUNG_LOBE_ROIS)
            fut_vessel = pool.submit(segment_lung_vessels_mask, volume, spacing)
            lobe_masks = fut_lobes.result()
            vessel_mask = fut_vessel.result()
        lung_mask = np.zeros(volume.shape, dtype=bool)
        for roi_mask in lobe_masks.values():
            lung_mask |= roi_mask
        if not lung_mask.any():
            from .lung_segment_3d import segment_lungs_hu_3d
            lung_mask = segment_lungs_hu_3d(volume)
            lobe_masks = {}
            meta["lungSegSource"] = "hu_fallback"
        else:
            meta["tsParallel"] = True
            if not vessel_mask.any():
                meta["vesselMaskMissing"] = True
            lung_mask = refine_lung_mask(lung_mask, volume, dilate_iters=1)
            meta["segmentationMs"] = int((time.time() - t0) * 1000)
            meta["lobeVoxels"] = summarize_lobe_masks(lobe_masks)
            return lung_mask, vessel_mask, meta, lobe_masks
    else:
        try:
            lobe_masks = segment_rois_dict(volume, spacing, LUNG_LOBE_ROIS)
            lung_mask = np.zeros(volume.shape, dtype=bool)
            for roi_mask in lobe_masks.values():
                lung_mask |= roi_mask
            if not lung_mask.any():
                raise RuntimeError("empty lung mask")
        except Exception:
            from .lung_segment_3d import segment_lungs_hu_3d
            lung_mask = segment_lungs_hu_3d(volume)
            lobe_masks = {}
            meta["lungSegSource"] = "hu_fallback"

    lung_mask = refine_lung_mask(lung_mask, volume, dilate_iters=1)
    meta["segmentationMs"] = int((time.time() - t0) * 1000)
    meta["lobeVoxels"] = summarize_lobe_masks(lobe_masks)

    if settings.scheme_b_skip_vessel_seg:
        meta["vesselMaskMissing"] = True
        return lung_mask, np.zeros(volume.shape, dtype=bool), meta, lobe_masks

    try:
        if use_hu:
            meta["vesselMaskMissing"] = True
            vessel_mask = np.zeros(volume.shape, dtype=bool)
        else:
            vessel_mask = segment_lung_vessels_mask(volume, spacing)
            if not vessel_mask.any():
                meta["vesselMaskMissing"] = True
    except Exception:
        vessel_mask = np.zeros(volume.shape, dtype=bool)
        meta["vesselMaskMissing"] = True

    return lung_mask, vessel_mask, meta, lobe_masks
