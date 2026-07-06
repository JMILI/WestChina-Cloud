#!/bin/bash
# ==============================================================================
# WestChina-Cloud 环境配置脚本
# 
# 被其他脚本 source 使用，自动检测本机已安装的工具路径。
# 支持：自动检测 / tools目录 / sdkman / 标准安装路径
# ==============================================================================

export PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# ---------- Java (JDK 8) ----------
if [ -z "$JAVA_HOME" ]; then
  # 优先级：tools 目录 > 系统安装 > sdkman
  if [ -d "$HOME/tools/jdk8" ]; then
    export JAVA_HOME="$HOME/tools/jdk8"
  elif [ -d "$HOME/tools/jdk1.8" ]; then
    export JAVA_HOME="$HOME/tools/jdk1.8"
  elif [ -n "$(command -v java 2>/dev/null)" ]; then
    export JAVA_HOME="$(dirname "$(dirname "$(readlink -f "$(which java)")")")"
  elif [ -d "$HOME/.sdkman/candidates/java/current" ]; then
    export JAVA_HOME="$HOME/.sdkman/candidates/java/current"
  fi
fi
export PATH="$JAVA_HOME/bin:$PATH"

# ---------- Maven ----------
if [ -z "$MAVEN_HOME" ]; then
  if [ -d "$HOME/tools/maven/apache-maven"* ]; then
    export MAVEN_HOME="$(ls -d "$HOME"/tools/maven/apache-maven-* 2>/dev/null | head -1)"
  elif [ -d "$HOME/tools/maven" ] && [ -f "$HOME/tools/maven/bin/mvn" ]; then
    export MAVEN_HOME="$HOME/tools/maven"
  elif [ -n "$(command -v mvn 2>/dev/null)" ]; then
    export MAVEN_HOME="$(dirname "$(dirname "$(readlink -f "$(which mvn)")")")"
  fi
fi
[ -n "$MAVEN_HOME" ] && export PATH="$MAVEN_HOME/bin:$PATH"

# ---------- Node.js ----------
if [ -z "$NODE_HOME" ]; then
  if [ -n "$(command -v node 2>/dev/null)" ]; then
    export NODE_HOME="$(dirname "$(dirname "$(readlink -f "$(which node)")")")"
  elif [ -d "$HOME/.nvm/versions/node" ]; then
    export NODE_HOME="$(ls -d "$HOME"/.nvm/versions/node/v* 2>/dev/null | sort -V | tail -1)"
  fi
fi
[ -n "$NODE_HOME" ] && export PATH="$NODE_HOME/bin:$PATH"

# ---------- Python (AI 服务) ----------
if [ -x "$PROJECT_ROOT/ai-service/.conda/bin/python" ]; then
  export AI_PYTHON="$PROJECT_ROOT/ai-service/.conda/bin/python"
elif [ -x "$PROJECT_ROOT/ai-service/.venv/bin/python" ]; then
  export AI_PYTHON="$PROJECT_ROOT/ai-service/.venv/bin/python"
else
  export AI_PYTHON="python3"
fi

# ---------- Docker ----------
export DOCKER_COMPOSE="$(command -v docker 2>/dev/null) compose"
# 兼容旧版 docker-compose
if ! docker compose version >/dev/null 2>&1; then
  if command -v docker-compose >/dev/null 2>&1; then
    export DOCKER_COMPOSE="docker-compose"
  else
    export DOCKER_COMPOSE=""
  fi
fi

# ---------- 部署目录 ----------
export DEPLOY_DIR="$PROJECT_ROOT/deploymentServer"
export DOCKER_DIR="$PROJECT_ROOT/dockerOfMy"
export LOG_DIR="$DEPLOY_DIR/logs"
mkdir -p "$LOG_DIR"

# ---------- 端口定义 ----------
# MySQL: 3306, Redis: 6379, RabbitMQ: 5672/15672, Nacos: 8848
# MinIO: 9000/9001, Gateway: 8080, Auth: 9200, System: 9600
# CT: 9800, File: 9300, Tenant: 9700, Gen: 9400, Job: 9500, Monitor: 9100
# AI: 9810, UI: 5000

# ---------- 工具函数 ----------
log_info()  { echo -e "\033[32m[INFO]\033[0m $*"; }
log_warn()  { echo -e "\033[33m[WARN]\033[0m $*"; }
log_error() { echo -e "\033[31m[ERROR]\033[0m $*"; }

# 检查端口是否在监听
port_listening() {
  ss -tlnp 2>/dev/null | grep -q ":$1 " && return 0 || return 1
}

# 等待端口就绪
wait_port() {
  local port="$1" timeout="${2:-30}" label="${3:-服务}"
  log_info "等待 $label (端口 $port)..."
  for i in $(seq 1 "$timeout"); do
    port_listening "$port" && log_info "$label 已就绪" && return 0
    sleep 2
  done
  log_warn "$label 启动超时 ($port)"
  return 1
}
