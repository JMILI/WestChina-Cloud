存放 Docker MySQL 首次初始化脚本。

- xy-cloud.sql / xy-config.sql / xy_seata.sql：主库与配置库
- slave-init.sql：租户子库表结构（由 westsql/slave-init.sql 同步，勿手改）
- zz-init-tenant-dbs.sh：首次启动时创建 xy-cloud1、xy-cloud2 并导入 slave-init.sql

修改子库表结构请编辑 westsql/slave-init.sql，再执行 bash scripts/sync-sql.sh
