import asyncio
import logging
import os
import queue
import sys

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from .chest_detector import gpu_available
from .config import settings
from .detection_runner import run_detection_events, sse_encode
from .engines import get_engine_catalog, refresh_engine_catalog
from .log_paths import ensure_ai_dirs
from .schemas import DetectLesionRequest, DetectLesionResponse
from .task_pool import GpuSlot, TaskCancelledError, engine_needs_gpu, get_detect_executor
from .task_runtime import cancel_task, is_task_cancelled, register_task, unregister_task

# ── 结构化 JSON 日志配置 ──
log_level = os.getenv("AI_LOG_LEVEL", "INFO")
ensure_ai_dirs()
_log_dir = os.path.dirname(settings.ai_log_path)

# 控制台 Handler（plain text）
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(getattr(logging, log_level, logging.INFO))
console_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))

# JSON 文件 Handler
if settings.ai_log_json:
    try:
        file_handler = logging.FileHandler(settings.ai_log_path, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        # 文件日志不需额外格式化，logging_ctx 已输出 JSON 行
        file_handler.setFormatter(logging.Formatter("%(message)s"))
    except Exception:
        file_handler = None
else:
    file_handler = None

# 配置 ai-service.structured logger
structured_logger = logging.getLogger("ai-service.structured")
structured_logger.setLevel(logging.INFO)
structured_logger.propagate = False
structured_logger.addHandler(console_handler)
if file_handler:
    structured_logger.addHandler(file_handler)

# 配置 root logger
logging.basicConfig(level=getattr(logging, log_level, logging.INFO),
                    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                    handlers=[console_handler])

logger = logging.getLogger(__name__)

app = FastAPI(title="WestChina CT AI Service", version="1.0.0")


@app.on_event("startup")
def warmup_engine_catalog():
    """后台预热引擎目录，避免首个 /engines 请求阻塞过久。"""
    import threading

    def _warm() -> None:
        try:
            catalog = refresh_engine_catalog(force=True)
            logger.info("Engine catalog warmed up (%d engines)", len(catalog))
        except Exception as exc:
            logger.warning("Engine catalog warmup failed: %s", exc)

    threading.Thread(target=_warm, daemon=True, name="engine-catalog-warmup").start()


@app.get("/health")
def health():
    from .task_pool import pool_stats

    return {
        "status": "ok",
        "gpuAvailable": gpu_available(),
        "engine": "scheme-a/b/c",
        "engines": get_engine_catalog(),
        **pool_stats(),
    }


@app.get("/engines")
def list_engines():
    return {"engines": get_engine_catalog()}


@app.post("/detectLesion/stream")
async def detect_lesion_stream(req: DetectLesionRequest):
    logger.info("detectLesion/stream start, engine=%s, mode=%s, slices=%d",
                req.detectEngine, req.detectMode, req.imageCount)

    loop = asyncio.get_event_loop()
    event_queue: queue.Queue = queue.Queue(maxsize=512)
    engine_id = req.detectEngine or "scheme-a"
    task_id = req.taskId
    register_task(task_id)

    def producer() -> None:
        try:
            if engine_needs_gpu(engine_id):
                event_queue.put((
                    "event",
                    {
                        "type": "log",
                        "level": "info",
                        "message": "[方案B] 等待 GPU 资源（按提交顺序排队，前序任务完成后自动开始）…",
                        "progress": 1,
                        "stage": "queued",
                    },
                ))
            with GpuSlot(engine_id, task_id=task_id):
                for event in run_detection_events(req):
                    if is_task_cancelled(task_id):
                        break
                    event_queue.put(("event", event))
        except TaskCancelledError as exc:
            logger.info("detectLesion/stream cancelled while waiting GPU, taskId=%s", task_id)
            event_queue.put((
                "event",
                {
                    "type": "warn",
                    "message": str(exc),
                    "progress": 0,
                    "stage": "cancelled",
                },
            ))
        except Exception as exc:
            logger.exception("detectLesion/stream failed")
            event_queue.put(("error", exc))
        finally:
            event_queue.put(("done", None))
            unregister_task(task_id)

    loop.run_in_executor(get_detect_executor(), producer)

    async def event_stream():
        while True:
            kind, payload = await loop.run_in_executor(None, event_queue.get)
            if kind == "done":
                break
            if kind == "error":
                yield sse_encode({"type": "error", "message": str(payload)})
                break
            yield sse_encode(payload)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/detectLesion/cancel/{task_id}")
def cancel_detect_lesion(task_id: str):
    cancelled = cancel_task(task_id)
    return {"cancelled": cancelled}


@app.post("/detectLesion", response_model=DetectLesionResponse)
def detect_lesion(req: DetectLesionRequest):
    result_data = None
    error_msg = None
    for event in run_detection_events(req):
        if event.get("type") == "result":
            result_data = event.get("data")
        elif event.get("type") == "error":
            error_msg = event.get("message")
    if error_msg:
        raise HTTPException(status_code=500, detail=error_msg)
    if not result_data:
        raise HTTPException(status_code=500, detail="AI 服务未返回识别结果")
    return DetectLesionResponse(**result_data)
