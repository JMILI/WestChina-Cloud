#!/bin/bash
# Docker 首次启动：用 slave-init.sql 创建演示租户子库
set -e
for db in xy-cloud1 xy-cloud2; do
  mysql -uroot -p"${MYSQL_ROOT_PASSWORD}" -e \
    "CREATE DATABASE IF NOT EXISTS \`${db}\` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;"
  mysql -uroot -p"${MYSQL_ROOT_PASSWORD}" "${db}" < /opt/westsql/slave-init.sql
done
