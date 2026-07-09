# Docker 中间件（本机开发 / 部署）

本目录仅包含 **MySQL / Redis / RabbitMQ / MinIO / Nacos** 的 `docker-compose.yml` 与镜像构建上下文。

## 启动

```bash
# 推荐：项目根目录一键初始化（含中间件）
bash scripts/setup_env.sh base

# 或仅启动中间件
cd dockerOfMy && docker compose up -d
```

## 日志位置

容器日志已统一挂载到项目根目录 **`logs/docker/`**（见 `docker-compose.yml`）：

| 服务 | 宿主机路径 |
|------|------------|
| Nacos | `logs/docker/nacos/` |
| MySQL | `logs/docker/mysql/` |
| RabbitMQ | `logs/docker/rabbitmq/` |

**请勿**在 `dockerOfMy/nacos/logs` 或 `dockerOfMy/mysql/logs` 下积累日志；这些是旧版遗留目录，已在 `.gitignore` 中忽略。Java 微服务日志见 `logs/java/`（`deploymentServer/logs` 为指向该目录的符号链接）。

## SQL 初始化

- 主库：`westsql/xy-cloud.sql`、`xy-config.sql`、`xy_seata.sql`（MySQL 首次启动导入）
- 租户子库：**权威源** `westsql/slave-init.sql`，由 `scripts/sync-sql.sh` 同步到 classpath 与 `mysql/db/` 副本

## 数据卷（不提交 Git）

`mysql/data`、`redis/data`、`rabbitmq/data`、`minio/data` 等为运行时数据，已在 `.gitignore` 中忽略。
