"""2D 肺区分割（形态学，不依赖深度学习模型）。"""
from __future__ import annotations

import numpy as np
from scipy import ndimage
from skimage.measure import label

from .hu_utils import lung_parenchyma_2d, refine_lung_mask


def segment_lungs_2d(slice_hu: np.ndarray) -> np.ndarray:
    """对单层 CT (HU) 进行 2D 肺区分割，排除空气与胸壁脂肪。"""
    parenchyma = lung_parenchyma_2d(slice_hu)

    structure = np.ones((3, 3), dtype=bool)
    mask = ndimage.binary_opening(parenchyma, structure=structure, iterations=1)
    mask = ndimage.binary_closing(mask, structure=structure, iterations=1)

    labeled = label(mask)
    if labeled.max() == 0:
        return mask

    counts = np.bincount(labeled.ravel())
    counts[0] = 0
    keep_ids = np.argsort(counts)[-2:]
    lung = np.isin(labeled, keep_ids)
    return refine_lung_mask(lung, slice_hu, dilate_iters=0)
