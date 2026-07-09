"""GGO 区域分割（可插拔后端：启发式 / 自适应 / 深度学习模型）。"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
from scipy import ndimage
from skimage.measure import label, regionprops

from .hu_utils import extract_contour_normalized, ggo_candidate_mask, ggo_hu_window
from .lesion_enrichment import GGO_CIRCULARITY_MIN, GGO_MIN_AREA_MM2, smooth_slice_mask

logger = logging.getLogger(__name__)

MAX_GGO_REGIONS = 30


from .config import settings


def _backend_name() -> str:
    return (settings.scheme_b_ggo_backend or "off").lower().strip()


def _ggo_disabled() -> bool:
    return _backend_name() in ("off", "none", "disabled", "0", "false")


def _model_dir() -> Path:
    return Path(os.getenv("GGO_MODEL_DIR", "")).expanduser()


def is_ggo_model_ready() -> bool:
    d = _model_dir()
    if not d.is_dir():
        return False
    return (d / "model.pt").exists() or (d / "model.onnx").exists()


def _circularity(region) -> float:
    if region.area <= 0 or region.perimeter <= 0:
        return 0.0
    return float(4.0 * np.pi * region.area / (region.perimeter ** 2))


def _regions_from_volume_mask(
    ggo_vol: np.ndarray,
    volume: np.ndarray,
    spacing: Tuple[float, float, float],
    rows: int,
    cols: int,
    min_z_extent: int,
) -> List[Dict[str, Any]]:
    spacing_z, spacing_y, spacing_x = spacing
    pixel_area_mm2 = spacing_y * spacing_x
    labeled = label(ggo_vol)
    if labeled.max() == 0:
        return []

    regions: List[Dict[str, Any]] = []
    for region in regionprops(labeled):
        z0, y0, x0, z1, y1, x1 = region.bbox
        if (z1 - z0) < min_z_extent:
            continue
        vol_mm3 = float(region.area) * spacing_z * spacing_y * spacing_x
        if vol_mm3 < 15.0:
            continue

        best_z = z0
        best_area = 0
        for z in range(z0, z1):
            sl_area = int((labeled[z] == region.label).sum())
            if sl_area > best_area:
                best_area = sl_area
                best_z = z

        sl_mask = labeled[best_z] == region.label
        sl_mask = smooth_slice_mask(sl_mask)
        area_mm2 = float(sl_mask.sum()) * pixel_area_mm2
        if area_mm2 < GGO_MIN_AREA_MM2:
            continue

        labeled_sl = label(sl_mask)
        if labeled_sl.max() == 0:
            continue
        sl_region = regionprops(labeled_sl)[0]
        if _circularity(sl_region) < GGO_CIRCULARITY_MIN:
            continue

        yy, xx = np.where(sl_mask)
        min_row, max_row = int(yy.min()), int(yy.max()) + 1
        min_col, max_col = int(xx.min()), int(xx.max()) + 1
        crop = sl_mask[min_row:max_row, min_col:max_col]
        points = extract_contour_normalized(crop, min_row, min_col, rows, cols)
        if len(points) < 3:
            continue

        long_mm = max((max_col - min_col) * spacing_x, spacing_x)
        short_mm = max((max_row - min_row) * spacing_y, spacing_y)
        roi = volume[best_z, min_row:max_row, min_col:max_col]
        hu_mean = float(np.median(roi[crop])) if crop.any() else -500.0

        regions.append({
            "id": f"GGO{len(regions) + 1}",
            "sliceIndex": int(best_z),
            "points": points,
            "contour": points,
            "areaMm2": round(area_mm2, 1),
            "volumeMm3": round(vol_mm3, 1),
            "diameterMm": round((long_mm + short_mm) / 2.0, 1),
            "longAxisMm": round(long_mm, 1),
            "shortAxisMm": round(short_mm, 1),
            "huMean": round(hu_mean, 1),
            "ggoBackend": _backend_name(),
        })
        if len(regions) >= MAX_GGO_REGIONS:
            break
    return regions


def _detect_heuristic(
    volume: np.ndarray,
    lung_mask: np.ndarray,
    vessel_mask: np.ndarray | None,
    spacing: Tuple[float, float, float],
    rows: int,
    cols: int,
) -> List[Dict[str, Any]]:
    spacing_z = spacing[0]
    min_z = 1 if spacing_z >= 5.0 else 2
    ggo_vol = ggo_candidate_mask(lung_mask, volume, spacing_z)
    if vessel_mask is not None and vessel_mask.any():
        ggo_vol = ggo_vol & ~ndimage.binary_dilation(vessel_mask, iterations=1)
    ggo_vol = ndimage.binary_opening(ggo_vol, iterations=1)
    ggo_vol = ndimage.binary_closing(ggo_vol, iterations=1)
    return _regions_from_volume_mask(ggo_vol, volume, spacing, rows, cols, min_z)


def _detect_adaptive_local(
    volume: np.ndarray,
    lung_mask: np.ndarray,
    vessel_mask: np.ndarray | None,
    spacing: Tuple[float, float, float],
    rows: int,
    cols: int,
) -> List[Dict[str, Any]]:
    """局部 HU 自适应 GGO：比全局阈值更抗正常肺实质干扰。"""
    spacing_z = spacing[0]
    min_z = 1 if spacing_z >= 5.0 else 2
    ggo_lo, ggo_hi = ggo_hu_window(spacing_z)

    ggo_vol = np.zeros_like(lung_mask, dtype=bool)
    structure = np.ones((15, 15), dtype=bool)
    for z in range(volume.shape[0]):
        sl_hu = volume[z]
        sl_lung = lung_mask[z]
        if not sl_lung.any():
            continue
        local_mean = ndimage.generic_filter(
            sl_hu.astype(np.float32),
            np.mean,
            footprint=structure,
            mode="nearest",
        )
        adaptive = sl_lung & (sl_hu >= ggo_lo) & (sl_hu <= ggo_hi) & (sl_hu < local_mean - 25)
        ggo_vol[z] = adaptive

    if vessel_mask is not None and vessel_mask.any():
        ggo_vol = ggo_vol & ~ndimage.binary_dilation(vessel_mask, iterations=1)
    ggo_vol = ndimage.binary_opening(ggo_vol, iterations=1)
    ggo_vol = ndimage.binary_closing(ggo_vol, iterations=1)
    return _regions_from_volume_mask(ggo_vol, volume, spacing, rows, cols, min_z)


def _load_ggo_model_config(model_dir: Path) -> dict:
    import json
    cfg_path = model_dir / "config.json"
    if not cfg_path.exists():
        return {
            "input_size": [512, 512],
            "hu_min": -1024,
            "hu_max": 400,
            "threshold": 0.45,
            "input_name": "input",
            "output_name": "output",
        }
    with open(cfg_path, encoding="utf-8") as f:
        return json.load(f)


def _normalize_hu_slice(sl_hu: np.ndarray, hu_min: float, hu_max: float) -> np.ndarray:
    x = np.clip(sl_hu.astype(np.float32), hu_min, hu_max)
    return (x - hu_min) / max(hu_max - hu_min, 1e-6)


def _resize_slice(arr: np.ndarray, out_h: int, out_w: int) -> np.ndarray:
    from scipy.ndimage import zoom
    h, w = arr.shape
    if h == out_h and w == out_w:
        return arr
    return zoom(arr, (out_h / h, out_w / w), order=1)


def _infer_ggo_onnx_volume(
    session,
    config: dict,
    volume: np.ndarray,
    lung_mask: np.ndarray,
) -> np.ndarray:
    input_name = config.get("input_name", "input")
    output_name = config.get("output_name", "output")
    out_h, out_w = config.get("input_size", [512, 512])
    hu_min = float(config.get("hu_min", -1024))
    hu_max = float(config.get("hu_max", 400))
    thresh = float(config.get("threshold", 0.45))

    ggo_vol = np.zeros(volume.shape, dtype=bool)
    step = max(1, volume.shape[0] // int(os.getenv("GGO_MODEL_MAX_SLICES", "64")))

    for z in range(0, volume.shape[0], step):
        if not lung_mask[z].any():
            continue
        norm = _normalize_hu_slice(volume[z], hu_min, hu_max)
        inp = _resize_slice(norm, int(out_h), int(out_w))[None, None].astype(np.float32)
        out = session.run([output_name], {input_name: inp})[0]
        prob = out[0, 0] if out.ndim >= 3 else out[0]
        if prob.ndim == 3:
            prob = prob[0]
        mask = prob >= thresh
        mask_up = _resize_slice(mask.astype(np.float32), volume.shape[1], volume.shape[2]) > 0.5
        ggo_vol[z] = mask_up & lung_mask[z]

    return ggo_vol


def _detect_model(
    volume: np.ndarray,
    lung_mask: np.ndarray,
    vessel_mask: np.ndarray | None,
    spacing: Tuple[float, float, float],
    rows: int,
    cols: int,
) -> List[Dict[str, Any]]:
    """GGO 深度学习分割：优先 ONNX，其次 TorchScript，否则 adaptive。"""
    model_dir = _model_dir()
    onnx_path = model_dir / "model.onnx"
    ts_path = model_dir / "model.pt"
    config = _load_ggo_model_config(model_dir)
    spacing_z = spacing[0]
    min_z = 1 if spacing_z >= 5.0 else 2

    try:
        if onnx_path.exists():
            import onnxruntime as ort
            sess = ort.InferenceSession(
                str(onnx_path),
                providers=["CUDAExecutionProvider", "CPUExecutionProvider"],
            )
            ggo_vol = _infer_ggo_onnx_volume(sess, config, volume, lung_mask)
            backend_tag = "onnx"
        elif ts_path.exists():
            import torch
            model = torch.jit.load(str(ts_path), map_location="cpu")
            model.eval()
            ggo_vol = np.zeros(volume.shape, dtype=bool)
            out_h, out_w = config.get("input_size", [512, 512])
            hu_min = float(config.get("hu_min", -1024))
            hu_max = float(config.get("hu_max", 400))
            thresh = float(config.get("threshold", 0.45))
            with torch.no_grad():
                for z in range(volume.shape[0]):
                    if not lung_mask[z].any():
                        continue
                    norm = _normalize_hu_slice(volume[z], hu_min, hu_max)
                    inp = torch.from_numpy(
                        _resize_slice(norm, int(out_h), int(out_w))[None, None]
                    ).float()
                    out = model(inp)
                    prob = out.squeeze().detach().cpu().numpy()
                    mask = prob >= thresh
                    mask_up = _resize_slice(mask.astype(np.float32), rows, cols) > 0.5
                    ggo_vol[z] = mask_up & lung_mask[z]
            backend_tag = "torchscript"
        else:
            logger.warning("[GGO] 模型未就绪 (%s)，回退 adaptive", model_dir)
            return _detect_adaptive_local(volume, lung_mask, vessel_mask, spacing, rows, cols)

        if vessel_mask is not None and vessel_mask.any():
            ggo_vol = ggo_vol & ~ndimage.binary_dilation(vessel_mask, iterations=1)
        ggo_vol = ndimage.binary_opening(ggo_vol, iterations=1)
        ggo_vol = ndimage.binary_closing(ggo_vol, iterations=1)
        regions = _regions_from_volume_mask(ggo_vol, volume, spacing, rows, cols, min_z)
        for r in regions:
            r["ggoBackend"] = backend_tag
        if regions:
            return regions
        logger.info("[GGO] 模型推理无区域，回退 adaptive")
        return _detect_adaptive_local(volume, lung_mask, vessel_mask, spacing, rows, cols)
    except Exception as exc:
        logger.warning("[GGO] 模型推理失败: %s，回退 adaptive", exc)
        return _detect_adaptive_local(volume, lung_mask, vessel_mask, spacing, rows, cols)


def detect_ggo_regions(
    volume: np.ndarray,
    lung_mask: np.ndarray,
    vessel_mask: np.ndarray | None,
    spacing: Tuple[float, float, float],
    rows: int,
    cols: int,
) -> Tuple[List[Dict[str, Any]], str]:
    """统一 GGO 检测入口。返回 (regions, backend_used)。"""
    if _ggo_disabled():
        return [], "off"
    backend = _backend_name()
    if backend == "model" and is_ggo_model_ready():
        return _detect_model(volume, lung_mask, vessel_mask, spacing, rows, cols), "model"
    if backend == "heuristic":
        return _detect_heuristic(volume, lung_mask, vessel_mask, spacing, rows, cols), "heuristic"
    return _detect_adaptive_local(volume, lung_mask, vessel_mask, spacing, rows, cols), "adaptive"
