#!/usr/bin/env python3
"""方案 B 金标准验收清单（文档 12.2）。

对 AI 识别结果 JSON 做规则校验，可用于人工标注序列回归。

用法:
    python scripts/scheme_b_gold_checklist.py result.json --profile ggo
    python scripts/scheme_b_gold_checklist.py result.json --profile solid_vessel
    python scripts/scheme_b_gold_checklist.py result.json --profile calcified
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROFILES = {
    "ggo": {
        "label": "明显 GGO",
        "rules": [
            ("overlay_bbox", lambda r: r.get("overlayType") == "bbox"),
            ("ggo_merged", lambda r: len(r.get("ggoRegions") or []) == 0),
            ("has_ggo_lesion", lambda r: any(
                (l.get("subType") in ("pureGGO", "mixedGGO")
                 or l.get("colorKey") == "ggo"
                 or l.get("type") == "磨玻璃结节")
                for l in (r.get("lesions") or [])
            )),
            ("has_contour", lambda r: any(
                len(l.get("contour") or []) >= 3 for l in (r.get("lesions") or [])
            )),
        ],
    },
    "solid_vessel": {
        "label": "实性结节贴血管",
        "rules": [
            ("has_solid", lambda r: any(
                l.get("colorKey") == "solid" or l.get("subType") == "solid"
                for l in (r.get("lesions") or [])
            )),
            ("not_all_filtered", lambda r: len(r.get("lesions") or []) >= 1),
            ("has_metrics", lambda r: all(
                k in ((r.get("lesions") or [{}])[0])
                for k in ("longAxisMm", "huMean", "detectionConfidence")
            ) if r.get("lesions") else False),
        ],
    },
    "calcified": {
        "label": "钙化灶",
        "rules": [
            ("has_calc", lambda r: any(
                l.get("colorKey") == "calcified"
                or l.get("subType") == "calcified"
                or "高密度" in (l.get("label") or "")
                for l in (r.get("lesions") or [])
            )),
            ("marker_diamond_or_yellow", lambda r: any(
                l.get("markerType") == "diamond" or l.get("colorKey") == "calcified"
                for l in (r.get("lesions") or [])
            )),
        ],
    },
}


def run_checklist(result: dict, profile: str) -> tuple[bool, list[str]]:
    spec = PROFILES.get(profile)
    if not spec:
        raise ValueError(f"unknown profile: {profile}")

    failures: list[str] = []
    for rule_id, fn in spec["rules"]:
        try:
            ok = bool(fn(result))
        except Exception as exc:
            ok = False
            failures.append(f"{rule_id}: exception {exc}")
            continue
        if not ok:
            failures.append(rule_id)

    return len(failures) == 0, failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("result_json", help="scheme-b result JSON（含 lesions/meta）")
    parser.add_argument(
        "--profile",
        choices=list(PROFILES.keys()),
        required=True,
    )
    args = parser.parse_args()

    path = Path(args.result_json)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    ok, failures = run_checklist(data, args.profile)
    label = PROFILES[args.profile]["label"]
    print(f"Profile: {label} ({args.profile})")
    print(f"Lesions: {len(data.get('lesions') or [])}")
    if ok:
        print("✅ 金标准验收通过")
        return 0
    print("❌ 未通过:")
    for f in failures:
        print(f"  - {f}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
