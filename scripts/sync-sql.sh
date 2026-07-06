#!/bin/bash
# 以 westsql/slave-init.sql 为唯一权威来源，同步到 Java classpath
set -e
source "$(dirname "$0")/env.sh"

WESTSQL="$PROJECT_ROOT/westsql"
SLAVE_INIT="$WESTSQL/slave-init.sql"
CLASSPATH_SQL="$PROJECT_ROOT/westChina-common/westChina-common-datasource/src/main/resources/sql/slave-init.sql"
DOCKER_SLAVE="$PROJECT_ROOT/dockerOfMy/mysql/db/slave-init.sql"

if [[ ! -f "$SLAVE_INIT" ]]; then
  echo "缺少 $SLAVE_INIT" >&2
  exit 1
fi

echo "=== 同步 slave-init.sql → classpath ==="
mkdir -p "$(dirname "$CLASSPATH_SQL")"
cp "$SLAVE_INIT" "$CLASSPATH_SQL"

echo "=== 同步 slave-init.sql → docker 参考副本（供运维手动补库）==="
cp "$SLAVE_INIT" "$DOCKER_SLAVE"

echo "=== SQL 同步完成 ==="
echo "  权威源: westsql/slave-init.sql (17 张表)"
echo "  运行时: westChina-common-datasource/.../sql/slave-init.sql"
echo "  租户子库: 管理界面「新增数据源」时自动建库建表（DSUtils + slave-init.sql）"
