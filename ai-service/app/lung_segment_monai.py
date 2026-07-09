"""MONAI / 2D 堆叠肺分割后端（方案 B P2，TotalSegmentator 轻量替代）。"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Tuple

import numpy as np
from scipy import ndimage
from skimage.measure import label

from .hu_utils import refine_lung_mask
from .lung_segment_2d import segment_lungs_2d
from .lung_segment_3d import segment_lungs_hu_3d

logger = logging.getLogger(__name__)


def _lung_bundle_dir() -> Path:
    return Path(os.getenv("MONAI_LUNG_BUNDLE_DIR", "")).expanduser()


def is_monai_lung_bundle_ready() -> bool:
    d = _lung_bundle_dir()
    return d.is_dir() and (d / "models" / "model.pt").exists()


def segment_lungs_stack2d(volume: np.ndarray) -> np.ndarray:
    """逐层 2D 肺分割再 3D 合并（CPU 友好，无 TS 依赖）。"""
    z_count = volume.shape[0]
    masks = np.zeros(volume.shape, dtype=bool)
    for z in range(z_count):
        masks[z] = segment_lungs_2d(volume[z])

    structure = np.ones((3, 3, 3), dtype=bool)
    masks = ndimage.binary_closing(masks, structure=structure, iterations=1)
    labeled = label(masks)
    if labeled.max() > 0:
        counts = np.bincount(labeled.ravel())
        counts[0] = 0
        keep_ids = np.argsort(counts)[-2:]
        masks = np.isin(labeled, keep_ids)

    return refine_lung_mask(masks, volume, dilate_iters=1)


def segment_lungs_monai(volume: np.ndarray, spacing: Tuple[float, float, float]) -> np.ndarray:
    """MONAI 肺分割 bundle（若就绪）；否则回退 stack2d。"""
    if not is_monai_lung_bundle_ready():
        logger.info("[lung_seg] MONAI lung bundle 未就绪，使用 stack2d")
        return segment_lungs_stack2d(volume)

    try:
        from .log_paths import ai_temp_directory
        import nibabel as nib
        import torch
        from monai.bundle import ConfigParser

        bundle_dir = str(_lung_bundle_dir())
        spacing_z, spacing_y, spacing_x = spacing
        data = np.ascontiguousarray(volume.transpose(2, 1, 0).astype(np.float32))
        affine = np.array([
            [spacing_x, 0, 0, 0],
            [0, spacing_y, 0, 0],
            [0, 0, spacing_z, 0],
            [0, 0, 0, 1],
        ], dtype=np.float64)

        with ai_temp_directory("monai_lung_") as tmp:
            nii_in = os.path.join(tmp, "ct.nii.gz")
            nib.save(nib.Nifti1Image(data, affine), nii_in)

            parser = ConfigParser()
            parser.read_config(os.path.join(bundle_dir, "configs", "inference.json"))
            parser["bundle_root"] = bundle_dir
            inferer = parser.get_parsed_content("inferer")
            network = parser.get_parsed_content("network")
            device = parser.get_parsed_content("device")
            preprocessing = parser.get_parsed_content("preprocessing")
            postprocessing = parser.get_parsed_content("postprocessing")

            ckpt = torch.load(
                os.path.join(bundle_dir, "models", "model.pt"),
                map_location=device,
                weights_only=False,
            )
            state = ckpt.get("network") or ckpt.get("model") or ckpt
            network.load_state_dict(state, strict=False)
            network.eval()

            batch = preprocessing({"image": nii_in})
            with torch.no_grad():
                out = inferer(batch["image"].to(device), network)
            result = postprocessing({**batch, "pred": out})

        pred = result.get("pred")
        if pred is None:
            raise RuntimeError("empty MONAI lung pred")

        seg = pred.detach().cpu().numpy() if hasattr(pred, "detach") else np.asarray(pred)
        if seg.ndim == 4:
            seg = seg[0]
        seg_zyx = (seg > 0).transpose(2, 1, 0)
        if seg_zyx.shape != volume.shape:
            raise RuntimeError(f"shape mismatch {seg_zyx.shape} vs {volume.shape}")
        return refine_lung_mask(seg_zyx.astype(bool), volume, dilate_iters=1)
    except Exception as exc:
        logger.warning("[lung_seg] MONAI 推理失败: %s，回退 stack2d", exc)
        return segment_lungs_stack2d(volume)


def segment_lungs_by_backend(
    volume: np.ndarray,
    spacing: Tuple[float, float, float],
    backend: str,
) -> np.ndarray:
    """backend: hu | stack2d | monai"""
    mode = (backend or "hu").lower()
    if mode in ("monai", "monai_lung"):
        return segment_lungs_monai(volume, spacing)
    if mode in ("stack2d", "2d", "stack"):
        return segment_lungs_stack2d(volume)
    return segment_lungs_hu_3d(volume)
