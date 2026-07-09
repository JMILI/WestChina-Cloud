# scripts 目录说明

本目录为 **Linux / WSL2 开发与部署的主脚本入口**。

## 环境与构建

| 脚本 | 用途 |
|------|------|
| `env.sh` | 导出 `PROJECT_ROOT`、`JAVA_HOME`、`AI_PYTHON` 等（被其他脚本 source） |
| `log_paths.sh` | 统一日志路径；创建 `logs/` 子目录；`deploymentServer/logs` → `logs/java` 符号链接 |
| `setup_env.sh` | 一键初始化：`base` / `ai-engines` / `gpu` / `full` |
| `build.sh` | Maven 编译 + 前端 build + 复制到 `deploymentServer/` |
| `sync-sql.sh` | `westsql/slave-init.sql` → classpath + `dockerOfMy/mysql/db/` |

## 启停与状态

| 脚本 | 用途 |
|------|------|
| `start.sh` | 启动后端 Java（调用 `deploymentServer/runlocal.sh`） |
| `start-ai.sh` | 启动 AI 服务 :9810 |
| `stop.sh` | 停止 Java + AI + UI |
| `status.sh` | 检查端口与健康状态 |

根目录封装：

```bash
bash start_all.sh core    # Docker + Java 核心 + AI + UI
bash stop_all.sh          # 停止应用层
bash build_all.sh         # 调用 scripts/build.sh
```

## 数据库

| 脚本 | 用途 |
|------|------|
| `init-local-db.sh` | 本机部署：Nacos 配置主机名 → 127.0.0.1 等 |
| `init-tenant-db.sh` | 运维手动建租户子库并执行 slave-init.sql |

## 远程访问（可选）

| 脚本 | 用途 |
|------|------|
| `start-sealtun.sh` | 启动 Sealtun 隧道 |
| `expose-sealtun.sh` | 暴露本地 5000 |
| `expose-sealtun-auto.sh` | 自动暴露（配合 `sealtun.yaml`） |
| `fix-wsl-dns.sh` | WSL2 DNS 修复 |

## 运维辅助

| 脚本 | 用途 |
|------|------|
| `install-ai-engines.sh` | 安装 TotalSegmentator / MONAI 等 |
| `install-pytorch-gpu.sh` | GPU 版 PyTorch |
| `reset-tenant-data.sh` | 重置演示租户数据 |
| `resort-minio-series.py` | MinIO 序列文件重排序 |

## 典型 0→1 流程

```bash
bash scripts/setup_env.sh base
bash scripts/setup_env.sh ai-engines   # 需要 AI 时
bash build_all.sh
bash start_all.sh core
bash scripts/status.sh
```
