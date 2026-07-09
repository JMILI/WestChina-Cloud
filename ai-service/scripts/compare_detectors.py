#!/usr/bin/env python3
"""方案 B 检测器 A/B 对比（MONAI vs nnDetection，3-P2-03）。"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _load_volume(nii: str | None, cache_study: str | None, cache_series: str | None, image_count: int):
    if nii:
        import nibabel as nib
        img = nib.load(nii)
        data = img.get_fdata().astype(np.float32)
        if data.ndim == 4:
            data = data[..., 0]
        vol = data.transpose(2, 1, 0)
        spacing = tuple(float(s) for s in img.header.get_zooms()[:3][::-1])
        rows, cols = vol.shape[1], vol.shape[2]
        return vol, spacing, rows, cols

    if cache_study and cache_series:
        from app.volume_cache import try_load_cached_volume
        meta = try_load_cached_volume(cache_study, cache_series, image_count)
        if meta is None:
            raise RuntimeError("体数据缓存未命中，请先跑一次 scheme-b 或提供 --nii")
        return meta.volume, meta.spacing, meta.rows, meta.cols

    raise RuntimeError("请指定 --nii 或 --study-uid + --series-uid + --image-count")


def _run_detector(name: str, volume, spacing, rows, cols) -> dict:
    t0 = time.time()
    if name == "monai":
        from app.monai_bundle_manager import is_monai_available, is_monai_bundle_ready
        if not (is_monai_available() and is_monai_bundle_ready()):
            return {"ok": False, "reason": "MONAI bundle 未就绪"}
        from app.monai_nnunet_detector import detect_lesions_monai_nnunet
        out = detect_lesions_monai_nnunet(volume, spacing, rows, cols)
    elif name == "nndet":
        from app.nndet_wrapper import is_nndet_available, is_nndet_weights_ready, detect_lesions_nndet
        if not (is_nndet_available() and is_nndet_weights_ready()):
            return {"ok": False, "reason": "nnDetection 权重未就绪"}
        out = detect_lesions_nndet(volume, spacing, rows, cols)
    else:
        raise ValueError(name)

    elapsed = time.time() - t0
    lesions = out.get("lesions") or []
    low = out.get("lowConfLesions") or []
    return {
        "ok": True,
        "elapsedSec": round(elapsed, 2),
        "lesionCount": len(lesions),
        "lowConfCount": len(low),
        "stats": out.get("stats") or {},
        "topLesions": lesions[:5],
    }


def _iou(a: dict, b: dict) -> float:
    ax, ay, aw, ah = a.get("x", 0), a.get("y", 0), a.get("width", 0), a.get("height", 0)
    bx, by, bw, bh = b.get("x", 0), b.get("y", 0), b.get("width", 0), b.get("height", 0)
    x1 = max(ax, bx)
    y1 = max(ay, by)
    x2 = min(ax + aw, bx + bw)
    y2 = min(ay + ah, by + bh)
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    union = aw * ah + bw * bh - inter
    return inter / union if union > 0 else 0.0


def _compare_overlap(a_lesions: list, b_lesions: list, threshold: float = 0.3) -> dict:
    matched = 0
    for la in a_lesions:
        for lb in b_lesions:
            if la.get("sliceIndex") != lb.get("sliceIndex"):
                continue
            if _iou(la.get("bbox") or {}, lb.get("bbox") or {}) >= threshold:
                matched += 1
                break
    return {
        "aCount": len(a_lesions),
        "bCount": len(b_lesions),
        "matchedPairs": matched,
        "iouThreshold": threshold,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Scheme B detector A/B compare")
    parser.add_argument("--nii", help="NIfTI 体数据路径")
    parser.add_argument("--study-uid")
    parser.add_argument("--series-uid")
    parser.add_argument("--image-count", type=int, default=0)
    parser.add_argument("--out", help="JSON 输出路径（默认 logs/ai-service/reports/）")
    args = parser.parse_args()

    from app.log_paths import ai_reports_dir

    if not args.out:
        ai_reports_dir().mkdir(parents=True, exist_ok=True)
        args.out = str(ai_reports_dir() / f"compare_{int(time.time())}.json")

    volume, spacing, rows, cols = _load_volume(
        args.nii, args.study_uid, args.series_uid, args.image_count,
    )
    print(f"Volume shape={volume.shape} spacing={spacing}")

    report = {"shape": list(volume.shape), "spacing": list(spacing), "detectors": {}}
    for name in ("monai", "nndet"):
        print(f"\n--- {name} ---")
        result = _run_detector(name, volume, spacing, rows, cols)
        report["detectors"][name] = result
        if result.get("ok"):
            print(f"  lesions={result['lesionCount']} low={result['lowConfCount']} "
                  f"time={result['elapsedSec']}s")
        else:
            print(f"  skip: {result.get('reason')}")

    monai_l = (report["detectors"].get("monai") or {}).get("topLesions") or []
    nndet_l = (report["detectors"].get("nndet") or {}).get("topLesions") or []
    if monai_l and nndet_l:
        report["overlap"] = _compare_overlap(monai_l, nndet_l)
        print(f"\nOverlap: {report['overlap']}")

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\nReport saved: {args.out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
