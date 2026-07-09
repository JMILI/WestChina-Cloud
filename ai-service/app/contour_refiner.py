"""框内轮廓细化（watershed，方案 B 3-P2-01 轻量版）。"""
from __future__ import annotations

import numpy as np
from scipy import ndimage
from skimage.measure import label
from skimage.segmentation import watershed

from .config import settings


def watershed_refine_mask(
    roi_hu: np.ndarray,
    seed_mask: np.ndarray,
    spacing_z: float,
) -> np.ndarray:
    """在候选 mask 内用 HU 梯度 watershed 细化边界。"""
    if seed_mask is None or not np.any(seed_mask):
        return seed_mask

    h, w = roi_hu.shape
    if h < 4 or w < 4:
        return seed_mask

    smooth = ndimage.gaussian_filter(roi_hu.astype(np.float32), sigma=0.8)
    grad = ndimage.morphological_gradient(smooth, size=(3, 3))
    markers = label(seed_mask.astype(bool))
    if markers.max() == 0:
        return seed_mask

    # 限制搜索域：候选膨胀一圈
    domain = ndimage.binary_dilation(seed_mask, iterations=2)
    grad = np.where(domain, grad, grad.max() + 1)

    ws = watershed(grad, markers=markers, mask=domain)
    refined = ws > 0
    if not refined.any():
        return seed_mask

    # 保留与种子重叠最大的连通域
    overlap = label(refined & seed_mask)
    if overlap.max() == 0:
        return seed_mask
    best = max(range(1, overlap.max() + 1), key=lambda i: (overlap == i).sum())
    seed_labels = ws[seed_mask]
    if seed_labels.size == 0:
        return seed_mask
    dominant = int(np.bincount(seed_labels.astype(int)).argmax())
    if dominant <= 0:
        return seed_mask
    return ws == dominant


def refine_mask_with_watershed(
    roi_hu: np.ndarray,
    seed_mask: np.ndarray,
    spacing_z: float,
) -> np.ndarray:
    if not settings.scheme_b_watershed_contour:
        return seed_mask
    try:
        return watershed_refine_mask(roi_hu, seed_mask, spacing_z)
    except Exception:
        return seed_mask
