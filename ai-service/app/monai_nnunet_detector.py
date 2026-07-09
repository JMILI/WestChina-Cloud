"""MONAI RetinaNet (LUNA16 预训练) 肺结节检测。"""
from __future__ import annotations

import logging
import os
import sys
from .log_paths import ai_temp_directory
import time
from typing import Any, Dict, List, Tuple

import numpy as np

from .chest_detector import _extract_contour, _lesion_type
from .config import settings
from .monai_bundle_manager import ensure_monai_bundle, is_monai_available

logger = logging.getLogger(__name__)

# 与 bundle inference.json 中 detector score_thresh 对齐
SCORE_THRESH = float(os.getenv("MONAI_SCORE_THRESH", "0.12"))
LOW_SCORE_MIN = float(os.getenv("SCHEME_B_LOW_CONF_MIN", "0.01"))
LOW_SCORE_MAX = float(os.getenv("SCHEME_B_LOW_CONF_MAX", "0.05"))
TARGET_SPACING = (0.703125, 0.703125, 1.25)
# Z 轴最大层数：超过此值时沿 Z 均匀降采样，避免 Spacingd OOM/超时
MAX_Z_SLICES = 200


def _pred_box_count(pred: Dict[str, Any]) -> int:
    boxes = pred.get("box")
    if boxes is None:
        return 0
    try:
        import torch
        if isinstance(boxes, torch.Tensor):
            if boxes.numel() == 0:
                return 0
            return int(boxes.shape[0]) if boxes.ndim > 1 else 1
    except Exception:
        pass
    try:
        return len(boxes)
    except Exception:
        return 0


def _iter_pred_boxes(boxes) -> List[Any]:
    if boxes is None:
        return []
    try:
        import torch
        if isinstance(boxes, torch.Tensor):
            if boxes.numel() == 0:
                return []
            if boxes.ndim == 1:
                return [boxes]
            return [boxes[i] for i in range(boxes.shape[0])]
    except Exception:
        pass
    if isinstance(boxes, (list, tuple)):
        return list(boxes)
    return [boxes]


def _write_nifti(volume: np.ndarray, spacing: Tuple[float, float, float], path: str) -> None:
    import nibabel as nib
    spacing_z, spacing_y, spacing_x = spacing
    data = np.ascontiguousarray(volume.transpose(2, 1, 0).astype(np.float32))
    affine = np.array([
        [spacing_x, 0, 0, 0],
        [0, spacing_y, 0, 0],
        [0, 0, spacing_z, 0],
        [0, 0, 0, 1],
    ], dtype=np.float64)
    nib.save(nib.Nifti1Image(data, affine), path)


def _load_monai_detector(bundle_dir):
    import torch
    from monai.bundle import ConfigParser
    bundle_dir = str(bundle_dir)
    if bundle_dir not in sys.path:
        sys.path.insert(0, bundle_dir)
    parser = ConfigParser()
    parser.read_config(os.path.join(bundle_dir, "configs", "inference.json"))
    parser["bundle_root"] = bundle_dir
    parser["whether_raw_luna16"] = True
    parser["whether_resampled_luna16"] = False
    device = parser.get_parsed_content("device")
    for op in parser.get_parsed_content("detector_ops"):
        if op is not None:
            op
    network = parser.get_parsed_content("network")
    detector = parser.get_parsed_content("detector")
    inferer = parser.get_parsed_content("inferer")
    ckpt_path = os.path.join(bundle_dir, "models", "model.pt")
    ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
    state_dict = ckpt["model"] if isinstance(ckpt, dict) and "model" in ckpt else ckpt
    network.load_state_dict(state_dict, strict=False)
    network.eval()
    return network, detector, inferer, device, torch


def _normalize_pred_boxes(pred: Dict[str, Any], image) -> Dict[str, Any]:
    from monai.data.box_utils import convert_box_mode
    import torch
    if not pred or pred.get("box") is None:
        return pred
    boxes = pred.get("box")
    if not isinstance(boxes, torch.Tensor):
        boxes = torch.as_tensor(boxes, dtype=torch.float32)
    if boxes.numel() == 0:
        return pred
    if boxes.ndim == 1:
        boxes = boxes.unsqueeze(0)
    shape = tuple(int(s) for s in image.shape[1:])
    max_dim = max(shape) if shape else 512
    sample = boxes[0].tolist()
    if len(sample) >= 6:
        _, _, _, w, h, d = sample[:6]
        if max(w, h, d) < max_dim * 0.25:
            return {**pred, "box": boxes}
    try:
        from monai.transforms import ClipBoxToImaged, ConvertBoxModed, Compose
        post = Compose([
            ClipBoxToImaged(box_keys="box", label_keys="label",
                            box_ref_image_keys="image", remove_empty=True),
            ConvertBoxModed(box_keys="box", src_mode="xyzxyz", dst_mode="cccwhd"),
        ])
        return post({**pred, "box": boxes, "image": image})
    except Exception as exc:
        logger.warning("[MONAI] ClipBox 后处理失败，直接 convert_box_mode: %s", exc)
    converted = convert_box_mode(boxes, src_mode="xyzxyz", dst_mode="cccwhd")
    return {**pred, "box": converted}


def _run_monai_inference(nii_path: str, bundle_dir):
    import torch
    from monai.transforms import (
        Compose, EnsureChannelFirstd, EnsureTyped, LoadImaged,
        Orientationd, ScaleIntensityRanged, Spacingd,
    )
    t0 = time.time()
    network, detector, inferer, device, torch_mod = _load_monai_detector(bundle_dir)
    logger.info("[MONAI] 模型加载完成 (%.1fs)，开始预处理…", time.time() - t0)

    t1 = time.time()
    preprocessing = Compose([
        LoadImaged(keys="image", reader="ITKReader", affine_lps_to_ras=True),
        EnsureChannelFirstd(keys="image"),
        Orientationd(keys="image", axcodes="RAS"),
        Spacingd(keys="image", pixdim=list(TARGET_SPACING), mode="bilinear"),
        ScaleIntensityRanged(keys="image", a_min=-1024.0, a_max=300.0,
                             b_min=0.0, b_max=1.0, clip=True),
        EnsureTyped(keys="image"),
    ])
    data = preprocessing({"image": nii_path})
    image = data["image"].to(device)
    logger.info("[MONAI] 预处理完成 (%.1fs)，resampled shape=%s，开始 GPU 推理…",
                time.time() - t1, tuple(image.shape))
    if image.ndim != 4:
        raise RuntimeError(f"MONAI 输入维度异常: {tuple(image.shape)}，期望 (C, D, H, W)")

    t2 = time.time()
    try:
        with torch_mod.no_grad():
            with torch_mod.amp.autocast("cuda", enabled=(device.type == "cuda")):
                outputs = inferer([image], network)
    except torch.cuda.OutOfMemoryError:
        logger.error("[MONAI] CUDA OOM！volume 过大，请减小 MAX_Z_SLICES 或使用 CPU")
        raise RuntimeError(
            "GPU 显存不足。请尝试 CPU 模式或减少序列层数。"
            f"当前 resampled shape={tuple(image.shape)}"
        )
    logger.info("[MONAI] GPU 推理完成 (%.1fs)，开始后处理…", time.time() - t2)

    pred = outputs[0] if isinstance(outputs, list) else outputs
    pred = _normalize_pred_boxes(pred, image)
    return pred, data["image"].meta, tuple(image.shape[1:])


def _resampled_voxel_to_original(
    center_zyx: Tuple[float, float, float],
    resampled_shape: Tuple[int, int, int],
    original_shape: Tuple[int, int, int],
    original_spacing: Tuple[float, float, float],
) -> Tuple[int, int, int]:
    spacing_z, spacing_y, spacing_x = original_spacing
    res_z, res_y, res_x = resampled_shape
    orig_z, orig_y, orig_x = original_shape
    phys_z = center_zyx[0] * TARGET_SPACING[2]
    phys_y = center_zyx[1] * TARGET_SPACING[1]
    phys_x = center_zyx[2] * TARGET_SPACING[0]
    oz = int(round(phys_z / max(spacing_z, 1e-6)))
    oy = int(round(phys_y / max(spacing_y, 1e-6)))
    ox = int(round(phys_x / max(spacing_x, 1e-6)))
    oz = max(0, min(orig_z - 1, oz))
    oy = max(0, min(orig_y - 1, oy))
    ox = max(0, min(orig_x - 1, ox))
    return oz, oy, ox


def _tensor_to_numpy(val) -> np.ndarray:
    """CUDA tensor → numpy（MONAI 推理后 box/score 常在 GPU 上）。"""
    try:
        import torch
        if isinstance(val, torch.Tensor):
            return val.detach().cpu().numpy()
    except Exception:
        pass
    return np.asarray(val, dtype=np.float64)


def _scores_list(scores) -> List[float]:
    if scores is None:
        return []
    try:
        import torch
        if isinstance(scores, torch.Tensor):
            arr = scores.detach().cpu().numpy().reshape(-1)
            return [float(x) for x in arr]
    except Exception:
        pass
    try:
        return [float(x) for x in scores]
    except Exception:
        return []


def _boxes_to_lesions(
    pred: Dict[str, Any], volume: np.ndarray,
    spacing: Tuple[float, float, float], rows: int, cols: int,
    resampled_shape: Tuple[int, int, int],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    boxes = pred.get("box")
    scores = pred.get("label_scores")
    box_list = _iter_pred_boxes(boxes)
    if not box_list:
        return [], []
    score_list = _scores_list(scores)
    lesions: List[Dict[str, Any]] = []
    low_conf: List[Dict[str, Any]] = []
    spacing_z, spacing_y, spacing_x = spacing
    orig_z, orig_y, orig_x = volume.shape

    for idx, box in enumerate(box_list):
        score = score_list[idx] if idx < len(score_list) else 0.5
        is_low = LOW_SCORE_MIN <= score < LOW_SCORE_MAX
        if score < LOW_SCORE_MIN:
            continue
        if score < SCORE_THRESH and not is_low:
            continue
        arr = _tensor_to_numpy(box).reshape(-1)
        if arr.size < 6:
            continue
        cx, cy, cz, w, h, d = arr[:6]
        z1 = max(0, cz - d / 2)
        z2 = min(resampled_shape[0], cz + d / 2)
        y1 = max(0, cy - h / 2)
        y2 = min(resampled_shape[1], cy + h / 2)
        x1 = max(0, cx - w / 2)
        x2 = min(resampled_shape[2], cx + w / 2)
        slice_index, oy, ox = _resampled_voxel_to_original(
            (cz, cy, cx), resampled_shape, volume.shape, spacing)
        sy = spacing_y / TARGET_SPACING[1]
        sx = spacing_x / TARGET_SPACING[0]
        min_y = int(max(0, min(rows - 1, round(y1 * sy))))
        max_y = int(max(min_y + 2, min(rows, round(y2 * sy))))
        min_x = int(max(0, min(cols - 1, round(x1 * sx))))
        max_x = int(max(min_x + 2, min(cols, round(x2 * sx))))
        sl_mask = np.zeros((rows, cols), dtype=bool)
        sl_mask[min_y:max_y, min_x:max_x] = True
        roi = volume[slice_index, min_y:max_y, min_x:max_x]
        mean_hu = float(roi.mean()) if roi.size else -50.0
        hu_min = float(roi.min()) if roi.size else mean_hu
        hu_max = float(roi.max()) if roi.size else mean_hu
        lesion_type, label_cn = _lesion_type(mean_hu)
        long_axis = max((max_x - min_x) * spacing_x, (max_y - min_y) * spacing_y,
                        d * TARGET_SPACING[2])
        short_axis = min((max_x - min_x) * spacing_x, (max_y - min_y) * spacing_y,
                         d * TARGET_SPACING[2])
        diameter_mm = (long_axis + short_axis) / 2.0
        if diameter_mm < settings.min_nodule_mm or diameter_mm > settings.max_nodule_mm:
            continue
        bbox = {
            "x": float(min_x) / cols, "y": float(min_y) / rows,
            "width": float(max(1, max_x - min_x)) / cols,
            "height": float(max(1, max_y - min_y)) / rows,
        }
        contour = _extract_contour(sl_mask, 0, 0, rows, cols)
        area_mm2 = float(sl_mask.sum()) * spacing_y * spacing_x
        entry = {
            "id": f"M{idx + 1}", "label": label_cn, "type": lesion_type,
            "confidence": round(min(max(score, 0.05), 0.99), 3),
            "detectionConfidence": round(min(max(score, 0.05), 0.99), 3),
            "sliceIndex": int(slice_index), "bbox": bbox, "contour": contour,
            "diameterMm": round(diameter_mm, 1), "longAxisMm": round(long_axis, 1),
            "shortAxisMm": round(short_axis, 1), "areaMm2": round(area_mm2, 1),
            "volumeMm3": round(area_mm2 * spacing_z, 1), "hu": round(mean_hu, 1),
            "huMean": round(mean_hu, 1), "huMin": round(hu_min, 1), "huMax": round(hu_max, 1),
            "source": "dl_low" if is_low else "dl_high",
        }
        if is_low:
            low_conf.append(entry)
        else:
            lesions.append(entry)
    lesions.sort(key=lambda x: x["confidence"], reverse=True)
    low_conf.sort(key=lambda x: x["confidence"], reverse=True)
    return lesions[: settings.max_lesions], low_conf[: settings.max_lesions]


def detect_lesions_monai_nnunet(
    volume: np.ndarray, spacing: Tuple[float, float, float],
    rows: int, cols: int,
) -> Dict[str, Any]:
    if not is_monai_available():
        raise RuntimeError("MONAI / PyTorch 未安装")
    bundle_dir = ensure_monai_bundle()

    original_z = int(volume.shape[0])
    z_subsampled = False
    max_z = settings.scheme_b_monai_max_z

    if original_z > max_z:
        logger.info("[MONAI] Z轴降采样 %d → %d 层", original_z, max_z)
        indices = np.linspace(0, original_z - 1, max_z, dtype=int)
        indices = np.unique(indices)
        volume = volume[indices]
        spacing = (spacing[0] * original_z / len(indices), spacing[1], spacing[2])
        z_subsampled = True

    logger.info("[MONAI] 开始 RetinaNet 推理, shape=%s, spacing=%.2f×%.2f×%.2f",
                volume.shape, spacing[0], spacing[1], spacing[2])

    with ai_temp_directory("monai_nodule_") as tmp:
        nii_path = os.path.join(tmp, "ct.nii.gz")
        _write_nifti(volume, spacing, nii_path)
        pred, _meta, res_shape = _run_monai_inference(nii_path, bundle_dir)

    lesions, low_conf = _boxes_to_lesions(pred, volume, spacing, rows, cols, res_shape)
    lung_mask = volume < -400
    stats = {
        "candidates": _pred_box_count(pred),
        "lesionCount": len(lesions),
        "lowConfCount": len(low_conf),
        "lungVoxels": int(lung_mask.sum()),
        "volumeShape": [int(volume.shape[0]), rows, cols],
    }
    if z_subsampled:
        stats["zSubsampled"] = True
        stats["zOriginalSlices"] = original_z
    return {"lesions": lesions, "lowConfLesions": low_conf, "stats": stats}
