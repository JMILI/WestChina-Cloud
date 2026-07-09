#!/usr/bin/env bash
# 方案 B 一键验收：单元测试 + 模块导入 + 可选 E2E
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PY="${PY:-$ROOT/.conda/bin/python}"
if [[ ! -x "$PY" ]]; then
  PY=python3
fi

echo "=== Scheme B Acceptance ==="
echo "Python: $PY"

echo ""
echo "[1/3] verify_scheme_b.py"
"$PY" scripts/verify_scheme_b.py

echo ""
echo "[2/3] unit tests"
"$PY" -c "
import tests.test_hu_classify as hu
import tests.test_ggo_detect_v2 as ggo
import tests.test_scheme_b_filter as flt
import tests.test_enhanced_contour as ec
import tests.test_scheme_b_p2 as p2
import tests.test_gold_fixtures as gf
for mod in (hu, ggo, flt, ec, p2, gf):
    for name in sorted(n for n in dir(mod) if n.startswith('test_')):
        getattr(mod, name)()
        print('  OK', mod.__name__, name)
"

if [[ -n "${E2E_DICOM_DIR:-}" ]]; then
  echo ""
  echo "[3/3] e2e_detect_test.py ($E2E_DICOM_DIR)"
  PYTHONPATH=. "$PY" scripts/e2e_detect_test.py "$E2E_DICOM_DIR"
else
  echo ""
  echo "[3/3] E2E skipped (set E2E_DICOM_DIR to run)"
fi

echo ""
echo "=== Acceptance complete ==="
