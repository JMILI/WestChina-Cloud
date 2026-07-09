#!/bin/bash
# 项目运行时中间文件统一目录（日志、缓存、临时文件）
# 由 scripts/env.sh source；Python 侧见 ai-service/app/log_paths.py

: "${PROJECT_ROOT:?PROJECT_ROOT required}"

# 防止 Windows CRLF 或旧 shell 会话污染路径
_strip_cr() { printf '%s' "$1" | tr -d '\r'; }
PROJECT_ROOT="$(_strip_cr "$PROJECT_ROOT")"

export LOG_ROOT="$(_strip_cr "${LOG_ROOT:-$PROJECT_ROOT/logs}")"

export LOG_DIR_AI="$(_strip_cr "${LOG_DIR_AI:-$LOG_ROOT/ai-service}")"
export LOG_DIR_AI_CACHE="$(_strip_cr "${LOG_DIR_AI_CACHE:-$LOG_DIR_AI/cache/volumes}")"
export LOG_DIR_AI_TMP="$(_strip_cr "${LOG_DIR_AI_TMP:-$LOG_DIR_AI/tmp}")"
export LOG_DIR_AI_E2E="$(_strip_cr "${LOG_DIR_AI_E2E:-$LOG_DIR_AI/e2e}")"
export LOG_DIR_AI_REPORTS="$(_strip_cr "${LOG_DIR_AI_REPORTS:-$LOG_DIR_AI/reports}")"
export LOG_FILE_AI="$(_strip_cr "${LOG_DIR_AI}/ai-service.log")"

export LOG_DIR_JAVA="$(_strip_cr "${LOG_DIR_JAVA:-$LOG_ROOT/java}")"
export LOG_DIR_UI="$(_strip_cr "${LOG_DIR_UI:-$LOG_ROOT/ui}")"
export LOG_FILE_UI="$(_strip_cr "${LOG_DIR_UI}/ui.log")"

export LOG_DIR_DOCKER="$(_strip_cr "${LOG_DIR_DOCKER:-$LOG_ROOT/docker}")"
export LOG_DIR_DOCKER_NACOS="$(_strip_cr "${LOG_DIR_DOCKER_NACOS:-$LOG_DIR_DOCKER/nacos}")"
export LOG_DIR_DOCKER_MYSQL="$(_strip_cr "${LOG_DIR_DOCKER_MYSQL:-$LOG_DIR_DOCKER/mysql}")"
export LOG_DIR_DOCKER_RABBITMQ="$(_strip_cr "${LOG_DIR_DOCKER_RABBITMQ:-$LOG_DIR_DOCKER/rabbitmq}")"

export LOG_DIR_SEALTUN="$(_strip_cr "${LOG_DIR_SEALTUN:-$LOG_ROOT/sealtun}")"
export LOG_FILE_SEALTUN="$(_strip_cr "${LOG_DIR_SEALTUN}/expose.log")"

export LOG_DIR_FILE_SERVICE="$(_strip_cr "${LOG_DIR_FILE_SERVICE:-$LOG_ROOT/file-service}")"
export LOG_DIR_UPLOAD="$(_strip_cr "${LOG_DIR_UPLOAD:-$LOG_DIR_FILE_SERVICE/uploadPath}")"

# 兼容旧变量名（逐步废弃 deploymentServer/logs）
export LOG_DIR="$LOG_ROOT"

ensure_log_dirs() {
  mkdir -p \
    "$LOG_DIR_AI" "$LOG_DIR_AI_CACHE" "$LOG_DIR_AI_TMP" "$LOG_DIR_AI_E2E" "$LOG_DIR_AI_REPORTS" \
    "$LOG_DIR_JAVA" "$LOG_DIR_UI" \
    "$LOG_DIR_DOCKER_NACOS" "$LOG_DIR_DOCKER_MYSQL" "$LOG_DIR_DOCKER_RABBITMQ" \
    "$LOG_DIR_SEALTUN" "$LOG_DIR_UPLOAD"
  # Java 进程 cwd=deploymentServer，logback 使用相对路径 logs/…
  mkdir -p "$PROJECT_ROOT/deploymentServer"
  ln -sfn "$LOG_DIR_JAVA" "$PROJECT_ROOT/deploymentServer/logs"
}

ensure_log_dirs
