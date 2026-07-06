# WestChina-Cloud 从零部署指南

> 场景：全新 Ubuntu 20.04/22.04/24.04 系统，从 GitHub 克隆后一步步跑起来。

相关文档：[DEPLOY.md](./DEPLOY.md) · [AI 服务说明](../ai-service/README.md) · [westsql 说明](../westsql/readme.txt)

---

## 前置条件

- Ubuntu 20.04+（物理机 / WSL2 均可）
- 可以访问互联网（下载依赖）
- 建议 8GB+ 内存、50GB+ 磁盘
- 如果有 NVIDIA 显卡，可额外启用 GPU AI 推理

---

## 第一步：克隆项目

```bash
git clone https://github.com/your-org/WestChina-Cloud.git
cd WestChina-Cloud
```

---

## 第二步：一键初始化环境

这一步会安装所有系统依赖并初始化 Docker 中间件和数据库。

```bash
bash scripts/setup_env.sh base
```

**这一步内部会做什么：**

| 子步骤 | 说明 | 耗时 |
|--------|------|------|
| 安装 Docker | 从官方脚本安装，当前用户加入 docker 组 | ~2 分钟 |
| 安装 Java 8 | 下载 Eclipse Temurin JDK8 到 `~/tools/jdk8/` | ~1 分钟 |
| 安装 Maven 3.8 | 下载到 `~/tools/maven/` | ~30 秒 |
| 安装 Node.js 18 | 通过 NodeSource 仓库安装 | ~1 分钟 |
| 安装 Python 3 | `apt install python3 python3-pip python3-venv` | ~30 秒 |
| 启动 Docker 中间件 | docker compose 拉起 MySQL/Redis/RabbitMQ/MinIO/Nacos | ~3 分钟 |
| 初始化数据库 | 主库 `xy-cloud` / `xy-config` / `xy_seata`（租户子库由界面新增数据源时创建） | ~2 分钟 |
| 本机配置适配 | 将配置中的主机名替换为 127.0.0.1 | ~1 分钟 |

**安装完成后验证：**

```bash
# Docker 中间件
docker ps | grep westChina

# Java
java -version   # 应显示 1.8.x

# Node
node -v         # 应显示 v18.x 或更高

# 数据库（应有 xy-cloud、xy-config 等；租户子库在界面添加数据源后出现）
docker exec westChina-mysql mysql -uroot -p123456 -e "SHOW DATABASES;"
```

**⚠️ 如果执行了 `sudo usermod -aG docker $USER`，需要重新登录或执行 `newgrp docker` 使 docker 组生效。**

租户子库（如 `xy-xiehe`）需在 **租户管理 → 新增数据源** 后才会出现；连接测试或保存时会自动执行 `slave-init.sql` 建 17 张表。

---

## 第三步（可选）：安装 AI 推理引擎

如果需要 AI 病灶识别功能：

```bash
# CPU 版（无 GPU 时）
bash scripts/setup_env.sh ai-engines

# GPU 版（有 NVIDIA 显卡时）
bash scripts/setup_env.sh gpu
```

**验证 AI 引擎：**

```bash
cd ai-service
.conda/bin/python -c "from app.engines import get_engine_catalog; print(get_engine_catalog())"
```

---

## 第四步：编译项目

```bash
bash build_all.sh
```

**这一步内部会做什么：**

| 子步骤 | 说明 | 耗时 |
|--------|------|------|
| 同步 SQL | `scripts/sync-sql.sh` → Java classpath | ~1 秒 |
| Maven 编译后端 | `mvn clean package -DskipTests`，产出 9 个 JAR | ~5 分钟 |
| 复制 JAR | 将编译产物复制到 `deploymentServer/` | ~5 秒 |
| npm 编译前端 (main) | `npm install && vue-cli-service build` | ~3 分钟 |
| npm 编译前端 (administrator) | 同上 | ~3 分钟 |
| npm 编译前端 (ct) | 同上 | ~3 分钟 |
| 复制前端 dist | 将 dist 复制到 `deploymentServer/ui-dist/` | ~5 秒 |

**如果 Maven 未安装，脚本会自动跳过 Java 编译并提示使用已有的 JAR 包。**

**验证编译产物：**

```bash
ls -lh deploymentServer/*.jar
ls deploymentServer/ui-dist/ct/index.html
```

---

## 第五步：启动全部服务

```bash
bash start_all.sh core
```

**启动顺序：**

```
Docker 中间件 (MySQL/Redis/RabbitMQ/Nacos/MinIO)
    │  等待端口就绪
    ▼
后端 Java 服务 (Gateway→Auth→System→Tenant)
    │
    ▼
AI 推理服务 (Python FastAPI, :9810)
    │
    ▼
前端 UI 服务 (Node.js, :5000)
```

**脚本输出示例：**

```
============================================
  WestChina-Cloud 一键启动 (core)
============================================
[INFO] Docker 中间件已在运行
[INFO] 启动后端 Java 服务...
[INFO] 启动 gateway ...
[INFO] gateway 已就绪 (端口 8080)
[INFO] 启动 auth ...
[INFO] auth 已就绪 (端口 9200)
[INFO] 启动 system ...
[INFO] system 已就绪 (端口 9600)
[INFO] 启动 tenant ...
[INFO] tenant 已就绪 (端口 9700)
[INFO] 启动 AI 推理服务...
[INFO] 等待 AI推理服务 (端口 9810)...
[INFO] AI推理服务 已就绪
[INFO] 启动前端 UI...
[INFO] 等待 前端UI (端口 5000)...
[INFO] 前端UI 已就绪

============================================
  服务状态检查
============================================
  ✓ Nacos       http://127.0.0.1:8848 (200)
  ✓ Gateway     http://127.0.0.1:8080 (200)
  ✓ System      http://127.0.0.1:9600 (200)
  ✓ CT阅片     http://127.0.0.1:9800 (200)
  ✓ AI推理     http://127.0.0.1:9810 (200)
  ✓ 前端UI     http://127.0.0.1:5000 (200)

============================================
  访问地址
============================================
  管理系统:    http://127.0.0.1:5000/main/
  租户管理:    http://127.0.0.1:5000/administrator/
  阅片系统:    http://127.0.0.1:5000/ct/
  Nacos:       http://127.0.0.1:8848/nacos  (nacos/nacos)
  MinIO:       http://127.0.0.1:9001  (admin/admin123456)
  RabbitMQ:    http://127.0.0.1:15672  (guest/guest)
============================================
```

---

## 第六步：登录使用

浏览器打开 `http://127.0.0.1:5000/main/`：

| 字段 | 值 |
|------|-----|
| 企业账号 | `superadmin` |
| 员工账号 | `superadmin` |
| 密码 | `superadmin` |

CT 阅片系统：`http://127.0.0.1:5000/ct/`

---

## 日常操作速查

```bash
# 启动
bash start_all.sh core      # 核心服务
bash start_all.sh all       # 全部服务
bash start_all.sh ai-only   # 仅重启 AI

# 停止
bash stop_all.sh            # 停止应用层
bash stop_all.sh docker     # 停止应用层 + Docker 中间件

# 状态检查
bash scripts/status.sh

# 查看日志
tail -f deploymentServer/logs/ai-service.log   # AI 日志
tail -f deploymentServer/logs/ct.log           # CT 模块日志
docker logs -f westChina-nacos                 # Nacos 日志
```

---

## 端口速查

| 端口 | 服务 | 访问 |
|:----:|------|------|
| 5000 | 前端 UI | http://127.0.0.1:5000/ |
| 8080 | API 网关 | - |
| 8848 | Nacos | http://127.0.0.1:8848/nacos/ |
| 9001 | MinIO | http://127.0.0.1:9001/ |
| 9810 | AI 推理 | http://127.0.0.1:9810/health |
| 9200 | Auth | - |
| 9600 | System | - |
| 9800 | CT 阅片 | - |

---

## 故障排查

### Docker 权限错误

```bash
sudo usermod -aG docker $USER
# 退出重新登录，或执行：
newgrp docker
```

### Java/Maven 未找到

如果 `~/tools/` 下没有自动安装成功，手动安装：

```bash
# Java 8
sudo apt install openjdk-8-jdk

# Maven
sudo apt install maven
```

### Nacos 启动后报数据库连接错误

等待 MySQL 完全就绪后重启：

```bash
cd dockerOfMy
docker compose restart westChina-nacos
```

### 前端页面空白/接口报错

检查 gateway 和 system 是否已启动：

```bash
bash scripts/status.sh
# 如果 gateway 或 system 未启动：
bash start_all.sh core
```

### AI 识别无结果

```bash
# 检查 AI 服务是否在跑
curl http://127.0.0.1:9810/engines
# 确认 scheme-a / scheme-b 的 available 为 true；scheme-b 还需 GPU
# 若为 false，安装引擎后重启：
bash scripts/setup_env.sh ai-engines
bash scripts/start-ai.sh
```

### 新增租户子库缺 CT/AI 表

```bash
# 对应该数据源的数据库名执行（如 xy-xiehe）
bash scripts/init-tenant-db.sh <数据库名> docker
```

---

## 完整执行序列（复制粘贴版）

```bash
# === 从 GitHub 克隆 ===
git clone https://github.com/your-org/WestChina-Cloud.git
cd WestChina-Cloud

# === 初始化环境（首次约 15 分钟） ===
bash scripts/setup_env.sh base

# === (可选) 安装 AI 引擎 ===
bash scripts/setup_env.sh ai-engines

# === 编译项目（约 15 分钟） ===
bash build_all.sh

# === 启动 ===
bash start_all.sh core

# === 浏览器访问 ===
# http://127.0.0.1:5000/main/
# 账号: superadmin / superadmin
```
