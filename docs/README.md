# 文档索引

## 部署与运维

| 文档 | 说明 |
|------|------|
| [DEPLOY.md](./DEPLOY.md) | **从零部署完整教程**（架构、分步操作、数据库、Sealtun、排错） |
| [12-sealtun-remote-access.md](./12-sealtun-remote-access.md) | Sealtun 远程访问（原理、计费、自定义域名） |
| [../scripts/README.md](../scripts/README.md) | 脚本清单与用途 |
| [../logs/README.md](../logs/README.md) | 统一日志目录结构 |
| [../dockerOfMy/README.md](../dockerOfMy/README.md) | Docker 中间件 |

## AI 病灶识别

| 文档 | 说明 |
|------|------|
| [../ai-service/README.md](../ai-service/README.md) | AI 服务 API、三种方案、环境变量、方案 B 验收脚本 |

## 数据库

| 文档 | 说明 |
|------|------|
| [../westsql/readme.txt](../westsql/readme.txt) | SQL 文件说明；`slave-init.sql` 为租户子库唯一权威源 |

## 远程访问（固定地址）

隧道名 **`westchina-ui`**（`sealtun.yaml`），公网基址：

**https://sealtun-westchina-ui-ns-km83ebvo.sealosgzg.site**

| 系统 | 地址 |
|------|------|
| 管理端 | https://sealtun-westchina-ui-ns-km83ebvo.sealosgzg.site/main/ |
| CT 阅片 | https://sealtun-westchina-ui-ns-km83ebvo.sealosgzg.site/ct/ |
| 租户端 | https://sealtun-westchina-ui-ns-km83ebvo.sealosgzg.site/administrator/ |

`bash start_all.sh core` 会自动恢复该隧道，域名不变。详见 [12-sealtun-remote-access.md](./12-sealtun-remote-access.md)。

## 快速命令

```bash
bash scripts/setup_env.sh base      # 初始化环境
bash build_all.sh                   # 编译（含 sync-sql）
bash start_all.sh core              # 启动核心服务
bash scripts/status.sh              # 状态检查
bash scripts/sync-sql.sh            # 同步 slave-init.sql
```

默认登录：**superadmin / superadmin** → http://127.0.0.1:5000/main/
