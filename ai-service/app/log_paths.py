"""项目 logs 目录约定（与 scripts/log_paths.sh 对齐）。"""
from __future__ import annotations

import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def logs_root() -> Path:
    env = os.getenv("LOG_ROOT", "").strip()
    if env:
        return Path(env).expanduser()
    return project_root() / "logs"


def ai_logs_dir() -> Path:
    return Path(os.getenv("LOG_DIR_AI", logs_root() / "ai-service"))


def ai_log_file() -> Path:
    return Path(os.getenv("LOG_FILE_AI", ai_logs_dir() / "ai-service.log"))


def ai_cache_dir() -> Path:
    return Path(os.getenv("LOG_DIR_AI_CACHE", os.getenv("SCHEME_B_CACHE_DIR", ai_logs_dir() / "cache" / "volumes")))


def ai_tmp_dir() -> Path:
    return Path(os.getenv("LOG_DIR_AI_TMP", ai_logs_dir() / "tmp"))


def ai_e2e_dir() -> Path:
    return Path(os.getenv("LOG_DIR_AI_E2E", ai_logs_dir() / "e2e"))


def ai_reports_dir() -> Path:
    return Path(os.getenv("LOG_DIR_AI_REPORTS", ai_logs_dir() / "reports"))


def ensure_ai_dirs() -> None:
    for d in (ai_logs_dir(), ai_cache_dir(), ai_tmp_dir(), ai_e2e_dir(), ai_reports_dir()):
        d.mkdir(parents=True, exist_ok=True)


@contextmanager
def ai_temp_directory(prefix: str) -> Iterator[str]:
    """AI 推理临时目录，落在 logs/ai-service/tmp/ 而非 /tmp。"""
    ensure_ai_dirs()
    with tempfile.TemporaryDirectory(prefix=prefix, dir=str(ai_tmp_dir())) as tmp:
        yield tmp
