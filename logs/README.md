# 运行时中间文件目录

本目录存放项目运行产生的**日志、缓存、临时文件**，按模块分子目录。已在 `.gitignore` 中忽略（本 README 除外）。

## 目录结构

```mermaid
flowchart TB
  Root["logs/"]
  Root --> ai["ai-service/<br/>主日志 · 体数据缓存 · 临时 NIfTI"]
  Root --> java["java/<br/>微服务日志（deploymentServer/logs 符号链接）"]
  Root --> ui["ui/<br/>前端 UI 日志"]
  Root --> docker["docker/<br/>Nacos · MySQL · RabbitMQ"]
  Root --> sealtun["sealtun/<br/>隧道 expose.log"]
  Root --> file["file-service/<br/>本地上传文件"]
```

## 环境变量

由 `scripts/log_paths.sh` 导出，详见 `scripts/env.sh`。

常用：

```bash
LOG_ROOT=/path/to/WestChina-Cloud/logs
AI_LOG_PATH=$LOG_ROOT/ai-service/ai-service.log
SCHEME_B_CACHE_DIR=$LOG_ROOT/ai-service/cache/volumes
```

## 查看日志

```bash
tail -f logs/ai-service/ai-service.log
tail -f logs/java/ct.log
tail -f logs/ui/ui.log
```
