"""方案 B 单元测试（P2 汇总）。"""
from __future__ import annotations

import numpy as np

from app.lesion_classifier import classify_lesion_multiclass
from app.lesion_morphology import (
    compute_mask_morphology,
    compute_pleural_distance_mm,
    pleural_hint,
)
from app.lobe_locator import locate_lobe, locate_lobe_heuristic
from app.lung_segment_monai import segment_lungs_stack2d
from app.volume_quality import check_volume_hu_quality

from tests.test_ggo_detect_v2 import test_ggo_detect_v2_vessel_subtract
from tests.test_hu_classify import (
    test_classify_nodule_hu_ggo,
    test_classify_nodule_hu_reject,
    test_classify_nodule_hu_solid,
    test_ggo_hu_window_thin,
)
from tests.test_scheme_b_filter import (
    test_filter_lesions_keeps_with_relaxed_iou,
    test_filter_vessel_iou_relaxed,
)


def test_morphology_circularity():
    sl = np.zeros((20, 20), dtype=bool)
    sl[5:15, 5:15] = True
    m = compute_mask_morphology(sl)
    assert m.get("circularity", 0) > 0.5


def test_pleural_distance_subpleural():
    lung = np.zeros((64, 64), dtype=bool)
    lung[5:60, 5:60] = True
    lesion = np.zeros((64, 64), dtype=bool)
    lesion[5:10, 30:35] = True
    dist = compute_pleural_distance_mm(lesion, lung, 0.7, 0.7)
    assert dist is not None
    assert dist <= 5.0
    assert pleural_hint(dist) in ("胸膜下/贴胸膜", "近胸膜")


def test_lobe_locator():
    lobe_masks = {
        "lung_upper_lobe_left": np.zeros((4, 64, 64), dtype=bool),
    }
    lobe_masks["lung_upper_lobe_left"][1, 20:40, 20:40] = True
    label = locate_lobe(lobe_masks, 1, 30, 30, 64, 64)
    assert label == "左肺上叶"


def test_lobe_heuristic_fallback():
    label = locate_lobe({}, 1, 10, 10, 64, 64)
    assert label == "左肺上叶"
    assert locate_lobe_heuristic(35, 50, 64, 64) == "右肺中叶"


def test_lung_stack2d():
    vol = np.random.uniform(-900, 100, (6, 48, 48)).astype(np.float32)
    vol[:, 10:38, 10:38] = np.random.uniform(-850, -400, (6, 28, 28))
    mask = segment_lungs_stack2d(vol)
    assert mask.shape == vol.shape
    assert mask.any()


def test_volume_quality_ok():
    vol = np.random.uniform(-600, -400, (10, 32, 32)).astype(np.float32)
    q = check_volume_hu_quality(vol)
    assert q["ok"]


def test_volume_cache_roundtrip():
    import os
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        os.environ["SCHEME_B_VOLUME_CACHE"] = "true"
        os.environ["SCHEME_B_CACHE_DIR"] = tmp
        from app.robust_ct_loader import VolumeMeta
        from app.volume_cache import save_volume_cache, try_load_cached_volume

        vol = np.random.uniform(-600, -400, (4, 16, 16)).astype(np.float32)
        meta = VolumeMeta(
            volume=vol,
            spacing=(1.0, 0.7, 0.7),
            rows=16,
            cols=16,
            slice_count=4,
            sort_method="ipp",
            file_slice_indices=[0, 1, 2, 3],
        )
        save_volume_cache(meta, "study1", "series1")
        loaded = try_load_cached_volume("study1", "series1", 4)
        assert loaded is not None
        assert loaded.slice_count == 4
        assert loaded.volume.shape == vol.shape


def test_cavitation_hint_solid_with_pocket():
    from app.lesion_morphology import detect_cavitation_hint

    vol = np.full((1, 32, 32), 20.0, dtype=np.float32)
    crop = np.zeros((16, 16), dtype=bool)
    crop[4:12, 4:12] = True
    vol[0, 6:10, 6:10] = -500.0
    hint = detect_cavitation_hint(vol, 0, crop, 4, 4, 25.0)
    assert hint == "可见空泡征倾向"


def test_lesion_multiclass():
    dc, label, conf = classify_lesion_multiclass("磨玻璃结节", "pureGGO", -500.0)
    assert dc == "ggo"
    assert conf > 0.5

    dc2, _, _ = classify_lesion_multiclass(
        "肺结节", "solid", 45.0, {"spiculationHint": "分叶/毛刺倾向"},
    )
    assert dc2 == "solid_suspicious"

    dc3, label3, _ = classify_lesion_multiclass(
        "肺结节", "solid", 45.0, dl_model_class="ggo",
    )
    assert dc3 == "ggo"
    assert "DL" in label3
