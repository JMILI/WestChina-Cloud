#!/bin/bash
# 首次本机部署：把配置中的 westChinaBackend 改为 127.0.0.1
set -e
source "$(dirname "$0")/env.sh"

echo "[1/2] 更新 Nacos 配置库..."
docker exec westChina-mysql mysql -uroot -p123456 -e "
UPDATE \`xy-config\`.config_info SET content = REPLACE(content, 'westChinaBackend', '127.0.0.1');
UPDATE \`xy-config\`.config_info SET content = REPLACE(content, 'D:/westChina/uploadPath', '/tmp/westChina/uploadPath');
" 2>/dev/null

echo "[2/4] 更新业务库租户数据源与监控菜单外链..."
docker exec westChina-mysql mysql -uroot -p123456 -e "
UPDATE \`xy-cloud\`.xy_tenant_source SET url_prepend = REPLACE(url_prepend, 'westChinaBackend', '127.0.0.1');
UPDATE \`xy-cloud\`.xy_system SET route = 'http://127.0.0.1:5000/ct/' WHERE system_id = 1;
UPDATE \`xy-cloud\`.xy_system SET route = 'http://127.0.0.1:5000/administrator/' WHERE system_id = 2;
UPDATE \`xy-cloud\`.sys_menu SET path = REPLACE(path, 'westChinaBackend', '127.0.0.1') WHERE path LIKE '%westChinaBackend%';
UPDATE \`xy-cloud\`.sys_menu SET path = 'http://127.0.0.1:9100/login' WHERE menu_id = 20230;
" 2>/dev/null

echo "[2.5/4] 补全 CT 模块数据库表结构..."
docker exec westChina-mysql mysql -uroot -p123456 -e "
ALTER TABLE \`xy-cloud\`.ct_dicom
  ADD COLUMN IF NOT EXISTS dicom_ct_description varchar(1000) NULL COMMENT '备注' AFTER dicom_ct_count;
" 2>/dev/null || docker exec westChina-mysql mysql -uroot -p123456 -e "
ALTER TABLE \`xy-cloud\`.ct_dicom
  ADD COLUMN dicom_ct_description varchar(1000) NULL COMMENT '备注' AFTER dicom_ct_count;
" 2>/dev/null || true

docker exec westChina-mysql mysql -uroot -p123456 -e "
CREATE TABLE IF NOT EXISTS \`xy-cloud\`.dicom_maker (
  dicom_maker_id bigint NOT NULL COMMENT 'id',
  instance_uid varchar(500) NOT NULL COMMENT '单张图像instanceID',
  study_uid varchar(500) NULL DEFAULT NULL,
  series_uid varchar(500) NULL DEFAULT NULL,
  study_date varchar(30) NULL DEFAULT NULL,
  pat_card_id varchar(20) NULL DEFAULT NULL,
  patient_name varchar(1000) NULL DEFAULT NULL,
  maker_doctor varchar(50) NULL DEFAULT NULL,
  maker_enterprise_name varchar(50) NULL DEFAULT NULL,
  maker_time varchar(30) NULL DEFAULT NULL,
  maker_image_address varchar(500) NULL DEFAULT NULL,
  maker_description varchar(1000) NULL DEFAULT NULL,
  maker_image varchar(50) NULL DEFAULT NULL,
  maker_columns int NULL DEFAULT NULL,
  maker_rows int NULL DEFAULT NULL,
  maker_column_pixel_spacing double NULL DEFAULT NULL,
  maker_row_pixel_spacing double NULL DEFAULT NULL,
  maker_slope int NULL DEFAULT NULL,
  maker_intercept int NULL DEFAULT NULL,
  maker_window_center int NULL DEFAULT NULL,
  maker_window_width int NULL DEFAULT NULL,
  maker_is_dicom tinyint NULL DEFAULT NULL,
  maker_scale double NULL DEFAULT NULL,
  sort int UNSIGNED NOT NULL DEFAULT 0,
  create_by bigint NULL DEFAULT NULL,
  create_time datetime NULL DEFAULT CURRENT_TIMESTAMP,
  update_by bigint NULL DEFAULT NULL,
  update_time datetime NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  remark varchar(1000) NULL DEFAULT NULL,
  del_flag tinyint NOT NULL DEFAULT 0,
  tenant_id bigint NOT NULL,
  PRIMARY KEY (dicom_maker_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='病人标记过的dicom图像表';
" 2>/dev/null

docker exec westChina-mysql mysql -uroot -p123456 -e "
CREATE TABLE IF NOT EXISTS \`xy-cloud\`.dicom_ai_lesion (
  dicom_ai_lesion_id bigint NOT NULL COMMENT 'id',
  source_dicom_id bigint NULL DEFAULT NULL COMMENT '原始序列dicom_id',
  study_uid varchar(500) NULL DEFAULT NULL,
  series_uid varchar(500) NULL DEFAULT NULL,
  study_date varchar(30) NULL DEFAULT NULL,
  pat_card_id varchar(20) NULL DEFAULT NULL,
  patient_name varchar(1000) NULL DEFAULT NULL,
  body_part varchar(100) NULL DEFAULT NULL,
  detect_doctor varchar(50) NULL DEFAULT NULL,
  detect_enterprise_name varchar(50) NULL DEFAULT NULL,
  detect_time varchar(30) NULL DEFAULT NULL,
  ai_series_path varchar(1000) NULL DEFAULT NULL,
  image_count int NULL DEFAULT NULL,
  lesion_count int NULL DEFAULT 0,
  lesions_json mediumtext NULL,
  engine varchar(100) NULL DEFAULT NULL,
  disclaimer varchar(1000) NULL DEFAULT NULL,
  description varchar(1000) NULL DEFAULT NULL,
  detect_mode varchar(20) NULL DEFAULT 'series',
  instance_uid varchar(128) NULL DEFAULT NULL,
  source_slice_index int NULL DEFAULT NULL,
  sort int UNSIGNED NOT NULL DEFAULT 0,
  create_by bigint NULL DEFAULT NULL,
  create_time datetime NULL DEFAULT CURRENT_TIMESTAMP,
  update_by bigint NULL DEFAULT NULL,
  update_time datetime NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  remark varchar(1000) NULL DEFAULT NULL,
  del_flag tinyint NOT NULL DEFAULT 0,
  tenant_id bigint NOT NULL,
  PRIMARY KEY (dicom_ai_lesion_id),
  KEY idx_ai_lesion_pat_card (pat_card_id),
  KEY idx_ai_lesion_source_dicom (source_dicom_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='AI识别病灶结果序列表';
" 2>/dev/null

docker exec westChina-mysql mysql -uroot -p123456 -e "
ALTER TABLE \`xy-cloud\`.dicom_ai_lesion
  ADD COLUMN detect_mode varchar(20) NULL DEFAULT 'series' COMMENT '识别模式 series|single' AFTER description;
" 2>/dev/null || true
docker exec westChina-mysql mysql -uroot -p123456 -e "
ALTER TABLE \`xy-cloud\`.dicom_ai_lesion
  ADD COLUMN instance_uid varchar(128) NULL DEFAULT NULL COMMENT '标记层 SOP Instance UID' AFTER detect_mode;
" 2>/dev/null || true
docker exec westChina-mysql mysql -uroot -p123456 -e "
ALTER TABLE \`xy-cloud\`.dicom_ai_lesion
  ADD COLUMN source_slice_index int NULL DEFAULT NULL COMMENT '原始序列层索引0-based' AFTER instance_uid;
" 2>/dev/null || true

echo "[3/4] 清除 Redis 菜单缓存并重启 system 服务..."
docker exec westChina-redis redis-cli DEL \
  'sys_enterprise:-1:menu' \
  'sys_enterprise:0:menu' \
  'sys_enterprise:-1:system_menu' \
  'sys_enterprise:0:system_menu' 2>/dev/null || true
pkill -f 'westChina-modules-system.jar' 2>/dev/null || true
sleep 2
cd "$PROJECT_ROOT/deploymentServer"
export JAVA_HOME="${JAVA_HOME:-$HOME/tools/jdk8}"
export PATH="$JAVA_HOME/bin:$PATH"
nohup java -Xms128m -Xmx384m \
  -Dspring.cloud.nacos.discovery.server-addr=127.0.0.1:8848 \
  -Dspring.cloud.nacos.config.server-addr=127.0.0.1:8848 \
  -jar westChina-modules-system.jar >> logs/system.log 2>&1 &
for i in $(seq 1 24); do ss -tlnp | grep -q ':9600' && echo "system 已就绪" && break; sleep 5; done

mkdir -p /tmp/westChina/uploadPath

echo "重启 Nacos 使配置生效..."
cd "$PROJECT_ROOT/dockerOfMy"
docker compose restart westChina-nacos
sleep 20
curl -sf http://127.0.0.1:8848/nacos/ >/dev/null && echo "Nacos 已就绪" || echo "警告: Nacos 未响应，请检查 docker logs westChina-nacos"
