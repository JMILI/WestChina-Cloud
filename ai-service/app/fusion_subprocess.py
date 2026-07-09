"""方案 B 融合分析子进程入口（spawn，避免 fork + CUDA 初始化错误）。"""
from __future__ import annotations

import multiprocessing
from typing import Tuple

import numpy as np

# Linux 默认 fork；CUDA/PyTorch 必须在独立进程中用 spawn 启动
_FUSION_CTX = multiprocessing.get_context("spawn")


def fusion_worker(
    result_queue: multiprocessing.Queue,
    cancel_event: multiprocessing.synchronize.Event,
    volume: np.ndarray,
    spacing: Tuple[float, float, float],
    rows: int,
    cols: int,
    sub_engine: str,
    request_id: str,
    engine_id: str,
) -> None:
    """在独立子进程中运行 TotalSegmentator + MONAI，避免继承父进程 CUDA 上下文。"""
    try:
        if cancel_event.is_set():
            return
        from .logging_ctx import step_log
        from .scheme_b_fusion import detect_fusion

        with step_log(request_id, "fusion_filter", engine=engine_id, detect_mode="series") as metrics:
            detection = detect_fusion(volume, spacing, rows, cols, sub_engine=sub_engine)
            if cancel_event.is_set():
                return
            result_queue.put(("ok", detection))
            metrics.update(detection["stats"])
    except Exception as exc:
        if not cancel_event.is_set():
            result_queue.put(("error", str(exc)))
    finally:
        try:
            import torch

            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except Exception:
            pass


def start_fusion_process(
    volume: np.ndarray,
    spacing: Tuple[float, float, float],
    rows: int,
    cols: int,
    sub_engine: str,
    request_id: str,
    engine_id: str,
) -> tuple[multiprocessing.Process, multiprocessing.Queue, multiprocessing.synchronize.Event]:
    """启动 spawn 融合子进程，返回 (process, result_queue, cancel_event)。"""
    result_queue: multiprocessing.Queue = _FUSION_CTX.Queue(maxsize=1)
    cancel_event = _FUSION_CTX.Event()
    proc = _FUSION_CTX.Process(
        target=fusion_worker,
        args=(
            result_queue,
            cancel_event,
            volume,
            spacing,
            rows,
            cols,
            sub_engine,
            request_id,
            engine_id,
        ),
        daemon=False,
    )
    proc.start()
    return proc, result_queue, cancel_event
