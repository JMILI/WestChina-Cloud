#!/usr/bin/env python3
"""端到端测试：MinIO 上传 + 三方案 detectLesion/stream。

用法:
    cd ai-service
    PYTHONPATH=. python scripts/e2e_detect_test.py \\
        ../ct_file/翁倩/翁倩/20210819000536

环境变量:
    AI_BASE_URL=http://127.0.0.1:9810
    MINIO_BUCKET=superadmin
    E2E_MAX_SLICES=64          # 上传与全序列测试层数上限
    E2E_SLICE_INDEX=180        # 单层测试层（肺野较大）
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.schemas import DetectLesionRequest

# 复用上传逻辑
from scripts.upload_dicom_to_minio import prepare_sorted_datasets, upload_series


AI_BASE = os.getenv("AI_BASE_URL", "http://127.0.0.1:9810")
BUCKET = os.getenv("MINIO_BUCKET", "superadmin")
MAX_SLICES = int(os.getenv("E2E_MAX_SLICES", "64"))
SLICE_INDEX = int(os.getenv("E2E_SLICE_INDEX", "180"))


def stream_detect(payload: dict) -> tuple[dict | None, list[dict], str | None]:
    """POST /detectLesion/stream，解析 SSE。"""
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{AI_BASE}/detectLesion/stream",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    events: list[dict] = []
    result = None
    error = None

    try:
        with urllib.request.urlopen(req, timeout=1800) as resp:
            buffer = ""
            while True:
                chunk = resp.read(4096)
                if not chunk:
                    break
                buffer += chunk.decode("utf-8", errors="replace")
                while "\n\n" in buffer:
                    block, buffer = buffer.split("\n\n", 1)
                    for line in block.splitlines():
                        if not line.startswith("data:"):
                            continue
                        data = json.loads(line[5:].strip())
                        events.append(data)
                        if data.get("type") == "result":
                            result = data.get("data")
                        if data.get("type") == "error":
                            error = data.get("message") or data.get("code")
    except urllib.error.HTTPError as exc:
        error = f"HTTP {exc.code}: {exc.read().decode()[:500]}"
    except Exception as exc:
        error = str(exc)

    return result, events, error


def count_event_types(events: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for ev in events:
        t = ev.get("type", "?")
        counts[t] = counts.get(t, 0) + 1
    return counts


def run_case(name: str, payload: dict) -> bool:
    print(f"\n{'='*60}\n[CASE] {name}\n{'='*60}")
    t0 = time.time()
    result, events, error = stream_detect(payload)
    elapsed = time.time() - t0
    types = count_event_types(events)
    print(f"  事件: {types}")
    print(f"  耗时: {elapsed:.1f}s")

    if error:
        print(f"  ❌ 失败: {error}")
        return False
    if not result:
        print("  ❌ 未收到 result")
        return False

    lesions = result.get("lesions") or []
    overlay = result.get("overlayType", "bbox")
    screening = result.get("screening")
    heatmap = result.get("heatmap")
    stats = (result.get("meta") or {}).get("stats") or {}

    print(f"  engine={result.get('engine')} overlay={overlay}")
    print(f"  lesions={len(lesions)}")
    if screening:
        print(f"  screening={screening.get('label')} conf={screening.get('confidence')}")
    if heatmap:
        print(f"  heatmap={heatmap.get('width')}x{heatmap.get('height')}")
    if stats.get("reason"):
        print(f"  reason={stats.get('reason')}: {stats.get('message', '')}")
    if stats.get("subsample"):
        print(f"  subsample={stats['subsample']}")

    # 方案 C 验收：无 bbox，有热力图
    if payload.get("detectEngine") == "scheme-c":
        ok = overlay == "heatmap" and len(lesions) == 0 and heatmap is not None
        print("  ✅ 通过" if ok else "  ❌ 方案C应有热力图且无病灶框")
        return ok

    # 方案 B：融合精准分析验收清单
    if payload.get("detectEngine") == "scheme-b":
        src = stats.get("candidate_source")
        ggo_n = len(result.get("ggoRegions") or [])
        overlay_ok = overlay == "bbox" or stats.get("legacyGgoMode")
        ggo_ok = ggo_n == 0 or stats.get("legacyGgoMode")
        fields_ok = True
        if lesions:
            sample = lesions[0]
            for key in ("huMean", "detectionConfidence", "colorKey", "markerType"):
                if key not in sample:
                    fields_ok = False
                    break
        disclaimer_ok = "不能替代" in (result.get("disclaimer") or "")
        print(f"  candidate_source={src} ggo_regions={ggo_n} ggoBackend={stats.get('ggoBackend')}")
        print(f"  overlay={overlay} fields_ok={fields_ok} disclaimer_ok={disclaimer_ok}")
        if src:
            ok = overlay_ok and ggo_ok and fields_ok and disclaimer_ok
        elif stats.get("reason") in (
            "GPU_UNAVAILABLE", "DETECTOR_UNAVAILABLE", "NNDET_UNAVAILABLE"
        ):
            ok = True
        else:
            ok = result is not None and disclaimer_ok
        print("  ✅ 通过" if ok else "  ❌ 方案B验收未通过")
        save_path = os.getenv("E2E_SAVE_RESULT", "")
        if save_path and result:
            with open(save_path, "w", encoding="utf-8") as fh:
                json.dump(result, fh, ensure_ascii=False, indent=2)
            print(f"  结果已保存: {save_path}")
        return ok

    print("  ✅ 完成")
    return True


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    dicom_dir = sys.argv[1]
    print(f"E2E 测试目录: {dicom_dir}")
    print(f"AI={AI_BASE} bucket={BUCKET} max_slices={MAX_SLICES}")

    datasets, meta = prepare_sorted_datasets(dicom_dir, MAX_SLICES if MAX_SLICES > 0 else None)
    slice_index = min(SLICE_INDEX, meta["imageCount"] - 1)
    print(f"上传 {meta['imageCount']} 层…")
    meta = upload_series(datasets, meta, BUCKET, dry_run=False)

    base = {
        "bucket": meta["bucket"],
        "studyUid": meta["studyUid"],
        "seriesUid": meta["seriesUid"],
        "imageCount": meta["imageCount"],
        "bodyPart": meta["bodyPart"] or "CHEST",
    }

    passed = 0
    total = 0

    # scheme-a single
    total += 1
    if run_case(
        "scheme-a 当前层",
        {
            **base,
            "detectEngine": "scheme-a",
            "detectMode": "single",
            "detect_mode": "single",
            "singleSlice": True,
            "sliceIndex": slice_index,
            "currentSliceIndex": slice_index,
        },
    ):
        passed += 1

    # scheme-c single
    total += 1
    if run_case(
        "scheme-c 当前层",
        {
            **base,
            "detectEngine": "scheme-c",
            "detectMode": "single",
            "detect_mode": "single",
            "singleSlice": True,
            "sliceIndex": slice_index,
            "currentSliceIndex": slice_index,
        },
    ):
        passed += 1

    # scheme-a series (may be slow on CPU)
    total += 1
    if run_case(
        "scheme-a 全序列",
        {
            **base,
            "detectEngine": "scheme-a",
            "detectMode": "series",
        },
    ):
        passed += 1

    # scheme-b series
    total += 1
    if run_case(
        "scheme-b 全序列",
        {**base, "detectEngine": "scheme-b", "detectMode": "series"},
    ):
        passed += 1

    # scheme-c series should fail
    total += 1
    _result, events, error = stream_detect(
        {**base, "detectEngine": "scheme-c", "detectMode": "series"}
    )
    ok = error is not None or any(e.get("type") == "error" for e in events)
    print(f"\n[CASE] scheme-c 拒绝全序列: {'✅' if ok else '❌'}")
    if ok:
        passed += 1

    from app.log_paths import ai_e2e_dir

    print(f"\n{'='*60}\nE2E: {passed}/{total} 通过")
    meta_path = ai_e2e_dir() / "last-meta.json"
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    with open(meta_path, "w", encoding="utf-8") as fh:
        json.dump({**meta, "sliceIndex": slice_index}, fh, indent=2)
    print(f"元数据已保存: {meta_path}")

    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
