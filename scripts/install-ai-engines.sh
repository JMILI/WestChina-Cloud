#!/bin/bash
# 安装 TotalSegmentator 与 MONAI 可选推理引擎
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/ai-service"

PY=""
if [ -x "$ROOT/ai-service/.conda/bin/python" ]; then
  PY="$ROOT/ai-service/.conda/bin/python"
elif [ -x "$ROOT/ai-service/.venv/bin/python" ]; then
  PY="$ROOT/ai-service/.venv/bin/python"
else
  echo "请先运行 scripts/start-ai.sh 创建 Python 环境"
  exit 1
fi

PIP_PATCH="$ROOT/ai-service/scripts/pip_dns_patch.py"
pip_install() {
  if python3 -c "import socket; socket.gethostbyname('pypi.org')" >/dev/null 2>&1; then
    "$PY" -m pip "$@"
  else
    echo "（DNS 不可用，使用 IP 映射安装）"
    "$PY" "$PIP_PATCH" "$@"
  fi
}

echo "==> 安装 TotalSegmentator …"
pip_install install -r requirements-totalsegmentator.txt

echo "==> 安装 MONAI / PyTorch（CPU 版，体积较大请耐心等待）…"
pip_install install torch torchvision --index-url https://download.pytorch.org/whl/cpu || \
  pip_install install torch torchvision
pip_install install -r requirements-monai.txt

echo "==> 验证引擎可用性 …"
"$PY" - <<'PY'
from app.engines import get_engine_catalog
for e in get_engine_catalog():
    status = "可用" if e["available"] else "不可用"
    print(f"  {e['label']}: {status}")
PY

echo "完成。请执行: bash scripts/start-ai.sh"
