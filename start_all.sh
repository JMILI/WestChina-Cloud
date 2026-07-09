#!/bin/bash
# ==============================================================================
# WestChina-Cloud 一键启动全部服务
# 
# 启动顺序：Docker中间件 → 后端Java → AI推理 → 前端UI
# 用法: bash start_all.sh [core|all|ai-only|ui-only]
#   core  - 仅启动核心服务(中间件+后端核心+AI+UI) [默认]
#   all   - 启动全部服务(含file/gen/job/monitor)
#   ai-only   - 仅重启AI服务
#   ui-only   - 仅重启前端
#
# 环境变量:
#   SEALTUN_AUTO_START=0  跳过 Sealtun 隧道自动恢复（默认开启）
# ==============================================================================
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
source "$ROOT/scripts/env.sh"
MODE="${1:-core}"

echo "============================================"
echo "  WestChina-Cloud 一键启动 ($MODE)"
echo "============================================"

# ─────────────────────────────────────────────────────
# 1. Docker 中间件 (MySQL/Redis/RabbitMQ/MinIO/Nacos)
# ─────────────────────────────────────────────────────
if port_listening 3306 && port_listening 6379 && port_listening 8848; then
  log_info "Docker 中间件已在运行"
else
  log_info "启动 Docker 中间件..."
  cd "$DOCKER_DIR"
  if [ -n "$DOCKER_COMPOSE" ]; then
    $DOCKER_COMPOSE up -d mysql westChina-redis westChina-rabbit westChina-minio westChina-nacos 2>/dev/null || \
    $DOCKER_COMPOSE up -d 2>/dev/null || \
    $DOCKER_COMPOSE up -d
  fi
  wait_port 3306 30 MySQL
  wait_port 6379 10 Redis
  wait_port 8848 60 Nacos
  log_info "中间件已就绪"
fi

# ─────────────────────────────────────────────────────
# 2. 后端 Java 服务
# ─────────────────────────────────────────────────────
log_info "启动后端 Java 服务..."
cd "$DEPLOY_DIR"
# 修复 Windows 换行符
sed -i 's/\r$//' runlocal.sh 2>/dev/null || true

if [ "$MODE" = "all" ]; then
  bash runlocal.sh start all
else
  bash runlocal.sh start core
fi

# ─────────────────────────────────────────────────────
# 3. AI 推理服务 (Python FastAPI, 端口 9810)
# ─────────────────────────────────────────────────────
if [ "$MODE" != "ui-only" ]; then
  log_info "启动 AI 推理服务..."
  if port_listening 9810; then
    log_info "AI 服务已在运行"
  else
    # 清理旧进程
    pkill -f "ai-service.*run.py" 2>/dev/null || true
    pkill -f "uvicorn.*9810" 2>/dev/null || true
    sleep 2

    if [ -x "$AI_PYTHON" ]; then
      cd "$ROOT/ai-service"
      export AI_LOG_PATH="${AI_LOG_PATH:-$LOG_FILE_AI}"
      nohup "$AI_PYTHON" run.py >> "$LOG_FILE_AI" 2>&1 < /dev/null &
      wait_port 9810 20 "AI推理服务"
    else
      log_error "Python 环境未找到，请先运行 scripts/setup_env.sh"
    fi
  fi
fi

# ─────────────────────────────────────────────────────
# 4. 前端 UI (Node.js, 端口 5000)
# ─────────────────────────────────────────────────────
if [ "$MODE" != "ai-only" ]; then
  log_info "启动前端 UI..."
  if port_listening 5000; then
    log_info "前端已在运行"
  else
    pkill -f "local-ui-server.js" 2>/dev/null || true
    sleep 1
    cd "$DEPLOY_DIR"
    node local-ui-server.js >> "$LOG_FILE_UI" 2>&1 < /dev/null &
    wait_port 5000 5 "前端UI"
  fi
fi

# ─────────────────────────────────────────────────────
# 5. Sealtun 隧道（重启后恢复，供同事远程访问）
# ─────────────────────────────────────────────────────
if [ "${SEALTUN_AUTO_START:-1}" != "0" ] && [ "$MODE" != "ai-only" ]; then
  if [ -f "$ROOT/scripts/start-sealtun.sh" ]; then
    log_info "恢复 Sealtun 远程隧道..."
    bash "$ROOT/scripts/start-sealtun.sh" || log_warn "Sealtun 隧道未恢复（可稍后执行: bash scripts/start-sealtun.sh）"
  fi
fi

# ─────────────────────────────────────────────────────
# 6. 验证
# ─────────────────────────────────────────────────────
echo ""
echo "============================================"
echo "  服务状态检查"
echo "============================================"

check() {
  local label="$1" url="$2"
  local code=$(curl -sf -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
  if [ "$code" != "000" ]; then
    echo -e "  \033[32m✓\033[0m $label ($code)"
  else
    echo -e "  \033[31m✗\033[0m $label"
  fi
}

check "Nacos       http://127.0.0.1:8848" "http://127.0.0.1:8848/nacos/"
check "Gateway     http://127.0.0.1:8080" "http://127.0.0.1:8080/"
check "System      http://127.0.0.1:9600" "http://127.0.0.1:9600/"
check "CT阅片     http://127.0.0.1:9800" "http://127.0.0.1:9800/"
check "AI推理     http://127.0.0.1:9810" "http://127.0.0.1:9810/health"
check "前端UI     http://127.0.0.1:5000" "http://127.0.0.1:5000/ct/"

echo ""
echo "============================================"
echo "  访问地址"
echo "============================================"
echo "  管理系统:    http://127.0.0.1:5000/main/"
echo "  租户管理:    http://127.0.0.1:5000/administrator/"
echo "  阅片系统:    http://127.0.0.1:5000/ct/"
echo "  Nacos:       http://127.0.0.1:8848/nacos  (nacos/nacos)"
echo "  MinIO:       http://127.0.0.1:9001  (admin/admin123456)"
echo "  RabbitMQ:    http://127.0.0.1:15672  (guest/guest)"
echo "============================================"
