#!/bin/bash
# ==============================================================================
# WestChina-Cloud 一键编译
# 用法: bash build_all.sh [frontend-only]
# ==============================================================================
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
source "$ROOT/scripts/env.sh"
DEP="$DEPLOY_DIR"
UI="$ROOT/westChina-ui"

# ---------- 后端 Maven 编译 ----------
if [ "${1:-}" != "frontend-only" ]; then
  echo "=== 同步 SQL 脚本 ==="
  bash "$ROOT/scripts/sync-sql.sh" 2>/dev/null || log_warn "sync-sql 跳过"

  if [ -z "$MAVEN_HOME" ] || ! command -v mvn >/dev/null 2>&1; then
    log_error "Maven 未安装。请将 Maven 放到 $HOME/tools/maven/ 或安装: sudo apt install maven"
    log_info "跳过 Java 编译，使用已有的 JAR 包"
  else
    echo "=== 编译后端 (Maven) ==="
    cd "$ROOT"
    mvn clean package -Dmaven.test.skip=true -q

    echo "=== 复制 JAR ==="
    for jar in \
      westChina-gateway/target/westChina-gateway.jar \
      westChina-auth/target/westChina-auth.jar \
      westChina-modules/westChina-system/target/westChina-modules-system.jar \
      westChina-modules/westChina-tenant/target/westChina-modules-tenant.jar \
      westChina-modules/westChina-ct/target/westChina-modules-ct.jar \
      westChina-modules/westChina-file/target/westChina-modules-file.jar \
      westChina-modules/westChina-gen/target/westChina-modules-gen.jar \
      westChina-modules/westChina-job/target/westChina-modules-job.jar \
      westChina-visual/westChina-monitor/target/westChina-visual-monitor.jar; do
      [ -f "$ROOT/$jar" ] && cp "$ROOT/$jar" "$DEP/" && log_info "  $(basename $jar)"
    done
  fi
fi

# ---------- 前端 npm 编译 ----------
echo "=== 编译前端 ==="
build_frontend() {
  local mod="$1"
  log_info "编译 $mod..."
  cd "$UI/$mod"
  npm install --legacy-peer-deps --silent 2>/dev/null || npm install --legacy-peer-deps
  if [ -f "./node_modules/.bin/vue-cli-service" ]; then
    ./node_modules/.bin/vue-cli-service build
  else
    npx vue-cli-service build
  fi
  mkdir -p "$DEP/ui-dist/$mod"
  rm -rf "$DEP/ui-dist/$mod"/*
  cp -r dist/* "$DEP/ui-dist/$mod/"
}

for mod in main administrator ct; do
  build_frontend "$mod"
done

echo ""
echo "=== 编译完成 ==="
ls -lh "$DEP"/*.jar 2>/dev/null || true
echo "前端:"
ls -d "$DEP"/ui-dist/*/ 2>/dev/null
