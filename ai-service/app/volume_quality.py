"""体数据 HU 质量门控（方案 B P1）。"""
from __future__ import annotations

from typing import Any, Dict, Tuple

import numpy as np

from .hu_utils import lung_parenchyma_3d


def check_volume_hu_quality(volume: np.ndarray) -> Dict[str, Any]:
    """校验肺野 HU 中位数是否在合理范围。"""
    lung = lung_parenchyma_3d(volume)
    if not lung.any():
        return {
            "ok": False,
            "reason": "NO_LUNG_PARENCHYMA",
            "message": "体数据中未检测到肺实质 HU 范围，请确认是否为胸部 CT",
            "lungMedianHu": None,
        }

    sel = volume[lung]
    median_hu = float(np.median(sel))
    ok = -920.0 <= median_hu <= -200.0
    return {
        "ok": ok,
        "reason": None if ok else "HU_OUT_OF_RANGE",
        "message": (
            None
            if ok
            else f"肺野 HU 中位数 {median_hu:.0f} 超出预期范围 [-920, -200]，请检查 DICOM 截距/序列"
        ),
        "lungMedianHu": round(median_hu, 1),
        "lungVoxels": int(lung.sum()),
    }
