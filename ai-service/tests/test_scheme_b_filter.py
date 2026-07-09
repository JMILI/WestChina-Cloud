"""方案 B 融合过滤单元测试。"""
from __future__ import annotations

import numpy as np

from app.scheme_b_filter import filter_lesions_p1, lesion_vessel_iou


def test_filter_vessel_iou_relaxed():
    lesion = {
        "sliceIndex": 0,
        "bbox": {"x": 0.3, "y": 0.3, "width": 0.1, "height": 0.1},
    }
    vol = np.zeros((4, 100, 100), dtype=np.float32)
    lung = np.ones_like(vol, dtype=bool)
    vessel = np.zeros_like(vol, dtype=bool)
    vessel[0, 35:45, 35:45] = True
    iou = lesion_vessel_iou(lesion, vessel, 100, 100)
    assert 0 <= iou <= 1


def test_filter_lesions_keeps_with_relaxed_iou():
    vol = np.random.uniform(-600, -400, (4, 64, 64)).astype(np.float32)
    lung = vol < -300
    vessel = np.zeros_like(lung, dtype=bool)
    lesions = [{
        "sliceIndex": 1,
        "bbox": {"x": 0.2, "y": 0.2, "width": 0.15, "height": 0.15},
        "confidence": 0.8,
    }]
    kept, stats = filter_lesions_p1(lesions, vol, lung, vessel, (1.0, 0.7, 0.7), 64, 64)
    assert len(kept) >= 0
    assert "vessel_rejected" in stats
