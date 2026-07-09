"""带进度事件的病灶识别流水线。"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, Generator, Optional

from .chest_detector import detect_chest_lesions, gpu_available, is_chest_body_part
from .config import settings
from .dicom_volume import _client, _object_key, download_slice, parse_slice
from .engines import assert_engine_available, normalize_engine
from .logging_ctx import new_request_id, set_sse_emitter, step_log
from .schemas import DetectLesionRequest, Lesion
from .task_runtime import (
    is_task_cancelled,
    register_fusion_process,
    unregister_fusion_process,
)

DISCLAIMER = "AI 辅助结果仅供临床参考，不能替代医生诊断。"


def _event(event_type: str, **data: Any) -> Dict[str, Any]:
    return {"type": event_type, **data}


def _normalize_detect_mode(mode: str | None) -> str:
    value = (mode or "series").strip().lower()
    return "single" if value == "single" else "series"


def _resolve_slice_index(req: DetectLesionRequest) -> int:
    if req.sliceIndex is not None:
        return max(0, int(req.sliceIndex))
    return max(0, int(req.currentSliceIndex))


def _target_max_slices(spacing_z: float, z_count: int, engine_id: str) -> int:
    if engine_id.startswith("scheme-b"):
        if spacing_z <= 1.0:
            return min(150, z_count)
        if spacing_z >= 3.0:
            return min(250, z_count)
        return min(200, z_count)
    if gpu_available() and z_count <= 300:
        return z_count
    return min(200 if gpu_available() else settings.series_max_slices_cpu, z_count)


def _maybe_subsample_series_volume(
    volume,
    spacing,
    engine_id: str,
) -> tuple:
    from .volume_subsample import subsample_volume_z

    z_count = int(volume.shape[0])
    spacing_z = float(spacing[0]) if spacing else 1.0
    target = _target_max_slices(spacing_z, z_count, engine_id)

    if z_count <= target:
        identity = {i: i for i in range(z_count)}
        return volume, spacing, identity, {"subsampled": False, "target_slices": target}

    new_volume, new_spacing, slice_remap, info = subsample_volume_z(volume, spacing, target)
    info["engine"] = engine_id
    info["subsample_trigger"] = "scheme_b_dynamic" if engine_id.startswith("scheme-b") else (
        "gpu_large" if gpu_available() else "cpu"
    )
    info["target_slices"] = target
    return new_volume, new_spacing, slice_remap, info


def _download_series_bytes(
    req: DetectLesionRequest,
    task_id: Optional[str] = None,
) -> list:
    """下载全序列 DICOM；层数较多时默认并行。"""
    use_parallel = os.getenv("MINIO_PARALLEL_DOWNLOAD", "true").lower() in ("1", "true", "yes")
    if use_parallel and req.imageCount >= 8:
        from .minio_download import download_series_parallel

        def _cancel() -> bool:
            return bool(task_id and is_task_cancelled(task_id))

        last_reported = {"n": 0}

        def _progress(done: int, total: int) -> None:
            last_reported["n"] = done

        raw_list = download_series_parallel(
            req.bucket,
            req.studyUid,
            req.seriesUid,
            req.imageCount,
            cancel_check=_cancel,
            on_progress=_progress,
        )
        return raw_list

    client = _client()
    raw_list = []
    for i in range(1, req.imageCount + 1):
        if task_id and is_task_cancelled(task_id):
            raise RuntimeError("任务已取消")
        key = _object_key(req.studyUid, req.seriesUid, i)
        response = client.get_object(req.bucket, key)
        try:
            raw_list.append(response.read())
        finally:
            response.close()
            response.release_conn()
    return raw_list


# ---------------------------------------------------------------------------
# scheme-a 全序列识别
# ---------------------------------------------------------------------------

def _run_scheme_a_series(
    req: DetectLesionRequest,
    engine_id: str,
) -> Generator[Dict[str, Any], None, None]:
    request_id = new_request_id()

    yield _event("progress", percent=5, stage="download", message="正在从 MinIO 下载 DICOM…")
    task_id = getattr(req, "taskId", None)
    raw_list = []
    try:
        raw_list = _download_series_bytes(req, task_id=task_id)
        yield _event(
            "progress",
            percent=60,
            stage="download",
            message=f"已从 MinIO 下载 DICOM {req.imageCount}/{req.imageCount}",
        )
    except Exception as exc:
        if str(exc) == "任务已取消":
            yield _event("warn", message="任务已取消", progress=0, stage="cancelled")
            return
        yield _event("error", message=f"无法从 MinIO 读取 DICOM 序列: {exc}", progress=0)
        return

    yield _event("progress", percent=62, stage="volume", message="正在按 IPP 排序并构建 3D 体数据…")

    with step_log(request_id, "volume_build", engine=engine_id, detect_mode="series") as metrics:
        from .robust_ct_loader import load_series_dicoms
        meta = load_series_dicoms(raw_list)
        volume = meta.volume
        spacing = meta.spacing
        rows = meta.rows
        cols = meta.cols
        metrics["slice_count"] = meta.slice_count
        metrics["sort_method"] = meta.sort_method
        metrics["removed_localizers"] = meta.removed_localizers

    volume, spacing, slice_remap, subsample_info = _maybe_subsample_series_volume(
        volume, spacing, engine_id
    )
    if subsample_info.get("subsampled"):
        yield _event("warn", code="SERIES_SUBSAMPLED",
                     message=f"CPU 模式：序列 {subsample_info['original_slices']} 层已降采样为 "
                             f"{subsample_info['used_slices']} 层以加速分析",
                     progress=74, stage="volume")

    yield _event("log", level="info",
                 message=(f"[DICOM] 体数据 Z×H×W = {volume.shape[0]}×{rows}×{cols}，"
                         f"层间距 {spacing[0]:.2f} mm，排序方式 {meta.sort_method}"),
                 progress=72, stage="volume")

    from .scheme_a_detector import _adaptive_hu_range, _adaptive_continuity_min
    hu_min, hu_max = _adaptive_hu_range(spacing[0])
    cont_min = _adaptive_continuity_min(spacing[0])
    yield _event("log", level="info",
                 message=(f"[方案A] 自适应参数: HU [{hu_min:.0f}, {hu_max:.0f}]，"
                         f"连续性≥{cont_min}层（层间距 {spacing[0]:.1f}mm）"),
                 progress=75, stage="volume")

    yield _event("progress", percent=78, stage="segment", message="TotalSegmentator 肺区分割中…")
    lung_voxels = 0
    with step_log(request_id, "lung_mask", engine=engine_id, detect_mode="series") as metrics:
        from .totalsegmentator_lung import get_lung_mask_3d
        lung_mask = get_lung_mask_3d(volume, spacing)
        lung_voxels = int(lung_mask.sum())
        metrics["lung_voxels"] = lung_voxels
        metrics["lung_volume_ml"] = round(lung_voxels * spacing[0] * spacing[1] * spacing[2] / 1000, 1)

    yield _event("progress", percent=88, stage="detect", message="正在形态学候选筛选…")
    with step_log(request_id, "morphology_filter", engine=engine_id, detect_mode="series") as metrics:
        from .scheme_a_detector import detect_series
        detection = detect_series(volume, spacing, rows, cols, lung_mask)
        stats = detection["stats"]
        metrics["candidates"] = stats.get("candidates", 0)
        metrics["lesion_count"] = len(detection["lesions"])

    lesions_raw = detection["lesions"]
    stats = detection.get("stats", {})
    if subsample_info.get("subsampled"):
        from .volume_subsample import remap_lesions_slice_index
        lesions_raw = remap_lesions_slice_index(lesions_raw, slice_remap)
        stats = {**stats, "subsample": subsample_info}

    from .slice_index_map import map_lesions_to_file_slices
    lesions_raw = map_lesions_to_file_slices(lesions_raw, meta.file_slice_indices)

    # P2: 详细日志
    yield _event("log", level="info",
                 message=(f"[方案A] 3D筛选: 总候选={stats.get('candidates',0)} "
                          f"体积过滤={stats.get('volumeRejected',0)} "
                          f"solidity过滤={stats.get('solidityRejected',0)} "
                          f"连续性过滤={stats.get('continuityRejected',0)} "
                          f"肺门抑制={stats.get('hilarSuppressed',0)} "
                          f"最终={len(lesions_raw)}"),
                 progress=90, stage="detect")

    if not lesions_raw:
        stats = {**stats, "reason": "NO_LESION_FOUND",
                 "message": "全序列未发现符合形态学条件的疑似病灶"}

    yield _event("log", level="success",
                 message=f"[方案A] 识别完成：肺野体素 {lung_voxels}，检出 {len(lesions_raw)} 处疑似病灶",
                 progress=96, stage="done")
    yield _event("stats", lesionCount=len(lesions_raw),
                 candidates=stats.get("candidates", 0),
                 lungVoxels=lung_voxels, progress=92, stage="detect")

    lesions = [Lesion(**item).model_dump() for item in lesions_raw]
    result = {
        "bodyPart": req.bodyPart,
        "studyUid": req.studyUid,
        "seriesUid": req.seriesUid,
        "engine": f"scheme-a-{'gpu' if gpu_available() else 'cpu'}",
        "gpuAvailable": gpu_available(),
        "disclaimer": DISCLAIMER,
        "overlayType": "bbox",
        "lesions": lesions,
        "meta": {
            "sliceCount": meta.slice_count,
            "spacingMm": {"z": spacing[0], "y": spacing[1], "x": spacing[2]},
            "rows": rows,
            "columns": cols,
            "sortMethod": meta.sort_method,
            "stats": stats,
        },
    }
    yield _event("progress", percent=100, stage="done", message="识别流程结束")
    yield _event("result", data=result, progress=100)


# ---------------------------------------------------------------------------
# scheme-a 当前层识别
# ---------------------------------------------------------------------------

def _run_scheme_a_single(
    req: DetectLesionRequest,
    slice_index: int,
    engine_id: str,
) -> Generator[Dict[str, Any], None, None]:
    request_id = new_request_id()

    if slice_index < 0 or slice_index >= req.imageCount:
        yield _event("error", message=f"层索引无效：{slice_index + 1} / {req.imageCount}", progress=0)
        return

    yield _event("log", level="info",
                 message=f"[方案A] 单层识别，第 {slice_index + 1}/{req.imageCount} 层",
                 progress=2, stage="init")

    yield _event("progress", percent=5, stage="download",
                 message=f"正在下载第 {slice_index + 1} 层 DICOM…")
    try:
        raw = download_slice(req.bucket, req.studyUid, req.seriesUid, slice_index)
    except Exception as exc:
        yield _event("error", message=f"无法从 MinIO 读取当前层 DICOM: {exc}", progress=0)
        return

    yield _event("progress", percent=55, stage="segment", message="正在解析当前层并进行 2D 肺分割…")
    slice_hu, spacing_y, spacing_x, rows, cols, spacing_z = parse_slice(raw)

    with step_log(request_id, "lung_segment_2d", engine=engine_id, detect_mode="single") as metrics:
        from .lung_segment_2d import segment_lungs_2d
        lung_mask_2d = segment_lungs_2d(slice_hu)
        metrics["lung_pixels"] = int(lung_mask_2d.sum())

    if lung_mask_2d.sum() < 500:
        yield _event("error", code="LUNG_AREA_TOO_SMALL",
                     message="当前层面肺野区域过小，无法分析", progress=0)
        return

    yield _event("progress", percent=78, stage="detect", message="正在对当前层进行候选筛选…")
    with step_log(request_id, "morphology_filter_2d", engine=engine_id, detect_mode="single") as metrics:
        from .scheme_a_detector import detect_single_slice
        detection = detect_single_slice(
            slice_hu, spacing_y, spacing_x, slice_index, lung_mask_2d, spacing_z=spacing_z
        )
        stats = detection["stats"]
        metrics["candidates"] = stats.get("candidates", 0)
        metrics["lesion_count"] = len(detection["lesions"])

    lesions_raw = detection["lesions"]

    yield _event("log", level="info",
                 message=(f"[方案A] 2D筛选(层{slice_index+1}): "
                          f"候选={stats.get('candidates',0)} "
                          f"面积过滤={stats.get('areaRejected',0)} "
                          f"肺门抑制={stats.get('hilarSuppressed',0)} "
                          f"最终={len(lesions_raw)}"),
                 progress=88, stage="detect")

    if not lesions_raw:
        stats = {**stats, "reason": "NO_LESION_FOUND",
                 "message": "当前层未发现符合形态学条件的疑似病灶"}

    yield _event("log", level="success",
                 message=f"[方案A] 当前层识别完成：检出 {len(lesions_raw)} 处疑似病灶",
                 progress=96, stage="done")

    lesions = [Lesion(**item).model_dump() for item in lesions_raw]
    result = {
        "bodyPart": req.bodyPart,
        "studyUid": req.studyUid,
        "seriesUid": req.seriesUid,
        "engine": f"scheme-a-single-{'gpu' if gpu_available() else 'cpu'}",
        "gpuAvailable": gpu_available(),
        "disclaimer": DISCLAIMER,
        "overlayType": "bbox",
        "lesions": lesions,
        "meta": {
            "detectMode": "single",
            "sliceIndex": slice_index,
            "sliceCount": req.imageCount,
            "spacingMm": {"y": spacing_y, "x": spacing_x},
            "rows": rows,
            "columns": cols,
            "stats": stats,
        },
    }
    yield _event("progress", percent=100, stage="done", message="单层识别流程结束")
    yield _event("result", data=result, progress=100)


# ---------------------------------------------------------------------------
# scheme-b 全序列识别（融合精准分析）
# ---------------------------------------------------------------------------

def _run_scheme_b_series(
    req: DetectLesionRequest,
    engine_id: str,
) -> Generator[Dict[str, Any], None, None]:
    import threading
    import time

    request_id = new_request_id()
    task_id = getattr(req, "taskId", None)

    sub_engine = getattr(req, "detectSubEngine", "auto") or "auto"
    if sub_engine not in ("auto", "monai", "nndet"):
        sub_engine = "auto"

    yield _event("log", level="info",
                 message=f"[方案B] 融合分析，共 {req.imageCount} 层，子引擎: {sub_engine}",
                 progress=1, stage="init")

    from .volume_cache import save_volume_cache, try_load_cached_volume

    cache_hit = False
    meta = try_load_cached_volume(req.studyUid, req.seriesUid, req.imageCount)
    if meta is not None:
        cache_hit = True
        yield _event(
            "progress",
            percent=55,
            stage="download",
            message=f"命中体数据缓存，跳过 MinIO 下载（{meta.slice_count} 层）",
        )
    else:
        yield _event("progress", percent=5, stage="download", message="正在从 MinIO 下载 DICOM…")
        raw_list = []
        try:
            raw_list = _download_series_bytes(req, task_id=task_id)
            yield _event(
                "progress",
                percent=60,
                stage="download",
                message=f"已从 MinIO 下载 DICOM {req.imageCount}/{req.imageCount}",
            )
        except Exception as exc:
            if str(exc) == "任务已取消":
                yield _event("warn", message="任务已取消", progress=0, stage="cancelled")
                return
            yield _event("error", message=f"无法从 MinIO 读取 DICOM 序列: {exc}", progress=0)
            return

        yield _event("progress", percent=62, stage="volume", message="正在构建 3D 体数据…")
        from .robust_ct_loader import load_series_dicoms
        meta = load_series_dicoms(raw_list)
        save_volume_cache(meta, req.studyUid, req.seriesUid)

    yield _event("progress", percent=62, stage="volume", message="正在加载 3D 体数据…")
    with step_log(request_id, "volume_build", engine=engine_id, detect_mode="series") as metrics:
        volume = meta.volume
        spacing = meta.spacing
        rows = meta.rows
        cols = meta.cols
        metrics["slice_count"] = meta.slice_count
        metrics["volume_cache_hit"] = cache_hit

    volume, spacing, slice_remap, subsample_info = _maybe_subsample_series_volume(
        volume, spacing, engine_id
    )
    if subsample_info.get("subsampled"):
        yield _event(
            "warn",
            code="SERIES_SUBSAMPLED",
            message=(
                f"序列降采样 {subsample_info['original_slices']}→{subsample_info['used_slices']} 层"
                f"（目标 {subsample_info.get('target_slices', '?')} 层）"
            ),
            progress=70,
            stage="volume",
        )

    if settings.scheme_b_hu_quality_gate:
        from .volume_quality import check_volume_hu_quality
        quality = check_volume_hu_quality(volume)
        if not quality.get("ok"):
            yield _event(
                "warn",
                code=quality.get("reason") or "HU_QUALITY",
                message=quality.get("message") or "体数据 HU 质量检查未通过，结果仅供参考",
                progress=72,
                stage="volume",
            )

    fusion_timeout_sec = settings.fusion_timeout_sec
    timeout_min = max(1, fusion_timeout_sec // 60)
    yield _event(
        "progress",
        percent=78,
        stage="detect",
        message=f"正在融合分析（肺分割 + MONAI 推理，最长约 {timeout_min} 分钟）…",
    )

    import threading
    import time

    FUSION_WAIT_MILESTONES = (
        (0, 79, "TotalSegmentator 肺叶分割中…"),
        (30, 82, "深度学习检测推理中…"),
        (90, 85, "融合过滤与病灶标注…"),
        (180, 88, "融合分析进行中（耗时较长属正常）…"),
    )

    def _fusion_wait_progress(elapsed: float) -> tuple[int, str]:
        pct, msg = FUSION_WAIT_MILESTONES[0][1], FUSION_WAIT_MILESTONES[0][2]
        for threshold, p, m in FUSION_WAIT_MILESTONES:
            if elapsed >= threshold:
                pct, msg = p, m
        return pct, msg

    fusion_done = threading.Event()
    fusion_result: Dict[str, Any] = {}
    fusion_error: list = []

    from .fusion_subprocess import start_fusion_process

    fusion_process, result_queue, fusion_cancel = start_fusion_process(
        volume,
        spacing,
        rows,
        cols,
        sub_engine,
        request_id,
        engine_id,
    )
    register_fusion_process(task_id, fusion_process)

    fusion_start = time.time()
    while not fusion_done.is_set():
        if not result_queue.empty():
            kind, payload = result_queue.get()
            if kind == "ok":
                fusion_result["detection"] = payload
            else:
                fusion_error.append(RuntimeError(payload))
            fusion_done.set()
            break
        if not fusion_process.is_alive():
            if not fusion_done.is_set():
                code = fusion_process.exitcode
                if code not in (0, None) and not fusion_error and result_queue.empty():
                    fusion_error.append(
                        RuntimeError(f"融合子进程异常退出 (exitcode={code})")
                    )
                fusion_done.set()
            break
        if is_task_cancelled(task_id):
            fusion_cancel.set()
            if fusion_process.is_alive():
                fusion_process.terminate()
                fusion_process.join(timeout=5)
                if fusion_process.is_alive():
                    fusion_process.kill()
                    fusion_process.join(timeout=2)
            unregister_fusion_process(task_id, fusion_process)
            yield _event("warn", message="任务已取消", progress=0, stage="cancelled")
            return
        elapsed = time.time() - fusion_start
        if elapsed > fusion_timeout_sec:
            fusion_cancel.set()
            if fusion_process.is_alive():
                fusion_process.terminate()
                fusion_process.join(timeout=5)
                if fusion_process.is_alive():
                    fusion_process.kill()
                    fusion_process.join(timeout=2)
            unregister_fusion_process(task_id, fusion_process)
            yield _event(
                "error",
                message=f"融合分析超时（{timeout_min} 分钟）。"
                        "请尝试减少序列层数或使用方案A。",
                progress=0,
            )
            return
        fusion_done.wait(timeout=5)
        wait_pct, wait_msg = _fusion_wait_progress(elapsed)
        yield _event(
            "progress",
            percent=wait_pct,
            stage="detect",
            message=wait_msg,
        )
        yield _event(
            "log",
            level="info",
            message=f"[方案B] {wait_msg}",
            progress=wait_pct,
            stage="detect",
        )

    if fusion_process.is_alive():
        fusion_process.join(timeout=1)
    unregister_fusion_process(task_id, fusion_process)

    if fusion_error:
        yield _event("error", message=f"融合分析失败: {fusion_error[0]}", progress=0)
        return
    if "detection" not in fusion_result:
        yield _event("error", message="融合分析未返回结果", progress=0)
        return

    detection = fusion_result["detection"]
    stats = detection["stats"]

    lesions_raw = detection["lesions"]
    ggo_regions = detection.get("ggoRegions", [])
    if subsample_info.get("subsampled"):
        from .volume_subsample import remap_ggo_regions, remap_lesions_slice_index
        lesions_raw = remap_lesions_slice_index(lesions_raw, slice_remap)
        ggo_regions = remap_ggo_regions(ggo_regions, slice_remap)
        stats = {**stats, "subsample": subsample_info}

    from .slice_index_map import map_ggo_to_file_slices, map_lesions_to_file_slices
    lesions_raw = map_lesions_to_file_slices(lesions_raw, meta.file_slice_indices)
    ggo_regions = map_ggo_to_file_slices(ggo_regions, meta.file_slice_indices)

    enhanced_uid = getattr(req, "enhancedSeriesUid", None) or None
    enhanced_count = getattr(req, "enhancedImageCount", None) or req.imageCount
    if enhanced_uid:
        yield _event(
            "progress",
            percent=88,
            stage="enhanced",
            message="正在加载配对增强 CT 并计算 ΔHU…",
        )
        try:
            enh_req = req.model_copy(update={
                "seriesUid": enhanced_uid,
                "imageCount": int(enhanced_count),
            })
            enh_raw = _download_series_bytes(req=enh_req, task_id=task_id)
            from .robust_ct_loader import load_series_dicoms
            from .enhanced_ct_utils import apply_enhancement_to_lesions
            enh_meta = load_series_dicoms(enh_raw)
            lesions_raw = apply_enhancement_to_lesions(
                lesions_raw, volume, enh_meta.volume, rows, cols,
            )
            stats = {**stats, "enhancedSeriesUid": enhanced_uid, "enhancementApplied": True}
        except Exception as exc:
            yield _event("warn", message=f"增强 CT ΔHU 计算跳过: {exc}", progress=89)
            stats = {**stats, "enhancementApplied": False, "enhancementError": str(exc)}

    candidate_source = stats.get("candidate_source", "unknown")
    ggo_heuristic = stats.get("ggo_heuristic_count", 0)
    ggo_merged = stats.get("ggo_merged_count", 0)
    yield _event("log", level="info",
                 message=(f"[方案B] 检测器: {candidate_source} | "
                          f"MONAI原始框={stats.get('nndet_candidates', 0)} "
                          f"解析后={stats.get('raw_lesion_count', len(lesions_raw))} "
                          f"融合保留={stats.get('fusion_filtered', len(lesions_raw))} "
                          f"肺外过滤={stats.get('filter_lung_rejected', 0)} "
                          f"血管过滤={stats.get('filter_vessel_rejected', 0)} "
                          f"GGO启发式={ggo_heuristic} 合并入病灶={ggo_merged}"),
                 progress=90, stage="detect")

    reason = stats.get("reason", "")
    if reason:
        yield _event("warn", code=reason, message=stats.get("message", ""),
                     progress=92, stage="detect")

    yield _event("log", level="success",
                 message=f"[方案B] 融合分析完成：检出 {len(lesions_raw)} 处（含 GGO 合并 {ggo_merged}）",
                 progress=96, stage="done")

    lesions = [Lesion(**item).model_dump() for item in lesions_raw]
    result = {
        "bodyPart": req.bodyPart,
        "studyUid": req.studyUid,
        "seriesUid": req.seriesUid,
        "engine": f"scheme-b-{'gpu' if gpu_available() else 'cpu'}",
        "gpuAvailable": gpu_available(),
        "disclaimer": settings.scheme_b_disclaimer,
        "overlayType": "bbox",
        "lesions": lesions,
        "ggoRegions": [],
        "meta": {
            "sliceCount": meta.slice_count,
            "spacingMm": {"z": spacing[0], "y": spacing[1], "x": spacing[2]},
            "rows": rows,
            "columns": cols,
            "stats": stats,
        },
    }
    yield _event("progress", percent=100, stage="done", message="融合分析流程结束")
    yield _event("result", data=result, progress=100)


# ---------------------------------------------------------------------------
# scheme-c 当前层识别（Grad-CAM 热力图）
# ---------------------------------------------------------------------------

def _run_scheme_c_single(
    req: DetectLesionRequest,
    slice_index: int,
    engine_id: str,
) -> Generator[Dict[str, Any], None, None]:
    request_id = new_request_id()

    if slice_index < 0 or slice_index >= req.imageCount:
        yield _event("error", message=f"层索引无效：{slice_index + 1} / {req.imageCount}", progress=0)
        return

    yield _event("log", level="info",
                 message=f"[方案C] DenseNet121 单层筛查，第 {slice_index + 1}/{req.imageCount} 层",
                 progress=2, stage="init")

    yield _event("progress", percent=5, stage="download",
                 message=f"正在下载第 {slice_index + 1} 层 DICOM…")
    try:
        raw = download_slice(req.bucket, req.studyUid, req.seriesUid, slice_index)
    except Exception as exc:
        yield _event("error", message=f"无法从 MinIO 读取当前层 DICOM: {exc}", progress=0)
        return

    yield _event("progress", percent=55, stage="infer", message="正在预处理 + DenseNet121 推理 + Grad-CAM…")
    slice_hu, spacing_y, spacing_x, rows, cols, spacing_z = parse_slice(raw)

    try:
        with step_log(request_id, "gradcam", engine=engine_id, detect_mode="single") as metrics:
            from .scheme_c_screening import predict
            result = predict(slice_hu)
            metrics["confidence"] = result["screening"]["confidence"]

        screening = result["screening"]
        heatmap_data = result["heatmap"]

        yield _event("log", level="info",
                     message=(f"[方案C] 分类: {screening['label']} "
                              f"(置信度 {screening['confidence']:.2f}) "
                              f"肺区聚焦比: {screening.get('lungFocusRatio', 0):.2f}"),
                     progress=90, stage="detect")

        yield _event("log", level="success",
                     message=f"[方案C] DenseNet121 筛查完成 (免责: 非医学诊断，仅供管线验证)",
                     progress=96, stage="done")

        final_result = {
            "bodyPart": req.bodyPart,
            "studyUid": req.studyUid,
            "seriesUid": req.seriesUid,
            "engine": f"scheme-c-{'gpu' if gpu_available() else 'cpu'}",
            "gpuAvailable": gpu_available(),
            "disclaimer": screening.get("disclaimer", DISCLAIMER),
            "overlayType": "heatmap",
            "screening": screening,
            "heatmap": heatmap_data,
            "lesions": [],
            "meta": {
                "detectMode": "single",
                "sliceIndex": slice_index,
                "sliceCount": req.imageCount,
                "rows": rows,
                "columns": cols,
            },
        }
        yield _event("progress", percent=100, stage="done", message="方案C筛查流程结束")
        yield _event("result", data=final_result, progress=100)

    except Exception as exc:
        yield _event("error", message=f"方案 C 推理失败: {exc}", progress=0)


# ---------------------------------------------------------------------------
# 旧引擎兼容（heuristic / totalsegmentator / monai-retinanet）
# ---------------------------------------------------------------------------

def _run_detection(volume, spacing, rows, cols, engine_id):
    if engine_id == "heuristic":
        detection = detect_chest_lesions(volume, spacing, rows, cols)
    else:
        from .totalsegmentator_lung import get_lung_mask_3d
        lung_mask = get_lung_mask_3d(volume, spacing)
        from .chest_detector import detect_chest_lesions
        detection = detect_chest_lesions(volume, spacing, rows, cols, lung_mask=lung_mask)
    return detection, engine_id


def _run_slice_detection(slice_hu, spacing_y, spacing_x, slice_index, engine_id):
    from .chest_detector import _segment_lungs, _extract_contour, _lesion_type, _confidence
    lung_mask = _segment_lungs(np.expand_dims(slice_hu, 0))[0]
    from .scheme_a_detector import detect_single_slice
    detection = detect_single_slice(slice_hu, spacing_y, spacing_x, slice_index, lung_mask)
    return detection, engine_id


# ---------------------------------------------------------------------------
# 调度器
# ---------------------------------------------------------------------------

STEP_LABELS = {
    "volume_build": "构建 3D 体数据",
    "lung_mask": "肺野分割",
    "morphology_filter": "形态学候选筛选",
    "lung_segment_2d": "2D 肺分割",
    "morphology_filter_2d": "2D 形态学筛选",
    "fusion_filter": "融合分析 (TotalSegmentator + MONAI)",
    "gradcam": "DenseNet121 + Grad-CAM",
}


def _drain_sse_buffer(buffer: list) -> Generator[Dict[str, Any], None, None]:
    while buffer:
        yield buffer.pop(0)


def run_detection_events(req: DetectLesionRequest) -> Generator[Dict[str, Any], None, None]:
    sse_buffer: list = []

    def _capture_sse(event: Dict[str, Any]) -> None:
        label = STEP_LABELS.get(event.get("step_id", ""), event.get("step_id", ""))
        if event.get("type") == "step_start" and label:
            event = {**event, "label": label}
        sse_buffer.append(event)

    set_sse_emitter(_capture_sse)
    try:
        for event in _run_detection_events_inner(req):
            yield from _drain_sse_buffer(sse_buffer)
            yield event
        yield from _drain_sse_buffer(sse_buffer)
    except Exception as exc:
        yield _event("error", message=str(exc), progress=0)
    finally:
        set_sse_emitter(None)


def _run_detection_events_inner(req: DetectLesionRequest) -> Generator[Dict[str, Any], None, None]:
    engine_id = normalize_engine(req.detectEngine)
    detect_mode = _normalize_detect_mode(req.detectMode)
    slice_index = _resolve_slice_index(req)

    # 旧引擎兼容层
    if engine_id in ("heuristic", "totalsegmentator", "monai-retinanet"):
        engine_id = "scheme-a"

    # ── scheme-a 分支 ──
    if engine_id == "scheme-a":
        try:
            assert_engine_available(engine_id)
        except RuntimeError as exc:
            yield _event("error", message=str(exc), progress=0)
            return
        if detect_mode == "single":
            yield from _run_scheme_a_single(req, slice_index, engine_id)
        else:
            yield from _run_scheme_a_series(req, engine_id)
        return

    # ── scheme-c 分支 ──
    if engine_id == "scheme-c":
        if detect_mode != "single":
            yield _event("error", code="INVALID_DETECT_MODE",
                         message="方案 C 仅支持当前层识别", progress=0)
            return
        yield from _run_scheme_c_single(req, slice_index, engine_id)
        return

    # ── scheme-b 分支 ──
    if engine_id == "scheme-b":
        if detect_mode != "series":
            yield _event("error", code="INVALID_DETECT_MODE",
                         message="方案 B 仅支持全序列识别，请使用「识别病灶」按钮", progress=0)
            return
        yield from _run_scheme_b_series(req, engine_id)
        return

    # ── 旧引擎兼容 ──
    if detect_mode == "single":
        yield _event("log", level="info",
                     message=f"[Python] 单层识别模式 detectMode=single，目标层 {slice_index + 1}/{req.imageCount}",
                     progress=1, stage="init")
        yield from _run_single_slice_events(req, slice_index, engine_id)
        return

    try:
        assert_engine_available(engine_id)
    except RuntimeError as exc:
        yield _event("error", message=str(exc), progress=0)
        return

    yield _event("log", level="info",
                 message=f"[Python] 识别方式: {engine_id}（全序列）",
                 progress=1, stage="init")
    yield _event("log", level="info",
                 message=f"[MinIO] 桶={req.bucket}，序列={req.seriesUid}，共 {req.imageCount} 层",
                 progress=3, stage="init")

    client = _client()
    raw_list = []
    try:
        for i in range(1, req.imageCount + 1):
            key = _object_key(req.studyUid, req.seriesUid, i)
            response = client.get_object(req.bucket, key)
            try:
                raw_list.append(response.read())
            finally:
                response.close()
                response.release_conn()
            percent = 5 + int(55 * i / max(req.imageCount, 1))
            yield _event("progress", percent=percent, stage="download",
                         message=f"正在从 MinIO 下载 DICOM {i}/{req.imageCount}")
    except Exception as exc:
        yield _event("error", message=f"无法从 MinIO 读取 DICOM 序列: {exc}", progress=0)
        return

    if len(raw_list) != req.imageCount:
        yield _event("error", message="DICOM 切片数量与元数据不一致", progress=0)
        return

    yield _event("log", level="info",
                 message=f"[DICOM] 下载完成，共 {len(raw_list)} 层",
                 progress=62, stage="volume")

    try:
        yield _event("progress", percent=65, stage="volume",
                     message="正在解析 DICOM 并构建 3D 体数据 (HU)")
        from .dicom_volume import build_volume
        volume, spacing, rows, cols = build_volume(raw_list)
        yield _event("log", level="info",
                     message=f"[DICOM] 体数据 Z×H×W = {volume.shape[0]}×{rows}×{cols}，"
                             f"层间距 {spacing[0]:.2f} mm",
                     progress=72, stage="volume")

        yield _event("progress", percent=78, stage="detect", message="正在识别…")
        detection, engine = _run_detection(volume, spacing, rows, cols, engine_id)
        lesions_raw = detection["lesions"]
        stats = detection.get("stats", {})

        yield _event("log", level="info",
                     message=f"[AI] 肺野体素 {stats.get('lungVoxels', 0)}，"
                             f"候选区域 {stats.get('candidates', 0)} 个",
                     progress=88, stage="detect")
        yield _event("stats", lesionCount=len(lesions_raw),
                     candidates=stats.get("candidates", 0),
                     lungVoxels=stats.get("lungVoxels", 0),
                     progress=92, stage="detect")
        yield _event("log", level="success",
                     message=f"[AI] 识别完成：共检出 {len(lesions_raw)} 处疑似病灶",
                     progress=96, stage="done")

        lesions = [Lesion(**item).model_dump() for item in lesions_raw]
        result = {
            "bodyPart": req.bodyPart,
            "studyUid": req.studyUid,
            "seriesUid": req.seriesUid,
            "engine": engine,
            "gpuAvailable": gpu_available(),
            "disclaimer": DISCLAIMER,
            "overlayType": "bbox",
            "lesions": lesions,
            "meta": {
                "sliceCount": req.imageCount,
                "spacingMm": {"z": spacing[0], "y": spacing[1], "x": spacing[2]},
                "rows": rows,
                "columns": cols,
                "stats": stats,
            },
        }
        yield _event("progress", percent=100, stage="done", message="识别流程结束")
        yield _event("result", data=result, progress=100)
    except Exception as exc:
        yield _event("error", message=f"病灶识别失败: {exc}", progress=0)


def sse_encode(event: Dict[str, Any]) -> str:
    return f"data: {json.dumps(event, ensure_ascii=False)}\n\n"


def _run_single_slice_events(
    req: DetectLesionRequest,
    slice_index: int,
    engine_id: str,
) -> Generator[Dict[str, Any], None, None]:
    if slice_index < 0 or slice_index >= req.imageCount:
        yield _event("error", message=f"层索引无效：{slice_index + 1} / {req.imageCount}", progress=0)
        return

    yield _event("log", level="info",
                 message=f"[Python] 单层识别，第 {slice_index + 1}/{req.imageCount} 层",
                 progress=2, stage="init")

    try:
        assert_engine_available(engine_id)
    except RuntimeError as exc:
        yield _event("error", message=str(exc), progress=0)
        return

    yield _event("log", level="info",
                 message=f"[MinIO] 桶={req.bucket}，下载第 {slice_index + 1} 层 DICOM",
                 progress=5, stage="download")

    try:
        raw = download_slice(req.bucket, req.studyUid, req.seriesUid, slice_index)
    except Exception as exc:
        yield _event("error", message=f"无法从 MinIO 读取当前层 DICOM: {exc}", progress=0)
        return

    yield _event("progress", percent=40, stage="download", message=f"已下载第 {slice_index + 1} 层")

    try:
        yield _event("progress", percent=55, stage="volume", message="正在解析当前层 DICOM (HU)")
        slice_hu, spacing_y, spacing_x, rows, cols, spacing_z = parse_slice(raw)
        yield _event("log", level="info",
                     message=f"[DICOM] 当前层 {rows}×{cols}，像素间距 {spacing_y:.2f}×{spacing_x:.2f} mm",
                     progress=65, stage="volume")

        yield _event("progress", percent=78, stage="detect", message="正在对当前层进行病灶检测…")
        detection, engine = _run_slice_detection(slice_hu, spacing_y, spacing_x, slice_index, engine_id)
        lesions_raw = detection["lesions"]
        stats = detection.get("stats", {})

        yield _event("log", level="info",
                     message=f"[AI] 肺野像素 {stats.get('lungVoxels', 0)}，候选区域 {stats.get('candidates', 0)} 个",
                     progress=88, stage="detect")
        yield _event("stats", lesionCount=len(lesions_raw),
                     candidates=stats.get("candidates", 0),
                     lungVoxels=stats.get("lungVoxels", 0),
                     progress=92, stage="detect")
        yield _event("log", level="success",
                     message=f"[AI] 当前层识别完成：检出 {len(lesions_raw)} 处疑似病灶",
                     progress=96, stage="done")

        lesions = [Lesion(**item).model_dump() for item in lesions_raw]
        result = {
            "bodyPart": req.bodyPart,
            "studyUid": req.studyUid,
            "seriesUid": req.seriesUid,
            "engine": engine,
            "gpuAvailable": gpu_available(),
            "disclaimer": DISCLAIMER,
            "overlayType": "bbox",
            "lesions": lesions,
            "meta": {
                "detectMode": "single",
                "sliceIndex": slice_index,
                "sliceCount": req.imageCount,
                "spacingMm": {"y": spacing_y, "x": spacing_x},
                "rows": rows,
                "columns": cols,
                "stats": stats,
            },
        }
        yield _event("progress", percent=100, stage="done", message="单层识别流程结束")
        yield _event("result", data=result, progress=100)
    except Exception as exc:
        yield _event("error", message=f"单层病灶识别失败: {exc}", progress=0)
