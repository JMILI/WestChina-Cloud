"""规则多类病灶分类（方案 B P2：在 DL 多类头就绪前的细分类）。"""
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple


DL_CLASS_LABELS = {
    "ggo": ("ggo", "磨玻璃(DL)", 0.78),
    "solid": ("solid", "实性(DL)", 0.80),
    "calcified": ("calcified", "钙化(DL)", 0.82),
    "mixed_ggo": ("mixed_ggo", "混合磨玻璃(DL)", 0.76),
}


def classify_lesion_multiclass(
    lesion_type: str,
    sub_type: str,
    mean_hu: float,
    morphology: Optional[Dict[str, Any]] = None,
    dl_model_class: Optional[str] = None,
) -> Tuple[str, str, float]:
    """返回 (detectionClass, detectionClassLabel, classConfidence)。"""
    if dl_model_class and dl_model_class in DL_CLASS_LABELS:
        dc, label, conf = DL_CLASS_LABELS[dl_model_class]
        return dc, label, conf

    morph = morphology or {}
    spiculation = morph.get("spiculationHint", "")
    lobulation = morph.get("lobulationHint", "")

    if sub_type == "mixedGGO":
        return "mixed_ggo", "混合磨玻璃", 0.82
    if sub_type == "pureGGO" or lesion_type == "磨玻璃结节":
        return "ggo", "磨玻璃", 0.88
    if sub_type == "calcified" or lesion_type == "高密度结节":
        return "calcified", "钙化/高密度", 0.86
    if lesion_type == "肺结节" or sub_type == "solid":
        if spiculation in ("边界欠规则", "分叶/毛刺倾向"):
            return "solid_suspicious", "实性可疑", 0.72
        return "solid", "实性结节", 0.84
    if not lesion_type or lesion_type == "排除":
        return "unknown", "待复核", 0.45
    if -280 < mean_hu < 12:
        return "ggo", "磨玻璃倾向", 0.55
    return "unknown", "未分类", 0.5
