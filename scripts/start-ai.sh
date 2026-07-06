#!/bin/bash
# 启动 CT AI 推理服务（FastAPI，默认 9810）
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/ai-service"

PY=""
if [ -x "$ROOT/ai-service/.conda/bin/python" ]; then
  PY="$ROOT/ai-service/.conda/bin/python"
elif [ -x "$ROOT/ai-service/.venv/bin/python" ]; then
  PY="$ROOT/ai-service/.venv/bin/python"
else
  if [ ! -d "$ROOT/ai-service/.conda" ] && command -v conda >/dev/null 2>&1; then
    conda create -y -p "$ROOT/ai-service/.conda" python=3.11 pip
    PY="$ROOT/ai-service/.conda/bin/python"
    "$PY" -m pip install -r requirements.txt
  elif [ ! -d "$ROOT/ai-service/.venv" ]; then
    python3 -m venv "$ROOT/ai-service/.venv"
    PY="$ROOT/ai-service/.venv/bin/python"
    "$PY" -m pip install -U pip
    "$PY" -m pip install -r requirements.txt
  else
    PY="$ROOT/ai-service/.venv/bin/python"
  fi
fi

export AI_HOST="${AI_HOST:-0.0.0.0}"
export AI_PORT="${AI_PORT:-9810}"
export MINIO_ENDPOINT="${MINIO_ENDPOINT:-127.0.0.1:9000}"
export MINIO_ACCESS_KEY="${MINIO_ACCESS_KEY:-admin}"
export MINIO_SECRET_KEY="${MINIO_SECRET_KEY:-admin123456}"

export SERIES_MAX_SLICES_CPU="${SERIES_MAX_SLICES_CPU:-128}"
export AI_LOG_JSON="${AI_LOG_JSON:-true}"
export AI_LOG_PATH="${AI_LOG_PATH:-$ROOT/deploymentServer/logs/ai-service.log}"

mkdir -p "$ROOT/deploymentServer/logs"
pkill -f "ai-service/run.py" 2>/dev/null || true
pkill -f "ai-service/.conda/bin/python run.py" 2>/dev/null || true
pkill -f "ai-service/.venv/bin/python run.py" 2>/dev/null || true
nohup "$PY" run.py > "$ROOT/deploymentServer/logs/ai-service.log" 2>&1 &
sleep 3
curl -sf "http://127.0.0.1:${AI_PORT}/health" && echo "" && echo "AI 服务已启动: http://127.0.0.1:${AI_PORT}"
