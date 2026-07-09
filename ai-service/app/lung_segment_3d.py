"""3D 肺区分割 HU 回退（不依赖 TotalSegmentator，方案 B P2）。"""
from __future__ import annotations

import numpy as np
from scipy import ndimage
from skimage.measure import label

from .hu_utils import lung_parenchyma_3d, refine_lung_mask


def segment_lungs_hu_3d(volume: np.ndarray) -> np.ndarray:
    """基于 HU 的 3D 肺实质分割，保留左右肺最大连通域。"""
    mask = lung_parenchyma_3d(volume)
    structure = np.ones((3, 3, 3), dtype=bool)
    mask = ndimage.binary_opening(mask, structure=structure, iterations=1)
    mask = ndimage.binary_closing(mask, structure=structure, iterations=2)

    labeled = label(mask)
    if labeled.max() == 0:
        return refine_lung_mask(mask, volume, dilate_iters=1)

    counts = np.bincount(labeled.ravel())
    counts[0] = 0
    keep_ids = np.argsort(counts)[-2:]
    lung = np.isin(labeled, keep_ids)
    lung = ndimage.binary_dilation(lung, iterations=1)
    return refine_lung_mask(lung, volume, dilate_iters=1)
