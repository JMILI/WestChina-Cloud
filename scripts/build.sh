#!/bin/bash
# 编译后端 + 前端，并复制到 deploymentServer
set -e
source "$(dirname "$0")/env.sh"

DEP="$PROJECT_ROOT/deploymentServer"
UI="$PROJECT_ROOT/westChina-ui"
export NODE_OPTIONS="${NODE_OPTIONS:---openssl-legacy-provider}"

build_frontend() {
  local mod="$1"
  echo "--- $mod ---"
  cd "$UI/$mod"
  npm install --legacy-peer-deps
  ./node_modules/.bin/vue-cli-service build
  mkdir -p "$DEP/ui-dist/$mod"
  rm -rf "$DEP/ui-dist/$mod"/*
  cp -r dist/* "$DEP/ui-dist/$mod/"
}

if [[ "${1:-}" != "frontend-only" ]]; then
  echo "=== 同步 SQL 脚本 ==="
  bash "$PROJECT_ROOT/scripts/sync-sql.sh"

  echo "=== 编译后端 (Maven) ==="
  cd "$PROJECT_ROOT"
  mvn clean package -Dmaven.test.skip=true

  echo "=== 复制 JAR ==="
  cp "$PROJECT_ROOT/westChina-gateway/target/westChina-gateway.jar" "$DEP/"
  cp "$PROJECT_ROOT/westChina-auth/target/westChina-auth.jar" "$DEP/"
  cp "$PROJECT_ROOT/westChina-modules/westChina-system/target/westChina-modules-system.jar" "$DEP/"
  cp "$PROJECT_ROOT/westChina-modules/westChina-tenant/target/westChina-modules-tenant.jar" "$DEP/"
  cp "$PROJECT_ROOT/westChina-modules/westChina-ct/target/westChina-modules-ct.jar" "$DEP/"
  cp "$PROJECT_ROOT/westChina-modules/westChina-file/target/westChina-modules-file.jar" "$DEP/"
  cp "$PROJECT_ROOT/westChina-modules/westChina-gen/target/westChina-modules-gen.jar" "$DEP/"
  cp "$PROJECT_ROOT/westChina-modules/westChina-job/target/westChina-modules-job.jar" "$DEP/"
  cp "$PROJECT_ROOT/westChina-visual/westChina-visual-monitor/target/westChina-visual-monitor.jar" "$DEP/"
fi

echo "=== 编译前端 (publicPath: /main/ /administrator/ /ct/) ==="
for mod in main administrator ct; do
  build_frontend "$mod"
done

echo "=== 构建完成 ==="
ls -lh "$DEP"/*.jar 2>/dev/null || true
ls "$DEP/ui-dist/"
