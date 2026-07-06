"""结构化日志上下文管理器。

提供 step_log contextmanager，同时写入 JSON 文件日志和 SSE 事件。
"""
from __future__ import annotations

import json
import logging
import time
import uuid
from contextlib import contextmanager
from typing import Any, Callable, Dict, Generator, Optional

logger = logging.getLogger("ai-service.structured")

# 全局 SSE 发射器（由 detection_runner 注入）
_sse_emitter: Optional[Callable[[Dict[str, Any]], None]] = None


def set_sse_emitter(emitter: Optional[Callable[[Dict[str, Any]], None]]) -> None:
    """注入 SSE 发射器回调。"""
    global _sse_emitter
    _sse_emitter = emitter


def _emit_sse(event: Dict[str, Any]) -> None:
    if _sse_emitter:
        try:
            _sse_emitter(event)
        except Exception:
            pass


def new_request_id() -> str:
    """生成短请求 ID（8 位 hex）。"""
    return uuid.uuid4().hex[:8]


@contextmanager
def step_log(
    request_id: str,
    step_id: str,
    engine: str = "",
    detect_mode: str = "",
    **extra: Any,
) -> Generator[Dict[str, Any], None, None]:
    """步骤日志上下文管理器。

    用法:
        with step_log(rid, "lung_mask", engine="scheme-a") as metrics:
            # ... 执行步骤 ...
            metrics["lung_voxels"] = 1250000

    自动在进入/退出时写入 step_start / step_end 日志和 SSE 事件。
    异常时写入 error 事件并重新抛出。
    """
    t0 = time.perf_counter()
    base = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "request_id": request_id,
        "engine": engine,
        "detect_mode": detect_mode,
        "step_id": step_id,
    }

    # step_start
    start_entry = {**base, "event": "step_start", "level": "INFO"}
    logger.info(json.dumps(start_entry, ensure_ascii=False))
    _emit_sse({"type": "step_start", "step_id": step_id, "label": step_id})

    metrics: Dict[str, Any] = {}
    try:
        yield metrics
    except Exception as e:
        err_entry = {
            **base,
            "event": "error",
            "level": "ERROR",
            "code": getattr(e, "code", "UNKNOWN"),
            "message": str(e),
        }
        logger.error(json.dumps(err_entry, ensure_ascii=False))
        _emit_sse({
            "type": "error",
            "code": err_entry["code"],
            "message": str(e),
            "step_id": step_id,
        })
        raise
    finally:
        duration_ms = round((time.perf_counter() - t0) * 1000)
        end_entry = {
            **base,
            "event": "step_end",
            "level": "INFO",
            "duration_ms": duration_ms,
            "metrics": metrics,
        }
        logger.info(json.dumps(end_entry, ensure_ascii=False))
        _emit_sse({
            "type": "step_end",
            "step_id": step_id,
            "duration_ms": duration_ms,
            "metrics": metrics,
        })
