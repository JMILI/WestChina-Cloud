#!/bin/sh

# 复制项目的文件到对应docker路径，便于一键生成镜像。
usage() {
	echo "Usage: sh copy.sh"
	exit 1
}


# copy sql
echo "begin copy sql "
cp ../sql/quartz.sql ./mysql/db
cp ../sql/westChina_1.sql ./mysql/db
cp ../sql/westChina_2.sql ./mysql/db
cp ../sql/xy_config.sql ./mysql/db

# copy html
echo "begin copy html "
cp -r ../westChina-ui/main/dist/** ./nginx/html/main
cp -r ../westChina-ui/administrator/dist/** ./nginx/html/administrator


# copy jar
echo "begin copy westChina-gateway "
cp ../westChina-gateway/target/westChina-gateway.jar ./westChina/gateway/jar

echo "begin copy westChina-auth "
cp ../westChina-auth/target/westChina-auth.jar ./westChina/auth/jar

echo "begin copy westChina-visual "
cp ../westChina-visual/westChina-monitor/target/westChina-visual-monitor.jar  ./westChina/visual/monitor/jar

echo "begin copy westChina-modules-system "
cp ../westChina-modules/westChina-system/target/westChina-modules-system.jar ./westChina/modules/system/jar

echo "begin copy westChina-modules-tenant "
cp ../westChina-modules/westChina-tenant/target/westChina-modules-tenant.jar ./westChina/modules/tenant/jar

echo "begin copy westChina-modules-file "
cp ../westChina-modules/westChina-file/target/westChina-modules-file.jar ./westChina/modules/file/jar

echo "begin copy westChina-modules-job "
cp ../westChina-modules/westChina-job/target/westChina-modules-job.jar ./westChina/modules/job/jar

echo "begin copy westChina-modules-gen "
cp ../westChina-modules/westChina-gen/target/westChina-modules-gen.jar ./westChina/modules/gen/jar