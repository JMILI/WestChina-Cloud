westsql 目录说明
================

本目录存放数据库初始化 SQL。**租户子库表结构的唯一权威来源是 `slave-init.sql`。**

文件清单
--------
slave-init.sql    租户子库表结构（17 张表）
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

租户子库如何创建
----------------
**不再预置 xy-cloud1 / xy-cloud2 等演示库。**

在租户管理界面「新增数据源」时：
1. 填写 JDBC 连接（含数据库名，如 xy-xiehe）
2. 后端 `DSUtils.initSlaveDatabase()` 自动 CREATE DATABASE + 执行 slave-init.sql

连接测试（`testSlaveConnection`）同样会建库并初始化表结构。

运维手动补库（可选）：

  bash scripts/init-tenant-db.sh <数据库名> docker

同步与部署
----------
1. 修改子库表结构：只编辑 westsql/slave-init.sql
2. 执行同步：bash scripts/sync-sql.sh
3. 完整构建：bash scripts/build.sh 或 build_all.sh

Docker MySQL 首次启动仅导入 xy-cloud / xy-config / xy_seata，不创建租户子库。
