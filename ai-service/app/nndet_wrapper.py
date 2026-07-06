"""nnDetection LUNA16 肺结节检测封装。

为方案 B 提供 nnDetection 推理入口。当 NNDET_LUNA16_WEIGHT_DIR
指向有效的训练目录（含 plan_inference.pkl、config.yaml、*.ckpt）时，
通过 subprocess 调用 nnDetection 的 scripts/predict.py 完成全管线推理；
否则自动回退到 MONAI RetinaNet。

完整启用 nnDetection 需要的步骤：
1. 按 nnDetection 官方文档训练或下载 LUNA16 预训练权重
2. 确认训练目录结构：
   weight_dir/
   ├── plan_inference.pkl
   ├── config.yaml
   └── *.ckpt
3. 设置环境变量：
   export NNDET_LUNA16_WEIGHT_DIR=/path/to/weight_dir
   export NNDET_FOLD=0              # 可选，默认 0
   export NNDET_MODEL_NAME=RetinaUNetV0  # 可选

详见 docs/08-upgrade-roadmap.md P1 路径。
"""
from __future__ import annotations

import logging
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 可用性检查
# ---------------------------------------------------------------------------


def is_nndet_available() -> bool:
    """检查 nnDetection Python 包是否可导入。"""
    try:
        import nndet  # noqa: F401
        return True
    except ImportError:
        return False


def is_nndet_weights_ready() -> bool:
    """检查 nnDetection LUNA16 训练目录是否就绪。

    要求 NNDET_LUNA16_WEIGHT_DIR 指向的目录包含：
    - plan_inference.pkl（推理计划）
    - config.yaml（训练配置）
    - 至少一个 .ckpt 文件（模型权重）
    """
    weight_dir = _get_weight_dir()
    if weight_dir is None:
        return False
    plans = weight_dir / "plan_inference.pkl"
    config = weight_dir / "config.yaml"
    has_ckpt = any(weight_dir.glob("*.ckpt"))
    return plans.exists() and config.exists() and has_ckpt


def _get_weight_dir() -> Path | None:
    path = os.getenv("NNDET_LUNA16_WEIGHT_DIR", "")
    if not path:
        return None
    p = Path(path).expanduser().resolve()
    return p if p.is_dir() else None


def _get_fold() -> int:
    try:
        return int(os.getenv("NNDET_FOLD", "0"))
    except ValueError:
        return 0


def _get_model_name() -> str:
    return os.getenv("NNDET_MODEL_NAME", "RetinaUNetV0")


# ---------------------------------------------------------------------------
# 主推理入口
# ---------------------------------------------------------------------------


def detect_lesions_nndet(
    volume: np.ndarray,
    spacing: Tuple[float, float, float],
    rows: int,
    cols: int,
) -> Dict[str, Any]:
    """使用 nnDetection 进行肺结节检测。

    当权重就绪时通过 subprocess 调用 scripts/predict.py；
    否则回退到 MONAI RetinaNet。

    Args:
        volume: (Z, H, W) HU float32 体数据
        spacing: (z_spacing, y_spacing, x_spacing) mm
        rows, cols: 原始图像尺寸

    Returns:
        {"lesions": [...], "stats": {...}}
    """
    if not is_nndet_weights_ready():
        logger.info("[nnDetection] 权重未就绪，回退 MONAI RetinaNet")
        return _fallback_monai(volume, spacing, rows, cols)

    try:
        return _run_nndet_subprocess(volume, spacing, rows, cols)
    except Exception as exc:
        logger.error("[nnDetection] 推理失败: %s，回退 MONAI", exc)
        return _fallback_monai(volume, spacing, rows, cols)


# ---------------------------------------------------------------------------
# MONAI 回退
# ---------------------------------------------------------------------------


def _fallback_monai(
    volume: np.ndarray,
    spacing: Tuple[float, float, float],
    rows: int,
    cols: int,
) -> Dict[str, Any]:
    """回退到 MONAI RetinaNet 检测器。"""
    from .monai_nnunet_detector import detect_lesions_monai_nnunet

    result = detect_lesions_monai_nnunet(volume, spacing, rows, cols)
    result.setdefault("stats", {})["detector"] = "monai-retinanet (nnDetection fallback)"
    return result


# ---------------------------------------------------------------------------
# nnDetection subprocess 推理
# ---------------------------------------------------------------------------


def _run_nndet_subprocess(
    volume: np.ndarray,
    spacing: Tuple[float, float, float],
    rows: int,
    cols: int,
) -> Dict[str, Any]:
    """通过 subprocess 调用 nnDetection predict.py 完成推理。"""
    import nibabel as nib

    weight_dir = _get_weight_dir()
    fold = _get_fold()
    model_name = _get_model_name()

    # 推导 nnDetection 目录结构
    nndet_root = Path(__file__).resolve().parent.parent / "third_party" / "nnDetection"
    predict_script = nndet_root / "scripts" / "predict.py"
    if not predict_script.exists():
        raise RuntimeError(f"nnDetection predict.py 不存在: {predict_script}")

    # 从 weight_dir 推导任务名（向上两级应包含 Task016_Luna）
    task_name = weight_dir.parent.parent.name if weight_dir.parent.parent.name.startswith("Task") else "Task016_Luna"
    models_root = weight_dir.parent.parent.parent  # 含 Task016_Luna 的目录

    # 写 NIfTI 到临时目录
    with tempfile.TemporaryDirectory(prefix="nndet_data_") as data_tmp:
        data_dir = Path(data_tmp) / task_name
        images_dir = data_dir / "imagesTs"
        images_dir.mkdir(parents=True, exist_ok=True)

        nii_path = images_dir / "ct_001.nii.gz"
        _write_nifti(volume, spacing, nii_path)

        # 设置环境变量
        env = os.environ.copy()
        env["det_models"] = str(models_root)
        env["det_data"] = str(data_dir)
        env["det_prep"] = str(data_dir)
        # 抑制 nnDetection 内部可能触发的 CUDA_VISIBLE_DEVICES 限制
        env.setdefault("CUDA_VISIBLE_DEVICES", "0")

        # 确保 nndet_root 在 PYTHONPATH 中
        pythonpath = str(nndet_root)
        if "PYTHONPATH" in env:
            env["PYTHONPATH"] = f"{pythonpath}:{env['PYTHONPATH']}"
        else:
            env["PYTHONPATH"] = pythonpath

        cmd = [
            sys.executable,
            str(predict_script),
            task_name,
            model_name,
            "-f", str(fold),
            "--no_preprocess",  # predict.py 中为 store_false → process=False
            "--force_args",     # 允许覆盖 config 中的 task/fold
        ]

        logger.info("[nnDetection] 启动推理: %s", " ".join(cmd))
        logger.info("[nnDetection] det_models=%s det_data=%s", models_root, data_dir)

        result = subprocess.run(
            cmd,
            cwd=str(nndet_root),
            env=env,
            capture_output=True,
            text=True,
            timeout=600,  # 10 分钟超时
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"nnDetection 推理返回非零 exit code {result.returncode}\n"
                f"STDERR:\n{result.stderr[-2000:]}\n"
                f"STDOUT:\n{result.stdout[-2000:]}"
            )

        # 解析输出
        training_dir = _find_training_dir(weight_dir, fold)
        pred_dir = training_dir / "test_predictions"
        return _parse_nndet_output(pred_dir, volume, spacing, rows, cols)


def _find_training_dir(weight_dir: Path, fold: int) -> Path:
    """查找实际训练目录（可能包含 fold 子目录）。"""
    # 如果 weight_dir 直接就是训练目录
    if (weight_dir / "plan_inference.pkl").exists():
        return weight_dir

    # 查找 fold 子目录
    from nndet.io.paths import get_training_dir
    return get_training_dir(weight_dir, fold)


def _parse_nndet_output(
    pred_dir: Path,
    volume: np.ndarray,
    spacing: Tuple[float, float, float],
    rows: int,
    cols: int,
) -> Dict[str, Any]:
    """解析 nnDetection 的预测输出 pickle 文件。"""
    from .chest_detector import _extract_contour, _lesion_type, _confidence
    from .config import settings

    # nnDetection 输出: {case_id}_boxes.pkl 包含
    #   pred_boxes: (N, 6) z1,y1,x1,z2,y2,x2 世界坐标
    #   pred_scores: (N,) 置信度
    #   pred_labels: (N,) 类别标签
    box_files = list(pred_dir.glob("*_boxes.pkl"))
    if not box_files:
        logger.warning("[nnDetection] 未找到预测输出文件")
        return {"lesions": [], "stats": {"reason": "NO_PREDICTION_FILE"}}

    try:
        from nndet.io.load import load_pickle
    except ImportError:
        import pickle as _pickle

        def load_pickle(p):
            with open(p, "rb") as f:
                return _pickle.load(f)

    all_lesions: List[Dict[str, Any]] = []
    spacing_z, spacing_y, spacing_x = spacing

    for bf in box_files:
        pred = load_pickle(bf)
        boxes = pred.get("pred_boxes", np.array([]).reshape(0, 6))
        scores = pred.get("pred_scores", np.array([]))
        labels = pred.get("pred_labels", np.array([]))

        # 获取原始图像信息用于坐标映射
        orig_shape = pred.get("original_size_of_raw_data", volume.shape)
        itk_spacing = pred.get("itk_spacing", spacing)
        itk_origin = pred.get("itk_origin", (0, 0, 0))

        for i in range(len(boxes)):
            if i >= settings.max_lesions:
                break

            score = float(scores[i])
            if score < 0.05:  # 至少 5% 置信度
                continue

            box = boxes[i]  # (z1, y1, x1, z2, y2, x2)
            z1, y1, x1, z2, y2, x2 = box[:6]

            # 映射到图像像素坐标
            min_z = int(max(0, min(volume.shape[0] - 1, round(z1))))
            max_z = int(max(min_z + 1, min(volume.shape[0], round(z2))))
            min_y = int(max(0, min(rows - 1, round(y1))))
            max_y = int(max(min_y + 1, min(rows, round(y2))))
            min_x = int(max(0, min(cols - 1, round(x1))))
            max_x = int(max(min_x + 1, min(cols, round(x2))))

            slice_index = (min_z + max_z) // 2
            if slice_index < 0 or slice_index >= volume.shape[0]:
                continue

            # HU 均值
            roi = volume[slice_index, min_y:max_y, min_x:max_x]
            mean_hu = float(roi.mean()) if roi.size else -50.0
            lesion_type, label_cn = _lesion_type(mean_hu)

            long_axis = max(
                (max_x - min_x) * spacing_x,
                (max_y - min_y) * spacing_y,
                (max_z - min_z) * spacing_z,
            )
            short_axis = min(
                max((max_x - min_x) * spacing_x, spacing_x),
                max((max_y - min_y) * spacing_y, spacing_y),
                max((max_z - min_z) * spacing_z, spacing_z),
            )
            diameter_mm = (long_axis + short_axis) / 2.0
            if diameter_mm < settings.min_nodule_mm or diameter_mm > settings.max_nodule_mm:
                continue

            bbox = {
                "x": float(min_x) / cols,
                "y": float(min_y) / rows,
                "width": float(max(1, max_x - min_x)) / cols,
                "height": float(max(1, max_y - min_y)) / rows,
            }

            sl_mask = np.zeros((rows, cols), dtype=bool)
            sl_mask[min_y:max_y, min_x:max_x] = True
            contour = _extract_contour(sl_mask, 0, 0, rows, cols)
            area_mm2 = float((max_x - min_x) * (max_y - min_y)) * spacing_y * spacing_x
            solidity = 0.85  # nnDetection 不提供 solidity，给默认值

            all_lesions.append({
                "id": f"N{i + 1}",
                "label": label_cn,
                "type": lesion_type,
                "confidence": round(min(max(score, 0.05), 0.99), 3),
                "sliceIndex": int(slice_index),
                "bbox": bbox,
                "contour": contour,
                "diameterMm": round(diameter_mm, 1),
                "longAxisMm": round(long_axis, 1),
                "shortAxisMm": round(short_axis, 1),
                "areaMm2": round(area_mm2, 1),
                "volumeMm3": round(area_mm2 * spacing_z, 1),
                "hu": round(mean_hu, 1),
            })

    all_lesions.sort(key=lambda x: x["confidence"], reverse=True)
    return {
        "lesions": all_lesions[: settings.max_lesions],
        "stats": {
            "candidates": len(all_lesions),
            "lesionCount": len(all_lesions[: settings.max_lesions]),
            "detector": "nndetection",
        },
    }


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------


def _write_nifti(
    volume: np.ndarray,
    spacing: Tuple[float, float, float],
    path: Path,
) -> None:
    """写入 NIfTI 文件（nnDetection 使用 LPS 坐标系）。"""
    import nibabel as nib

    spacing_z, spacing_y, spacing_x = spacing
    data = np.ascontiguousarray(volume.transpose(2, 1, 0).astype(np.float32))
    affine = np.array(
        [
            [spacing_x, 0, 0, 0],
            [0, spacing_y, 0, 0],
            [0, 0, spacing_z, 0],
            [0, 0, 0, 1],
        ],
        dtype=np.float64,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    nib.save(nib.Nifti1Image(data, affine), str(path))
