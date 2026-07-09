"""AI 推理线程池与 GPU 并发槽位。"""
from __future__ import annotations

import logging
import os
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional

from .chest_detector import gpu_available
from .task_runtime import is_task_cancelled

logger = logging.getLogger(__name__)

_executor: Optional[ThreadPoolExecutor] = None
_gpu_sem: Optional[threading.Semaphore] = None
_gpu_slot_cache: Optional[int] = None
_gpu_wait_lock = threading.Lock()
_gpu_waiters = 0

# scheme-b 单路全序列推理大致显存占用（GB），用于按显存推算并发槽位
_SCHEME_B_VRAM_GB_PER_JOB = float(os.getenv("AI_SCHEME_B_VRAM_GB", "6.0"))
_SCHEME_B_VRAM_RESERVE_GB = float(os.getenv("AI_GPU_VRAM_RESERVE_GB", "1.5"))
_GPU_ACQUIRE_POLL_SEC = float(os.getenv("AI_GPU_ACQUIRE_POLL_SEC", "1.0"))


class TaskCancelledError(Exception):
    """任务在排队或执行中被取消。"""


def _default_workers() -> int:
    cpu = os.cpu_count() or 4
    env_val = os.getenv("AI_DETECT_WORKERS")
    if env_val:
        return max(1, int(env_val))
    return max(2, min(cpu, 4))


def get_detect_executor() -> ThreadPoolExecutor:
    global _executor
    if _executor is None:
        workers = _default_workers()
        _executor = ThreadPoolExecutor(max_workers=workers, thread_name_prefix="ai-detect")
    return _executor


def _gpu_device_infos() -> List[Dict[str, Any]]:
    if not gpu_available():
        return []
    try:
        import torch

        infos: List[Dict[str, Any]] = []
        for i in range(torch.cuda.device_count()):
            props = torch.cuda.get_device_properties(i)
            total_gb = props.total_memory / (1024**3)
            free_gb = None
            try:
                free_bytes, total_bytes = torch.cuda.mem_get_info(i)
                free_gb = free_bytes / (1024**3)
                total_gb = total_bytes / (1024**3)
            except Exception:
                pass
            slots = _slots_for_vram_gb(total_gb)
            infos.append(
                {
                    "index": i,
                    "name": props.name,
                    "vramTotalGb": round(total_gb, 2),
                    "vramFreeGb": round(free_gb, 2) if free_gb is not None else None,
                    "recommendedSlots": slots,
                }
            )
        return infos
    except Exception as exc:
        logger.warning("GPU device probe failed: %s", exc)
        return []


def _slots_for_vram_gb(vram_gb: float) -> int:
    """按单卡显存推算 scheme-b 可并行路数（保守估计）。"""
    usable = max(0.0, vram_gb - _SCHEME_B_VRAM_RESERVE_GB)
    if usable < _SCHEME_B_VRAM_GB_PER_JOB:
        return 1
    return max(1, int(usable // _SCHEME_B_VRAM_GB_PER_JOB))


def _auto_gpu_slots() -> int:
    devices = _gpu_device_infos()
    if not devices:
        return 0
    slots = sum(int(d.get("recommendedSlots", 1)) for d in devices)
    return max(1, slots)


def _gpu_slots() -> int:
    global _gpu_slot_cache
    if _gpu_slot_cache is not None:
        return _gpu_slot_cache

    env_val = (os.getenv("AI_GPU_CONCURRENT") or "auto").strip().lower()
    if env_val in ("", "auto"):
        slots = _auto_gpu_slots()
        logger.info(
            "AI_GPU_CONCURRENT=auto -> %d slot(s) (scheme-b ~%.1fGB/job, reserve %.1fGB)",
            slots,
            _SCHEME_B_VRAM_GB_PER_JOB,
            _SCHEME_B_VRAM_RESERVE_GB,
        )
    else:
        slots = max(0, int(env_val))

    _gpu_slot_cache = slots
    return slots


def _get_gpu_sem() -> Optional[threading.Semaphore]:
    global _gpu_sem
    if _gpu_sem is None:
        slots = _gpu_slots()
        _gpu_sem = threading.Semaphore(slots) if slots > 0 else None
    return _gpu_sem


def engine_needs_gpu(engine_id: str | None) -> bool:
    value = (engine_id or "scheme-a").strip().lower()
    return value == "scheme-b"


def gpu_queue_stats() -> Dict[str, int]:
    slots = _gpu_slots()
    with _gpu_wait_lock:
        waiting = _gpu_waiters
    return {"gpuConcurrentSlots": slots, "gpuQueueWaiters": waiting}


def pool_stats() -> dict:
    devices = _gpu_device_infos()
    slots = _gpu_slots()
    mode = (os.getenv("AI_GPU_CONCURRENT") or "auto").strip().lower()
    return {
        "detectWorkers": _default_workers(),
        "gpuConcurrentSlots": slots,
        "gpuConcurrentMode": mode if mode else "auto",
        "gpuDevices": devices,
        "schemeBVramGbPerJob": _SCHEME_B_VRAM_GB_PER_JOB,
        "gpuVramReserveGb": _SCHEME_B_VRAM_RESERVE_GB,
        **gpu_queue_stats(),
    }


class GpuSlot:
    """scheme-b GPU 重任务占用槽位；FIFO 排队，等待期间可响应取消并唤醒后续任务。"""

    def __init__(self, engine_id: str | None, task_id: str | None = None) -> None:
        self._sem = _get_gpu_sem() if engine_needs_gpu(engine_id) else None
        self._task_id = task_id
        self._acquired = False
        self._entered_wait = False

    def __enter__(self) -> "GpuSlot":
        global _gpu_waiters
        if self._sem is None:
            return self

        with _gpu_wait_lock:
            _gpu_waiters += 1
            self._entered_wait = True
            queue_pos = _gpu_waiters

        logger.info(
            "scheme-b task waiting for GPU slot (task_id=%s, queue_pos~=%d)",
            self._task_id,
            queue_pos,
        )

        try:
            while True:
                if self._task_id and is_task_cancelled(self._task_id):
                    raise TaskCancelledError("任务已取消（等待 GPU 资源时）")
                if self._sem.acquire(timeout=_GPU_ACQUIRE_POLL_SEC):
                    if self._task_id and is_task_cancelled(self._task_id):
                        self._sem.release()
                        raise TaskCancelledError("任务已取消（获得 GPU 槽位后）")
                    self._acquired = True
                    logger.info("scheme-b task acquired GPU slot (task_id=%s)", self._task_id)
                    return self
        finally:
            if self._entered_wait:
                with _gpu_wait_lock:
                    _gpu_waiters = max(0, _gpu_waiters - 1)
                self._entered_wait = False

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._acquired and self._sem is not None:
            self._sem.release()
            self._acquired = False
            logger.info("scheme-b task released GPU slot (task_id=%s)", self._task_id)
