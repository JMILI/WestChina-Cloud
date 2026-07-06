# 文档索引

| 文档 | 说明 |
|------|------|
| [DEPLOY.md](./DEPLOY.md) | 部署与开发指南（架构、端口、数据库、AI 摘要） |
| [09-from-scratch.md](./09-from-scratch.md) | 全新 Ubuntu 从零部署步骤 |
| [../ai-service/README.md](../ai-service/README.md) | **AI 推理服务详细说明**（方案 A/B/C、API、环境变量） |
| [../westsql/readme.txt](../westsql/readme.txt) | SQL 脚本与租户子库表结构 |

## 快速命令

```bash
bash scripts/setup_env.sh base      # 初始化环境
bash build_all.sh                   # 编译
bash start_all.sh core              # 启动
bash scripts/status.sh              # 状态检查
```

默认登录：**superadmin / superadmin** → http://127.0.0.1:5000/main/
