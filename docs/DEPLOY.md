# WestChina-Cloud 部署与开发指南

> CT 阅片多租户管理系统 — 微服务 + AI 辅助诊断

更详细的从零步骤见 [09-from-scratch.md](./09-from-scratch.md)。AI 推理服务详见 [ai-service/README.md](../ai-service/README.md)。

---

## 1. 系统架构

```
┌──────────────────────────────────────────────────────────────────┐
│                        前端 UI (Node.js :5000)                     │
│          main (管理)  │  administrator (租户)  │  ct (阅片)        │
└──────────────────────────────┬───────────────────────────────────┘
                               │ /prod-api
┌──────────────────────────────▼───────────────────────────────────┐
│                    Gateway (Java :8080)                            │
│                      Spring Cloud Gateway                         │
└────┬──────────┬──────────┬──────────┬──────────┬─────────────────┘
     │          │          │          │          │
┌────▼────┐ ┌──▼───┐ ┌───▼───┐ ┌───▼───┐ ┌───▼──────┐
│  Auth   │ │System│ │  CT   │ │ File  │ │ Tenant   │
│  :9200  │ │:9600 │ │ :9800 │ │ :9300 │ │  :9700   │
└────┬────┘ └──┬───┘ └───┬───┘ └───────┘ └──────────┘
     │         │          │
     │         │    ┌─────▼──────┐
     │         │    │ AI Service │
     │         │    │Python :9810│
     │         │    └────────────┘
┌────▼─────────▼───────────────────────────────────────────────────┐
│                     中间件 (Docker)                                │
│  MySQL :3306  │  Redis :6379  │  RabbitMQ :5672  │  Nacos :8848  │
│  MinIO :9000  │  Sentinel :8718                                │
└──────────────────────────────────────────────────────────────────┘
```

---

## 2. 环境要求

| 组件 | 版本 | 用途 |
|------|------|------|
| Ubuntu | 20.04+ / WSL2 | 操作系统 |
| Docker | 24+ | 中间件容器化 |
| Java (JDK) | 1.8 | 后端微服务 |
| Maven | 3.8+ | Java 编译 |
| Node.js | 18+ | 前端编译 |
| Python | 3.11+ | AI 推理服务 |
| PyTorch | 2.x (CUDA 可选) | 方案 B GPU / 方案 C |

---

## 3. 快速开始

### 3.1 一键初始化环境

```bash
cd WestChina-Cloud

# 基础环境 (Docker + Java + Node + MySQL 数据库初始化)
bash scripts/setup_env.sh base

# 安装 AI 推理引擎 (TotalSegmentator + MONAI)
bash scripts/setup_env.sh ai-engines

# GPU 版 PyTorch（方案 B 推荐）
bash scripts/setup_env.sh gpu

# 或全量安装
bash scripts/setup_env.sh full
```

### 3.2 一键编译

```bash
bash build_all.sh              # Java + 前端
bash build_all.sh frontend-only
```

编译前会自动执行 `scripts/sync-sql.sh`，将 `westsql/slave-init.sql` 同步到 Java classpath。

### 3.3 一键启动

```bash
bash start_all.sh core         # 中间件 + 后端核心 + AI + 前端
bash start_all.sh all          # 含 file/gen/job/monitor
bash start_all.sh ai-only
bash start_all.sh ui-only
```

### 3.4 一键停止

```bash
bash stop_all.sh               # 应用层
bash stop_all.sh docker        # 应用层 + Docker 中间件
```

### 3.5 服务状态检查

```bash
bash scripts/status.sh
```

---

## 4. 服务端口与地址

| 服务 | 端口 | 访问地址 | 默认账号 |
|------|------|---------|---------|
| 管理系统 | 5000 | http://127.0.0.1:5000/main/ | superadmin / superadmin |
| 租户管理 | 5000 | http://127.0.0.1:5000/administrator/ | superadmin / superadmin |
| 阅片系统 | 5000 | http://127.0.0.1:5000/ct/ | superadmin / superadmin |
| API 网关 | 8080 | http://127.0.0.1:8080/ | - |
| AI 健康检查 | 9810 | http://127.0.0.1:9810/health | - |
| AI 引擎列表 | 9810 | http://127.0.0.1:9810/engines | - |
| Nacos | 8848 | http://127.0.0.1:8848/nacos/ | nacos / nacos |
| MinIO 控制台 | 9001 | http://127.0.0.1:9001/ | admin / admin123456 |
| RabbitMQ | 15672 | http://127.0.0.1:15672/ | guest / guest |

---

## 5. 数据库

### 5.1 数据库列表

| 数据库 | 用途 | 说明 |
|--------|------|------|
| `xy-cloud` | 主业务库 | 租户、策略、菜单、CT 元数据等 |
| `xy-cloud1` | 演示租户子库 1 | 17 张表，由 `slave-init.sql` 初始化 |
| `xy-cloud2` | 演示租户子库 2 | 同上 |
| `xy-config` | Nacos 配置库 | - |
| `xy-seata` | 分布式事务 | 可选 |

### 5.2 SQL 文件（`westsql/`）

| 文件 | 用途 |
|------|------|
| **`slave-init.sql`** | **租户子库唯一表结构源**（17 张表，含 CT + `dicom_ai_lesion`） |
| `xy-cloud.sql` | 主库结构与初始数据 |
| `xy-config.sql` | Nacos 配置 |
| `xy_seata.sql` | Seata |

新增租户数据源时，后台自动执行 `slave-init.sql`（见 `DSUtils.initSlaveDatabase`）。

### 5.3 手动初始化

```bash
# 主库
docker exec -i westChina-mysql mysql -uroot -p123456 xy-cloud < westsql/xy-cloud.sql

# 租户子库（任意库名）
bash scripts/init-tenant-db.sh xy-cloud1 docker
bash scripts/init-tenant-db.sh xy-xiehe docker
```

### 5.4 修改子库表结构后同步

```bash
# 1. 编辑 westsql/slave-init.sql
# 2. 同步到 classpath 与 Docker
bash scripts/sync-sql.sh
```

### 5.5 本机部署适配

```bash
# 将 westChinaBackend 替换为 127.0.0.1，补全 CT/AI 表字段
bash scripts/init-local-db.sh
```

---

## 6. AI 推理服务

完整说明见 **[ai-service/README.md](../ai-service/README.md)**。

### 6.1 三种方案摘要

| 方案 | 原理 | GPU | 输出 |
|------|------|:---:|------|
| A 肺区智能筛查 | 肺分割 + HU 形态学 | 否* | 轮廓 + HU |
| B 融合精准分析 | TotalSegmentator + MONAI/nnDetection | **是** | 轮廓 + GGO |
| C 单层异常倾向 | 体内 HU 异常热力图 | 否* | 原图分辨率热力图 |

\* CPU 可运行；B 需 CUDA。

### 6.2 安装与启动

```bash
bash scripts/setup_env.sh ai-engines
bash scripts/install-pytorch-gpu.sh   # 可选
bash scripts/start-ai.sh
```

---

## 7. Docker 中间件

```bash
cd dockerOfMy
docker compose up -d
docker compose ps
docker compose stop
docker compose down
```

| 服务 | 配置 |
|------|------|
| MySQL | `dockerOfMy/mysql/conf/`、`mysql/db/` |
| Redis | `dockerOfMy/redis/conf/redis.conf` |
| Nacos / MinIO | `docker-compose.yml` 环境变量 |

Docker 首次启动时，`zz-init-tenant-dbs.sh` 会自动创建 `xy-cloud1` / `xy-cloud2` 并导入 `slave-init.sql`。

---

## 8. 项目结构

```
WestChina-Cloud/
├── start_all.sh / stop_all.sh / build_all.sh
├── scripts/
│   ├── setup_env.sh          # 环境初始化
│   ├── sync-sql.sh           # SQL 同步
│   ├── init-tenant-db.sh     # 租户子库初始化
│   ├── start-ai.sh           # AI 服务启动
│   └── init-local-db.sh      # 本机配置适配
├── ai-service/               # Python AI（见 ai-service/README.md）
├── westChina-modules/        # Java 微服务
├── westChina-ui/             # Vue 2 前端
├── deploymentServer/         # JAR + ui-dist + 日志
├── dockerOfMy/               # Docker Compose
├── westsql/                  # SQL 源文件
└── docs/                     # 文档（含本文档）
```

---

## 9. 常见问题

### Docker 权限

```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Nacos 数据库连接失败

```bash
cd dockerOfMy && docker compose restart westChina-nacos
```

### AI GPU 不可用

```bash
nvidia-smi
bash scripts/install-pytorch-gpu.sh
```

### 前端登录失败

```bash
bash scripts/status.sh
bash scripts/init-local-db.sh
```

默认账号：**superadmin / superadmin**（企业账号与员工账号均填 `superadmin`）。

---

## 10. 日志

```bash
tail -f deploymentServer/logs/ai-service.log
tail -f deploymentServer/logs/ct.log
tail -f deploymentServer/logs/ui.log
docker logs -f westChina-nacos
```
