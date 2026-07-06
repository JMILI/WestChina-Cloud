#!/bin/bash
# ==============================================================================
# WestChina-Cloud 环境初始化（新 Ubuntu 系统一键构建开发环境）
source "$(dirname "$0")/env.sh" 2>/dev/null || { log_info() { echo "[INFO] $*"; }; log_warn() { echo "[WARN] $*"; }; log_error() { echo "[ERROR] $*"; }; }
#
# 步骤：
#   1. 安装系统依赖 (Docker, Java 8, Maven, Node 18+, Python 3.11)
#   2. 拉取 Docker 镜像并初始化数据库
#   3. 创建 Python 虚拟环境并安装 AI 依赖
#   4. 可选：安装 AI 引擎 (TotalSegmentator / MONAI / GPU PyTorch)
#
# 用法: bash scripts/setup_env.sh [full|ai-engines|gpu]
#   (无参数)  - 基础环境 (Docker + Java + Node + MySQL初始化)
#   ai-engines - 额外安装 AI 推理引擎
#   gpu        - 额外安装 GPU 版 PyTorch
#   full       - 全部安装
# ==============================================================================
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MODE="${1:-base}"

echo "============================================"
echo "  WestChina-Cloud 环境初始化 ($MODE)"
echo "============================================"

# ---------- 系统依赖 ----------
install_system_deps() {
  log_info "安装系统依赖..."
  sudo apt update -qq

  # Docker
  if ! command -v docker >/dev/null 2>&1; then
    log_info "安装 Docker..."
    curl -fsSL https://get.docker.com | sudo bash
    sudo usermod -aG docker "$USER"
  fi

  # Java 8
  if [ ! -d "$HOME/tools/jdk8" ] && ! command -v java >/dev/null 2>&1; then
    log_info "安装 Java 8..."
    mkdir -p "$HOME/tools"
    # 使用 Eclipse Temurin JDK 8
    wget -q "https://github.com/adoptium/temurin8-binaries/releases/download/jdk8u432-b06/OpenJDK8U-jdk_x64_linux_hotspot_8u432b06.tar.gz" -O /tmp/jdk8.tar.gz
    tar xzf /tmp/jdk8.tar.gz -C "$HOME/tools"
    mv "$HOME/tools"/jdk8u* "$HOME/tools/jdk8" 2>/dev/null || true
    rm /tmp/jdk8.tar.gz
    export JAVA_HOME="$HOME/tools/jdk8"
    export PATH="$JAVA_HOME/bin:$PATH"
  fi

  # Maven (可选 — 编译时才需要)
  if [ ! -d "$HOME/tools/maven" ] && ! command -v mvn >/dev/null 2>&1; then
    log_info "安装 Maven 3.8..."
    wget -q "https://dlcdn.apache.org/maven/maven-3/3.8.8/binaries/apache-maven-3.8.8-bin.tar.gz" -O /tmp/maven.tar.gz
    mkdir -p "$HOME/tools/maven"
    tar xzf /tmp/maven.tar.gz -C "$HOME/tools/maven" --strip-components=1
    rm /tmp/maven.tar.gz
    export MAVEN_HOME="$HOME/tools/maven"
    export PATH="$MAVEN_HOME/bin:$PATH"
  fi

  # Node.js 18+
  if ! command -v node >/dev/null 2>&1; then
    log_info "安装 Node.js 18..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt install -y nodejs
  fi

  # Python 3.11 (用于 AI 服务)
  if ! command -v python3 >/dev/null 2>&1; then
    sudo apt install -y python3 python3-pip python3-venv
  fi

  log_info "系统依赖安装完成"
}

# ---------- Docker 中间件 + 数据库初始化 ----------
init_docker_services() {
  log_info "启动 Docker 中间件..."
  cd "$ROOT/dockerOfMy"

  if ! docker compose version >/dev/null 2>&1; then
    if command -v docker-compose >/dev/null 2>&1; then
      docker-compose up -d
    else
      log_error "Docker 未安装，请先运行 Docker 安装步骤"
      return 1
    fi
  else
    docker compose up -d
  fi
  # 等待 MySQL 就绪
  for i in $(seq 1 60); do
    docker exec westChina-mysql mysqladmin ping -uroot -p123456 --silent 2>/dev/null && break
    sleep 2
  done
  log_info "MySQL 已就绪"

  # 初始化数据库
  log_info "初始化数据库表..."
  for sql in xy-cloud.sql xy-config.sql xy_seata.sql; do
    case "$sql" in
      xy-cloud.sql)   target_db="xy-cloud" ;;
      xy-config.sql)  target_db="xy-config" ;;
      xy_seata.sql)   target_db="xy-seata" ;;
    esac
    log_info "  导入 $sql → $target_db"
    docker exec -i westChina-mysql mysql -uroot -p123456 -e "CREATE DATABASE IF NOT EXISTS \`$target_db\` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;" 2>/dev/null
    docker exec -i westChina-mysql mysql -uroot -p123456 "$target_db" < "$ROOT/dockerOfMy/mysql/db/$sql" 2>/dev/null
  done
  log_info "数据库初始化完成（租户子库请在管理界面「新增数据源」时自动创建）"

  # 本机适配：替换 host 为 127.0.0.1
  bash "$ROOT/scripts/init-local-db.sh" 2>/dev/null || log_warn "init-local-db 部分失败（可手动执行）"
}

# ---------- Python AI 环境 ----------
init_python_env() {
  log_info "创建 Python 虚拟环境..."
  cd "$ROOT/ai-service"
  if [ ! -d ".conda" ] && [ ! -d ".venv" ]; then
    python3 -m venv .venv
    .venv/bin/pip install -U pip
    .venv/bin/pip install -r requirements.txt
    log_info "Python 基础依赖安装完成"
  else
    log_info "Python 环境已存在"
  fi
}

# ---------- 安装 AI 推理引擎 ----------
install_ai_engines() {
  log_info "安装 AI 推理引擎 (TotalSegmentator + MONAI)..."
  bash "$ROOT/scripts/install-ai-engines.sh" || log_warn "AI 引擎安装部分失败"
}

install_gpu_pytorch() {
  log_info "安装 GPU 版 PyTorch..."
  bash "$ROOT/scripts/install-pytorch-gpu.sh" || log_warn "GPU PyTorch 安装部分失败"
}

# ---------- 执行 ----------
case "$MODE" in
  base)
    install_system_deps
    init_docker_services
    init_python_env
    ;;
  ai-engines)
    init_python_env
    install_ai_engines
    ;;
  gpu)
    init_python_env
    install_gpu_pytorch
    ;;
  full)
    install_system_deps
    init_docker_services
    init_python_env
    install_ai_engines
    install_gpu_pytorch
    ;;
  *)
    echo "用法: bash scripts/setup_env.sh [base|ai-engines|gpu|full]"
    exit 1
    ;;
esac

echo ""
echo "============================================"
echo "  环境初始化完成"
echo "============================================"
echo "  下一步："
echo "  1. 编译:  bash build_all.sh"
echo "  2. 启动:  bash start_all.sh"
echo "============================================"
