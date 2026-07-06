#!/bin/bash
# 运维用手动初始化租户子库（与界面「新增数据源」效果相同：建库 + slave-init.sql）
# 正常流程请在管理界面添加数据源，由 DSUtils.initSlaveDatabase() 自动执行
# 用法: bash scripts/init-tenant-db.sh <数据库名> [docker]
set -e
source "$(dirname "$0")/env.sh"

DB_NAME="${1:?用法: init-tenant-db.sh <数据库名> [docker]}"
MODE="${2:-local}"
SLAVE_INIT="$PROJECT_ROOT/westsql/slave-init.sql"

if [[ ! -f "$SLAVE_INIT" ]]; then
  echo "缺少 $SLAVE_INIT" >&2
  exit 1
fi

mysql_exec() {
  if [[ "$MODE" == "docker" ]]; then
    docker exec -i westChina-mysql mysql -uroot -p123456 "$@"
  else
    mysql "$@"
  fi
}

echo "初始化租户子库: $DB_NAME"
mysql_exec -e "CREATE DATABASE IF NOT EXISTS \`$DB_NAME\` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;"
mysql_exec "$DB_NAME" < "$SLAVE_INIT"
echo "  完成: $DB_NAME（17 张表）"
