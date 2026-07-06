#!/bin/bash
# 停止：前端 + 后端 +（可选）中间件
source "$(dirname "$0")/env.sh"

STOP_DOCKER="${1:-}"   # 传 docker 则同时停中间件

echo "=== 停止前端 ==="
pkill -f "local-ui-server.js" 2>/dev/null || true

echo "=== 停止后端 JAR ==="
cd "$PROJECT_ROOT/deploymentServer"
bash runlocal.sh stop

if [ "$STOP_DOCKER" = "docker" ]; then
  echo "=== 停止 Docker 中间件 ==="
  cd "$PROJECT_ROOT/dockerOfMy"
  docker compose stop
fi

echo "已停止"
