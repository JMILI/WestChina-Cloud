存放 Docker MySQL 首次初始化脚本。

- xy-cloud.sql / xy-config.sql / xy_seata.sql：主库与配置库（首次空数据卷时自动执行）
- slave-init.sql：租户子库表结构参考副本（与 westsql 同步；**不由 Docker 自动执行**）

租户子库在管理界面「新增数据源」时由后端动态创建。

修改子库表结构请编辑 westsql/slave-init.sql，再执行 bash scripts/sync-sql.sh
