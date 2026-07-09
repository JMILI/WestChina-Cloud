"""方案 B 肺叶定位：TS mask + bbox 启发式 fallback。"""
from __future__ import annotations

from typing import Any, Dict, Optional

import numpy as np

LOBE_LABELS: Dict[str, str] = {
    "lung_upper_lobe_left": "左肺上叶",
    "lung_lower_lobe_left": "左肺下叶",
    "lung_upper_lobe_right": "右肺上叶",
    "lung_middle_lobe_right": "右肺中叶",
    "lung_lower_lobe_right": "右肺下叶",
}


def locate_lobe_heuristic(cy: float, cx: float, rows: int, cols: int) -> str:
    """无肺叶 mask 时，按 bbox 中心粗略定位（左/右 + 上/中/下）。"""
    side = "左" if cx < cols * 0.5 else "右"
    y_ratio = cy / max(rows, 1)
    if y_ratio < 0.38:
        lobe = "上叶"
    elif y_ratio < 0.62 and side == "右":
        lobe = "中叶"
    elif y_ratio < 0.65:
        lobe = "上叶" if side == "左" else "中叶"
    else:
        lobe = "下叶"
    return f"{side}肺{lobe}"


def locate_lobe(
    lobe_masks: Dict[str, np.ndarray],
    slice_index: int,
    cy: float,
    cx: float,
    rows: int,
    cols: int,
) -> Optional[str]:
    """根据病灶重心所在肺叶 mask 返回中文叶位；无 mask 时用启发式。"""
    if not lobe_masks:
        return locate_lobe_heuristic(cy, cx, rows, cols)
    zi = int(max(0, min(slice_index, next(iter(lobe_masks.values())).shape[0] - 1)))
    yi = int(max(0, min(rows - 1, round(cy))))
    xi = int(max(0, min(cols - 1, round(cx))))

    best_label = None
    best_score = 0
    for roi_id, mask in lobe_masks.items():
        if zi >= mask.shape[0]:
            continue
        sl = mask[zi]
        if sl[yi, xi]:
            return LOBE_LABELS.get(roi_id, roi_id)
        y0, y1 = max(0, yi - 1), min(rows, yi + 2)
        x0, x1 = max(0, xi - 1), min(cols, xi + 2)
        score = int(sl[y0:y1, x0:x1].sum())
        if score > best_score:
            best_score = score
            best_label = LOBE_LABELS.get(roi_id, roi_id)
    if best_score > 0:
        return best_label
    return locate_lobe_heuristic(cy, cx, rows, cols)


def lobe_hint_text(lobe_label: Optional[str]) -> Optional[str]:
    """位置特异性提示（参考性，非诊断）。"""
    if not lobe_label:
        return None
    if "上叶" in lobe_label:
        return "上叶病灶，结核/陈旧性病变相对多见（仅供参考）"
    if "中叶" in lobe_label:
        return "中叶病灶，请关注叶间裂邻近改变（仅供参考）"
    return None


def summarize_lobe_masks(lobe_masks: Dict[str, np.ndarray]) -> Dict[str, Any]:
    """统计各肺叶体素数，写入 meta.stats。"""
    if not lobe_masks:
        return {}
    return {
        roi: int(mask.sum())
        for roi, mask in lobe_masks.items()
    }
