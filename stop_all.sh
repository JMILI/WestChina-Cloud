#!/bin/bash
# ==============================================================================
# WestChina-Cloud 一键停止
# 用法: bash stop_all.sh [docker]   — 加 docker 参数则同时停止中间件
# ==============================================================================
ROOT="$(cd "$(dirname "$0")" && pwd)"
source "$ROOT/scripts/env.sh"
STOP_DOCKER="${1:-}"

echo "=== 停止前端 UI ==="
pkill -f "local-ui-server.js" 2>/dev/null && log_info "前端已停止" || log_info "前端未运行"

echo "=== 停止 AI 推理服务 ==="
pkill -f "ai-service.*run.py" 2>/dev/null || true
pkill -f "uvicorn.*9810" 2>/dev/null || true
log_info "AI服务已停止"

echo "=== 停止后端 Java 服务 ==="
cd "$DEPLOY_DIR"
sed -i 's/\r$//' runlocal.sh 2>/dev/null || true
bash runlocal.sh stop 2>/dev/null || pkill -f 'westChina-.*\.jar' 2>/dev/null
log_info "后端已停止"

if [ "$STOP_DOCKER" = "docker" ]; then
  echo "=== 停止 Docker 中间件 ==="
  cd "$DOCKER_DIR"
  if [ -n "$DOCKER_COMPOSE" ]; then
    $DOCKER_COMPOSE stop 2>/dev/null
  fi
  log_info "中间件已停止"
fi

echo ""
echo "全部服务已停止"
