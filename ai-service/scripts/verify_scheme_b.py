#!/usr/bin/env python3
"""方案 B 快速验收：模块导入 + 单元测试 + 关键配置检查。"""
from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

MODULES = [
    "app.volume_cache",
    "app.ggo_segmentation",
    "app.lesion_classifier",
    "app.lung_segment_monai",
    "app.scheme_b_fusion",
    "app.lung_segment_3d",
    "app.lobe_locator",
    "app.lesion_morphology",
]

TESTS = [
    "tests.test_hu_classify.test_classify_nodule_hu_ggo",
    "tests.test_ggo_detect_v2.test_ggo_detect_v2_vessel_subtract",
    "tests.test_scheme_b_filter.test_filter_vessel_iou_relaxed",
    "tests.test_scheme_b_p2.test_lesion_multiclass",
    "tests.test_scheme_b_p2.test_pleural_distance_subpleural",
    "tests.test_scheme_b_p2.test_lung_stack2d",
    "tests.test_scheme_b_p2.test_volume_cache_roundtrip",
]


def _check_imports() -> list[str]:
    errors: list[str] = []
    for name in MODULES:
        try:
            importlib.import_module(name)
        except Exception as exc:
            errors.append(f"{name}: {exc}")
    return errors


def _run_tests() -> list[str]:
    errors: list[str] = []
    for dotted in TESTS:
        mod_name, fn_name = dotted.rsplit(".", 1)
        mod = importlib.import_module(mod_name)
        fn = getattr(mod, fn_name)
        try:
            fn()
        except Exception as exc:
            errors.append(f"{dotted}: {exc}")
    return errors


def main() -> int:
    print("=== Scheme B verify ===")
    print(f"GGO backend: {os.getenv('SCHEME_B_GGO_BACKEND', 'off')}")
    print(f"Skip vessel TS: {os.getenv('SCHEME_B_SKIP_VESSEL_SEG', 'true')}")
    print(f"Volume cache: {os.getenv('SCHEME_B_VOLUME_CACHE', 'true')}")

    import_errors = _check_imports()
    test_errors = _run_tests()

    if import_errors:
        print("\n[FAIL] Import errors:")
        for e in import_errors:
            print(f"  - {e}")
    else:
        print("\n[OK] All modules import")

    if test_errors:
        print("\n[FAIL] Test errors:")
        for e in test_errors:
            print(f"  - {e}")
    else:
        print("[OK] Spot-check tests passed")

    return 1 if (import_errors or test_errors) else 0


if __name__ == "__main__":
    raise SystemExit(main())
