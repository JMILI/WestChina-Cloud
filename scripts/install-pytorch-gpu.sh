#!/bin/bash
# 安装与 WSL CUDA 12.4 驱动兼容的 PyTorch（替换 cu130 构建）
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="$ROOT/ai-service/.conda/bin/pip"
if [ ! -x "$ROOT/ai-service/.conda/bin/pip" ]; then
  echo "未找到 ai-service/.conda，请先运行 scripts/start-ai.sh"
  exit 1
fi

echo "卸载旧版 PyTorch…"
"$PY" uninstall -y torch torchvision 2>/dev/null || true

echo "安装 torch 2.5.1+cu124（约 900MB，请耐心等待）…"
"$PY" install \
  "torch==2.5.1+cu124" \
  "torchvision==0.20.1+cu124" \
  --index-url https://download.pytorch.org/whl/cu124

echo "验证 CUDA…"
"$ROOT/ai-service/.conda/bin/python" - <<'PY'
import torch
print("torch", torch.__version__)
print("cuda available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("device:", torch.cuda.get_device_name(0))
PY

echo "完成。请运行: bash scripts/start-ai.sh"
