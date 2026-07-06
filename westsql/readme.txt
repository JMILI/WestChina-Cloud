westsql 目录说明
================

本目录存放数据库初始化 SQL。**租户子库表结构的唯一权威来源是 `slave-init.sql`。**

文件清单
--------
slave-init.sql    租户子库表结构（17 张表，新增数据源时自动执行）
xy-cloud.sql      主库 xy-cloud（租户/策略/系统/CT 业务 + 初始数据）
xy-config.sql     Nacos 配置库 xy-config
xy_seata.sql      Seata 事务库（如启用分布式事务）

子库 slave-init.sql 表清单（17 张）
----------------------------------
CT 业务（4）：
  ct_patients, ct_dicom, dicom_maker, dicom_ai_lesion

系统（11）：
  sys_dept, sys_user, sys_role, sys_post, sys_logininfor, sys_oper_log,
  sys_notice, sys_notice_log, sys_organize_role, sys_role_dept_post, sys_role_system_menu

素材（2）：
  xy_material, xy_material_folder

演示子库 xy-cloud1 / xy-cloud2
------------------------------
不再维护单独的 xy-cloud1.sql / xy-cloud2.sql，统一用 slave-init.sql 初始化：

  bash scripts/init-tenant-db.sh xy-cloud1 docker
  bash scripts/init-tenant-db.sh xy-cloud2 docker

Docker 首次启动由 dockerOfMy/mysql/db/zz-init-tenant-dbs.sh 自动执行。

同步与部署
----------
1. 修改子库表结构：只编辑 westsql/slave-init.sql
2. 执行同步：bash scripts/sync-sql.sh
3. 完整构建：bash scripts/build.sh（含 SQL 同步）

新增租户数据源
--------------
后台「新增数据源」→ DSUtils.initSlaveDatabase() → 执行 slave-init.sql
