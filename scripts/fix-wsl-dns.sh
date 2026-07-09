#!/usr/bin/env bash
# 修复 WSL 重启后 gzg.sealos.run 解析失败，导致 sealtun 无法连接 Sealos
# 用法: sudo bash scripts/fix-wsl-dns.sh
set -eo pipefail

if [ "$(id -u)" -ne 0 ]; then
  echo "请使用 sudo 运行: sudo bash scripts/fix-wsl-dns.sh"
  exit 1
fi

RESOLV_CONF="/etc/resolv.conf"
WSL_CONF="/etc/wsl.conf"
HOSTS_LINE="101.33.204.143 gzg.sealos.run"

echo "=== 修复 WSL DNS（Sealtun / Sealos）==="

if ! grep -q "generateResolvConf = false" "$WSL_CONF" 2>/dev/null; then
  cat >> "$WSL_CONF" <<'EOF'

[network]
generateResolvConf = false
EOF
  echo "已写入 /etc/wsl.conf [network] generateResolvConf = false"
fi

cp "$RESOLV_CONF" "${RESOLV_CONF}.bak.$(date +%Y%m%d%H%M%S)" 2>/dev/null || true

cat > "$RESOLV_CONF" <<'EOF'
nameserver 223.5.5.5
nameserver 114.114.114.114
nameserver 8.8.8.8
EOF
echo "已更新 $RESOLV_CONF"

if ! grep -q "gzg.sealos.run" /etc/hosts 2>/dev/null; then
  echo "$HOSTS_LINE" >> /etc/hosts
  echo "已添加 /etc/hosts: $HOSTS_LINE"
fi

if getent hosts gzg.sealos.run >/dev/null 2>&1; then
  echo "DNS 检查通过: $(getent hosts gzg.sealos.run)"
else
  echo "DNS 仍异常，请在 Windows PowerShell 执行: wsl --shutdown 后重新打开 WSL"
  exit 1
fi

echo ""
echo "修复完成。请执行:"
echo "  cd $(cd "$(dirname "$0")/.." && pwd)"
echo "  bash scripts/start-sealtun.sh"
