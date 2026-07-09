#!/usr/bin/env bash
# 等待 Sealos 登录完成后自动创建隧道
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
source "$ROOT/scripts/env.sh"
LOG="$LOG_FILE_SEALTUN"

echo "[$(date)] 等待 Sealtun 登录..." | tee "$LOG"
for i in $(seq 1 40); do
  if npx sealtun status 2>/dev/null | grep -q "Logged in: yes"; then
    echo "[$(date)] 已登录" | tee -a "$LOG"
    break
  fi
  sleep 15
done

if ! npx sealtun status 2>/dev/null | grep -q "Logged in: yes"; then
  echo "[$(date)] 超时：仍未登录，请先在浏览器完成 sealtun login 授权" | tee -a "$LOG"
  exit 1
fi

if ! curl -sf -o /dev/null "http://127.0.0.1:5000/main/"; then
  bash start_all.sh ui-only >> "$LOG" 2>&1
fi

echo "[$(date)] 创建隧道（无 Basic Auth）..." | tee -a "$LOG"
npx sealtun expose 5000 2>&1 | tee -a "$LOG"
