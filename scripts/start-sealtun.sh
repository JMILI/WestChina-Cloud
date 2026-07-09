#!/usr/bin/env bash
# 重启后自动恢复 Sealtun 隧道，供同事远程访问 UI :5000
# 由 start_all.sh 调用，也可单独执行: bash scripts/start-sealtun.sh
set -eo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck source=scripts/env.sh
source "$ROOT/scripts/env.sh"

SEALTUN_CMD=""
SEALTUN_UI_TUNNEL="${SEALTUN_UI_TUNNEL:-westchina-ui}"
SEALTUN_FALLBACK_TUNNEL="${SEALTUN_FALLBACK_TUNNEL:-5458e3ca79d541c1}"

sealtun_cmd() {
  # shellcheck disable=SC2086
  $SEALTUN_CMD "$@"
}

ensure_sealtun_cli() {
  if command -v sealtun >/dev/null 2>&1; then
    SEALTUN_CMD=sealtun
    return 0
  fi

  if command -v npx >/dev/null 2>&1 && npx --yes sealtun --version >/dev/null 2>&1; then
    SEALTUN_CMD="npx sealtun"
    return 0
  fi

  if ! command -v npm >/dev/null 2>&1; then
    log_error "未找到 npm，无法安装 sealtun。请先安装 Node.js 或执行 scripts/setup_env.sh"
    return 1
  fi

  log_info "安装 sealtun CLI (npm install -g sealtun)..."
  npm install -g sealtun
  SEALTUN_CMD=sealtun
}

sealtun_logged_in() {
  sealtun_cmd status 2>/dev/null | grep -q "Logged in: yes"
}

sealtun_daemon_running() {
  sealtun_cmd status 2>/dev/null | grep -q "Running: yes"
}

check_sealos_network() {
  local i code
  for i in 1 2 3; do
    if getent hosts gzg.sealos.run >/dev/null 2>&1; then
      break
    fi
    [ "$i" -lt 3 ] && sleep 3
  done

  if ! getent hosts gzg.sealos.run >/dev/null 2>&1; then
    log_warn "无法解析 gzg.sealos.run（WSL 重启后 DNS 常见问题）"
    log_warn "请执行: sudo bash scripts/fix-wsl-dns.sh"
    log_warn "或在 Windows PowerShell 执行: wsl --shutdown 后重新打开 WSL"
    return 1
  fi

  for i in 1 2 3; do
    code=$(curl -sk --connect-timeout 12 -o /dev/null -w "%{http_code}" "https://gzg.sealos.run:6443/version" 2>/dev/null || echo "000")
    [ "$code" != "000" ] && return 0
    [ "$i" -lt 3 ] && sleep 3
  done

  log_warn "无法连接 Sealos API (gzg.sealos.run:6443)，请检查网络或 VPN"
  return 1
}

tunnel_exists() {
  local tunnel_id="$1"
  sealtun_cmd list 2>/dev/null | awk 'NR>3 {print $1}' | grep -qx "$tunnel_id"
}

tunnel_endpoint() {
  local tunnel_id="$1"
  sealtun_cmd list 2>/dev/null | awk -v id="$tunnel_id" '$1 == id {print $4; exit}'
}

start_existing_tunnel() {
  local tunnel_id="$1"
  log_info "恢复隧道: $tunnel_id"
  sealtun_cmd start "$tunnel_id"
}

create_tunnels_from_yaml() {
  log_info "按 sealtun.yaml 创建/同步隧道..."
  sealtun_cmd apply -f sealtun.yaml
}

print_tunnel_urls() {
  local endpoint
  endpoint="$(tunnel_endpoint "$SEALTUN_UI_TUNNEL" || true)"
  if [ -z "$endpoint" ]; then
    endpoint="$(tunnel_endpoint "$SEALTUN_FALLBACK_TUNNEL" || true)"
  fi
  if [ -z "$endpoint" ]; then
    return 0
  fi

  echo ""
  echo "  同事远程访问（Sealtun）:"
  echo "    管理端:  ${endpoint}/main/"
  echo "    租户端:  ${endpoint}/administrator/"
  echo "    CT阅片:  ${endpoint}/ct/"
}

main() {
  ensure_sealtun_cli

  if ! sealtun_logged_in; then
    log_warn "Sealtun 未登录，跳过隧道恢复"
    log_warn "首次使用请执行: sealtun login gzg"
    return 0
  fi

  if ! curl -sf -o /dev/null "http://127.0.0.1:5000/main/"; then
    log_warn "UI :5000 未就绪，跳过隧道恢复"
    return 0
  fi

  if ! check_sealos_network; then
    return 1
  fi

  log_info "恢复 Sealtun 隧道..."

  if tunnel_exists "$SEALTUN_UI_TUNNEL"; then
    start_existing_tunnel "$SEALTUN_UI_TUNNEL"
  elif tunnel_exists "$SEALTUN_FALLBACK_TUNNEL"; then
    start_existing_tunnel "$SEALTUN_FALLBACK_TUNNEL"
  else
    create_tunnels_from_yaml
  fi

  if sealtun_daemon_running; then
    log_info "Sealtun daemon 已运行"
  else
    log_warn "Sealtun daemon 未运行，请检查: sealtun status"
  fi

  sealtun_cmd list 2>/dev/null || true
  print_tunnel_urls
}

main "$@"
