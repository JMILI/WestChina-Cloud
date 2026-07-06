import logging
import os
import sys

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from .chest_detector import gpu_available
from .config import settings
from .detection_runner import run_detection_events, sse_encode
from .engines import get_engine_catalog
from .schemas import DetectLesionRequest, DetectLesionResponse

# ── 结构化 JSON 日志配置 ──
log_level = os.getenv("AI_LOG_LEVEL", "INFO")
_log_dir = os.path.dirname(settings.ai_log_path)
if _log_dir:
    os.makedirs(_log_dir, exist_ok=True)

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


@app.get("/health")
def health():
    return {
        "status": "ok",
        "gpuAvailable": gpu_available(),
        "engine": "scheme-a/b/c",
        "engines": get_engine_catalog(),
    }


@app.get("/engines")
def list_engines():
    return {"engines": get_engine_catalog()}


@app.post("/detectLesion/stream")
def detect_lesion_stream(req: DetectLesionRequest):
    logger.info("detectLesion/stream start, engine=%s, mode=%s, slices=%d",
                req.detectEngine, req.detectMode, req.imageCount)

    def event_stream():
        for event in run_detection_events(req):
            yield sse_encode(event)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


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
