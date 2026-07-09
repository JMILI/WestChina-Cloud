"""HU 分类单元测试。"""
from __future__ import annotations

from app.hu_utils import classify_nodule_hu, ggo_hu_window


def test_classify_nodule_hu_ggo():
    t, label, ok = classify_nodule_hu(-500)
    assert ok
    assert t == "磨玻璃结节"
    assert "磨玻璃" in label


def test_classify_nodule_hu_solid():
    t, label, ok = classify_nodule_hu(40)
    assert ok
    assert t == "肺结节"


def test_classify_nodule_hu_reject():
    _, _, ok = classify_nodule_hu(-950)
    assert not ok


def test_ggo_hu_window_thin():
    lo, hi = ggo_hu_window(0.8)
    assert lo <= -850
    assert hi >= -320
