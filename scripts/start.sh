#!/bin/bash
# 启动：中间件 + 后端 + 前端
set -e
source "$(dirname "$0")/env.sh"

MODE="${1:-core}"   # core | all

echo "=== 启动 Docker 中间件 ==="
cd "$PROJECT_ROOT/dockerOfMy"
docker compose up -d

echo "等待 Nacos..."
for i in $(seq 1 30); do
  curl -sf http://127.0.0.1:8848/nacos/ >/dev/null && break
  sleep 2
done

echo "=== 启动后端 ($MODE) ==="
cd "$PROJECT_ROOT/deploymentServer"
sed -i 's/\r$//' runlocal.sh 2>/dev/null || true
bash runlocal.sh start "$MODE"

echo "=== 启动 AI 推理服务 (端口 9810) ==="
sed -i 's/\r$//' "$PROJECT_ROOT/scripts/start-ai.sh" 2>/dev/null || true
bash "$PROJECT_ROOT/scripts/start-ai.sh" || echo "警告: AI 服务启动失败，可先执行 scripts/start-ai.sh"

echo "=== 启动前端 (端口 5000) ==="
pkill -f "local-ui-server.js" 2>/dev/null || true
nohup node "$PROJECT_ROOT/deploymentServer/local-ui-server.js" \
  >> "$LOG_FILE_UI" 2>&1 &

sleep 2
echo ""
echo "=========================================="
echo "  管理系统:     http://127.0.0.1:5000/main/"
echo "  租户管理:     http://127.0.0.1:5000/administrator/"
echo "  阅片系统(CT): http://127.0.0.1:5000/ct/  (后端需 start all)"
echo "  Nacos:        http://127.0.0.1:8848/nacos"
echo "  API 网关:     http://127.0.0.1:8080"
echo "=========================================="
