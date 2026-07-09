#!/usr/bin/env bash
# 重启 AI 服务并跑方案 B 验收（代码变更后执行）
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT_ROOT="$(cd "$ROOT/.." && pwd)"
# shellcheck source=../../scripts/env.sh
source "$PROJECT_ROOT/scripts/env.sh"
PY="${AI_PYTHON:-$ROOT/.conda/bin/python}"
LOG="${AI_LOG:-$LOG_FILE_AI}"

echo "=== Restart Scheme B (AI service) ==="

pkill -f "ai-service.*run.py" 2>/dev/null || true
pkill -f "uvicorn.*9810" 2>/dev/null || true
sleep 2

cd "$ROOT"
nohup "$PY" run.py >> "$LOG" 2>&1 < /dev/null &
echo "AI starting (log: $LOG)"

for i in $(seq 1 30); do
  if curl -sf http://127.0.0.1:9810/health >/dev/null 2>&1; then
    echo "AI ready after ${i}s"
    break
  fi
  sleep 1
done

curl -s http://127.0.0.1:9810/health | head -c 120
echo ""

bash "$ROOT/scripts/scheme_b_acceptance.sh"
echo "=== Done ==="
