#!/usr/bin/env bash
# 将 WestChina UI (:5000) 通过 Sealtun 暴露到公网
# 隧道层 Basic Auth：superadmin / superadmin
# 系统登录：superadmin / superadmin
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! curl -sf -o /dev/null "http://127.0.0.1:5000/main/"; then
  echo "UI :5000 未运行，先执行: bash start_all.sh core"
  exit 1
fi

if ! npx sealtun status 2>/dev/null | grep -q "Logged in: yes"; then
  echo "尚未登录 Sealos，请先执行: npx sealtun login gzg"
  echo "在浏览器完成授权后再运行本脚本。"
  exit 1
fi

export SEALTUN_BASIC_AUTH_PASSWORD='superadmin'
echo "创建隧道（无 Basic Auth，避免 SPA 反复弹窗）..."
exec npx sealtun expose 5000
