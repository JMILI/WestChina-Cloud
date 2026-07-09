#!/bin/bash
# 启动 CT AI 推理服务（FastAPI，默认 9810）
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
source "$ROOT/scripts/env.sh"
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
export AI_LOG_PATH="${AI_LOG_PATH:-$LOG_FILE_AI}"

export AI_WORKERS="${AI_WORKERS:-1}"
# GPU 并发：auto=按显存自动推算；也可手动设为 1、2 等整数
export AI_GPU_CONCURRENT="${AI_GPU_CONCURRENT:-auto}"
# scheme-b 融合分析超时（秒），默认 2 小时
export AI_FUSION_TIMEOUT_SEC="${AI_FUSION_TIMEOUT_SEC:-7200}"

pkill -f "ai-service/run.py" 2>/dev/null || true
pkill -f "ai-service/.conda/bin/python run.py" 2>/dev/null || true
pkill -f "ai-service/.venv/bin/python run.py" 2>/dev/null || true
pkill -f "ai-service.*run.py" 2>/dev/null || true
# 清理旧进程（cwd 可能不在 ai-service 目录，pkill 匹配不到）
fuser -k "${AI_PORT}/tcp" 2>/dev/null || true
sleep 1
nohup "$PY" run.py >> "$LOG_FILE_AI" 2>&1 &
sleep 3
curl -sf "http://127.0.0.1:${AI_PORT}/health" | "$PY" -c "import sys,json; d=json.load(sys.stdin); print('AI 服务已启动:', 'http://127.0.0.1:${AI_PORT}'); print('  GPU并发槽位:', d.get('gpuConcurrentSlots'), '(mode:', d.get('gpuConcurrentMode',''), ')'); [print('  -', g.get('name'), g.get('vramTotalGb'), 'GB, slots=', g.get('recommendedSlots')) for g in d.get('gpuDevices',[])]" 2>/dev/null || { curl -sf "http://127.0.0.1:${AI_PORT}/health" && echo "" && echo "AI 服务已启动: http://127.0.0.1:${AI_PORT}"; }
