"""GGO 检测单元测试。"""
from __future__ import annotations

import numpy as np

from app.ggo_segmentation import detect_ggo_regions


def test_ggo_detect_v2_vessel_subtract():
    from app.config import settings

    settings.scheme_b_ggo_backend = "adaptive"
    vol = np.full((8, 64, 64), -500.0, dtype=np.float32)
    lung = np.ones_like(vol, dtype=bool)
    vessel = np.zeros_like(vol, dtype=bool)
    vessel[:, 30:34, 30:34] = True
    regions, backend = detect_ggo_regions(vol, lung, vessel, (1.0, 0.7, 0.7), 64, 64)
    assert isinstance(regions, list)
    assert backend in ("adaptive", "heuristic", "model")


def test_ggo_backend_off_default():
    from app.config import settings

    settings.scheme_b_ggo_backend = "off"
    vol = np.full((4, 32, 32), -500.0, dtype=np.float32)
    lung = np.ones_like(vol, dtype=bool)
    regions, backend = detect_ggo_regions(vol, lung, None, (1.0, 0.7, 0.7), 32, 32)
    assert regions == []
    assert backend == "off"
