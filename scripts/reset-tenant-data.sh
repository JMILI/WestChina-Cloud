#!/bin/bash
# 硬删除租户测试数据：MinIO 桶、租户子库、xy-cloud 中租户/桶/数据源记录
# 保留 xy-cloud 主库（superadmin 租户 -1 及系统表）
# 用法: bash scripts/reset-tenant-data.sh [--yes]
set -eo pipefail

CONFIRM="${1:-}"
if [[ "$CONFIRM" != "--yes" ]]; then
  echo "将执行："
  echo "  1. 删除 MinIO 桶: common ren renmin super superadmin xiehe"
  echo "  2. DROP 数据库: xy-renmin xy-xiehe xy-cloud1 xy-cloud2 xy-cloud-init-test xy-cloud-test"
  echo "  3. 清理 xy-cloud 租户/桶/数据源/分库记录（保留 tenant_id=-1）"
  echo "  4. 清空 xy-cloud 中 CT/素材业务表"
  echo "  5. 清理 Redis 租户缓存"
  echo ""
  echo "确认请执行: bash scripts/reset-tenant-data.sh --yes"
  exit 0
fi

mysql_exec() {
  docker exec -i westChina-mysql mysql -uroot -p123456 "$@"
}

echo "=== 1/5 MinIO 桶 ==="
docker exec westChina-minio mc alias set local http://localhost:9000 admin admin123456 >/dev/null 2>&1 || true
for bucket in common ren renmin super superadmin xiehe; do
  if docker exec westChina-minio mc ls "local/$bucket" >/dev/null 2>&1; then
    echo "  删除桶: $bucket"
    docker exec westChina-minio mc rb --force "local/$bucket"
  else
    echo "  跳过（不存在）: $bucket"
  fi
done

echo "=== 2/5 DROP 租户子库 ==="
for db in xy-renmin xy-xiehe xy-cloud1 xy-cloud2 xy-cloud-init-test xy-cloud-test; do
  if mysql_exec -e "SHOW DATABASES LIKE '$db';" 2>/dev/null | grep -q "$db"; then
    echo "  DROP DATABASE \`$db\`"
    mysql_exec -e "DROP DATABASE \`$db\`;"
  else
    echo "  跳过（不存在）: $db"
  fi
done

echo "=== 3/5 清理 xy-cloud 租户元数据 ==="
mysql_exec xy-cloud <<'SQL'
SET FOREIGN_KEY_CHECKS = 0;

DELETE FROM xy_tenant_bucket;
DELETE FROM xy_tenant_separation WHERE write_id != 1;
DELETE FROM xy_tenant_strategy_source WHERE strategy_id != 1;
DELETE FROM xy_tenant_strategy WHERE strategy_id != 1;
DELETE FROM xy_tenant_source WHERE source_id != 1;
DELETE FROM xy_tenant WHERE tenant_id != -1;

SET FOREIGN_KEY_CHECKS = 1;
SQL

echo "=== 4/5 清空 xy-cloud 业务数据表 ==="
mysql_exec xy-cloud <<'SQL'
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE ct_dicom;
TRUNCATE TABLE ct_patients;
TRUNCATE TABLE dicom_maker;
TRUNCATE TABLE dicom_ai_lesion;
TRUNCATE TABLE xy_material;
TRUNCATE TABLE xy_material_folder;
SET FOREIGN_KEY_CHECKS = 1;
SQL

echo "=== 5/5 Redis 租户缓存 ==="
for key in login_enterprise:renmin login_enterprise:xiehe login_enterprise:ren; do
  docker exec westChina-redis redis-cli DEL "$key" >/dev/null 2>&1 || true
done
docker exec westChina-redis redis-cli --scan --pattern 'sys_enterprise:2072*' 2>/dev/null | while read -r key; do
  [[ -n "$key" ]] && docker exec westChina-redis redis-cli DEL "$key" >/dev/null
done

echo ""
echo "重置完成。建议重启 system/tenant 服务后重新登录 superadmin 创建租户。"
echo "  cd deploymentServer && sh runall.sh restart system tenant"
