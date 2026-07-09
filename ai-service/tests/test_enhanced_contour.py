"""增强 CT 与轮廓细化单元测试。"""
from __future__ import annotations

import numpy as np

from app.contour_refiner import watershed_refine_mask
from app.enhanced_ct_utils import align_volume_z, apply_enhancement_to_lesions, compute_lesion_delta_hu


def test_align_volume_z():
    plain = np.zeros((10, 8, 8), dtype=np.float32)
    enh = np.zeros((6, 8, 8), dtype=np.float32)
    p, e = align_volume_z(plain, enh)
    assert p.shape[0] == e.shape[0] == 6


def test_delta_hu_enhancement():
    plain = np.full((4, 32, 32), 10.0, dtype=np.float32)
    enhanced = np.full((4, 32, 32), 35.0, dtype=np.float32)
    lesion = {
        "sliceIndex": 1,
        "bbox": {"x": 0.25, "y": 0.25, "width": 0.25, "height": 0.25},
    }
    delta, hint = compute_lesion_delta_hu(plain, enhanced, lesion, 32, 32)
    assert delta is not None
    assert delta >= 20
    assert "强化" in (hint or "")


def test_apply_enhancement_to_lesions():
    plain = np.full((2, 16, 16), 0.0, dtype=np.float32)
    enhanced = np.full((2, 16, 16), 25.0, dtype=np.float32)
    lesions = [{"sliceIndex": 0, "bbox": {"x": 0.2, "y": 0.2, "width": 0.3, "height": 0.3}}]
    out = apply_enhancement_to_lesions(lesions, plain, enhanced, 16, 16)
    assert out[0].get("deltaHu") is not None


def test_extract_contour_1x1_safe():
    from app.hu_utils import extract_contour_normalized

    mask = np.ones((1, 1), dtype=bool)
    assert extract_contour_normalized(mask, 0, 0, 64, 64) == []


def test_watershed_refine_keeps_seed():
    hu = np.random.uniform(-600, -400, (24, 24)).astype(np.float32)
    seed = np.zeros((24, 24), dtype=bool)
    seed[8:16, 8:16] = True
    refined = watershed_refine_mask(hu, seed, 1.0)
    assert refined.any()
    assert (refined & seed).any()
