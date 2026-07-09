"""金标准 fixture 验收测试。"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

FIXTURES = Path(__file__).resolve().parent / "fixtures"
ROOT = Path(__file__).resolve().parent.parent


def _gold_module():
    path = ROOT / "scripts" / "scheme_b_gold_checklist.py"
    spec = importlib.util.spec_from_file_location("scheme_b_gold_checklist", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load(name: str) -> dict:
    with open(FIXTURES / name, encoding="utf-8") as f:
        return json.load(f)


def test_gold_ggo_fixture():
    ok, failures = _gold_module().run_checklist(_load("scheme_b_ggo.json"), "ggo")
    assert ok, failures


def test_gold_solid_vessel_fixture():
    ok, failures = _gold_module().run_checklist(_load("scheme_b_solid_vessel.json"), "solid_vessel")
    assert ok, failures


def test_gold_calcified_fixture():
    ok, failures = _gold_module().run_checklist(_load("scheme_b_calcified.json"), "calcified")
    assert ok, failures
