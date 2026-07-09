#!/bin/bash
source "$(dirname "$0")/env.sh"

echo "=== Docker 中间件 ==="
docker ps --filter name=westChina --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' 2>/dev/null || echo "(docker 未运行)"

echo ""
echo "=== 后端 JAR ==="
cd "$PROJECT_ROOT/deploymentServer"
bash runlocal.sh status

echo ""
echo "=== 端口监听 ==="
ss -tlnp 2>/dev/null | grep -E ':5000|:8080|:9200|:9600|:9700|:9800|:8848' || true

echo ""
echo "=== 健康检查 ==="
check() {
  local name="$1" url="$2"
  curl -sf -o /dev/null -w "$name: %{http_code}\n" "$url" 2>/dev/null || echo "$name: 未启动"
}
check "前端 /main/"           "http://127.0.0.1:5000/main/"
check "前端 /administrator/"  "http://127.0.0.1:5000/administrator/"
check "前端 /ct/"             "http://127.0.0.1:5000/ct/"
if curl -sf -o /dev/null "http://127.0.0.1:5000/code" 2>/dev/null; then
  check "API /code"           "http://127.0.0.1:5000/code"
else
  check "API /prod-api/code"  "http://127.0.0.1:5000/prod-api/code"
fi
check "Nacos"                 "http://127.0.0.1:8848/nacos/"

echo ""
echo "=== Redis 企业缓存 (登录依赖) ==="
docker exec westChina-redis redis-cli GET login_enterprise:superadmin 2>/dev/null \
  || echo "(Redis 未运行或缓存未加载，请重启 system 服务)"

echo ""
echo "=== Sealtun 隧道 ==="
if command -v sealtun >/dev/null 2>&1 || command -v npx >/dev/null 2>&1; then
  SEALTUN_BIN="sealtun"
  command -v sealtun >/dev/null 2>&1 || SEALTUN_BIN="npx sealtun"
  # shellcheck disable=SC2086
  $SEALTUN_BIN status 2>/dev/null | sed 's/^/  /' || echo "  (无法获取 sealtun 状态)"
  echo ""
  # shellcheck disable=SC2086
  $SEALTUN_BIN list 2>/dev/null | sed 's/^/  /' || echo "  (无法列出隧道)"
else
  echo "  sealtun 未安装，执行: npm install -g sealtun"
fi
