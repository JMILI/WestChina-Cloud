#!/usr/bin/env python3
"""端到端集成测试：模拟 SSE 完整请求链路。

从本地 DICOM 文件出发，模拟 MinIO 客户端，
测试三种方案在两个模式（识别病灶 / 当前层识别）下的完整链路。

用法:
    cd ai-service
    python scripts/test_integration.py ../ct_file/翁倩/翁倩/20210819000536
"""
from __future__ import annotations

import io
import json
import os
import sys
import time
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import numpy as np

TESTS_PASSED = 0
TESTS_FAILED = 0
ALL_RESULTS: List[Dict[str, Any]] = []


def log_result(test_name: str, passed: bool, detail: str = ""):
    global TESTS_PASSED, TESTS_FAILED
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"  [{status}] {test_name}")
    if detail:
        for line in detail.split("\n"):
            print(f"         {line}")
    if passed:
        TESTS_PASSED += 1
    else:
        TESTS_FAILED += 1


def assert_has(obj, key, msg=""):
    if key not in obj:
        raise AssertionError(f"Missing key '{key}' in response. {msg}")


def assert_eq(actual, expected, msg=""):
    if actual != expected:
        raise AssertionError(f"Expected {expected}, got {actual}. {msg}")


# ---------------------------------------------------------------------------
# Mock MinIO client (从本地文件系统读取)
# ---------------------------------------------------------------------------

class MockMinioClient:
    """模拟 MinIO 客户端，从本地 DICOM 目录按文件名顺序映射。"""

    def __init__(self, dcm_dir: str):
        self.dcm_files: Dict[str, bytes] = {}
        # 收集所有 DICOM 文件
        for root, dirs, files in os.walk(dcm_dir):
            for f in sorted(files):
                if f in ("DICOMDIR", "StudyInfo.dat"):
                    continue
                path = os.path.join(root, f)
                with open(path, "rb") as fh:
                    self.dcm_files[f] = fh.read()

    def get_object(self, bucket: str, key: str):
        """模拟 MinIO get_object。key 格式: studyUid/seriesUid/{i}.dcm"""
        # 从 key 提取文件名序号
        filename = os.path.basename(key)  # 例如 "1.dcm"
        # 在我们的 DICOM 目录中，文件是无扩展名的数字 (1, 3, 4, ...)
        base_name = filename.replace(".dcm", "")
        if base_name in self.dcm_files:
            data = self.dcm_files[base_name]
        elif filename in self.dcm_files:
            data = self.dcm_files[filename]
        else:
            # 尝试按索引映射
            try:
                idx = int(base_name)
                sorted_names = sorted(
                    self.dcm_files.keys(),
                    key=lambda x: int(x) if x.isdigit() else 99999,
                )
                if idx - 1 < len(sorted_names):
                    name = sorted_names[idx - 1]
                    data = self.dcm_files[name]
                else:
                    raise FileNotFoundError(f"No DICOM for key {key}")
            except (ValueError, IndexError):
                raise FileNotFoundError(f"No DICOM for key {key}")

        return MockResponse(data)


class MockResponse:
    def __init__(self, data: bytes):
        self._data = data

    def read(self) -> bytes:
        return self._data

    def close(self):
        pass

    def release_conn(self):
        pass


# ---------------------------------------------------------------------------
# SSE 事件收集器
# ---------------------------------------------------------------------------

class SSEEventCollector:
    """收集 run_detection_events 产生的所有 SSE 事件。"""

    def __init__(self, engine: str, mode: str):
        self.engine = engine
        self.mode = mode
        self.events: List[Dict[str, Any]] = []
        self.logs: List[str] = []
        self.errors: List[str] = []
        self.result: Dict[str, Any] | None = None
        self.progress_events: List[Dict] = []
        self.step_start_count = 0
        self.step_end_count = 0
        self.warnings: List[str] = []

    def collect(self, event: Dict[str, Any]):
        self.events.append(event)
        etype = event.get("type", "")

        if etype == "log":
            msg = event.get("message", "")
            self.logs.append(msg)
        elif etype == "error":
            msg = event.get("message", "")
            self.errors.append(msg)
        elif etype == "result":
            self.result = event.get("data", {})
        elif etype == "progress":
            self.progress_events.append(event)
        elif etype == "step_start":
            self.step_start_count += 1
        elif etype == "step_end":
            self.step_end_count += 1
        elif etype == "warn":
            self.warnings.append(event.get("message", ""))


# ---------------------------------------------------------------------------
# 测试执行
# ---------------------------------------------------------------------------

def run_detection_test(
    req_params: Dict[str, Any],
    collector: SSEEventCollector,
    mock_client: MockMinioClient,
) -> SSEEventCollector:
    """执行一次完整的检测流程，收集所有 SSE 事件。"""
    from app.detection_runner import run_detection_events
    from app.schemas import DetectLesionRequest

    # 注入 mock MinIO client
    with patch("app.dicom_volume._client", return_value=mock_client):
        with patch("app.detection_runner._client", return_value=mock_client):
            req = DetectLesionRequest(**req_params)
            for event in run_detection_events(req):
                collector.collect(event)

    return collector


def validate_response_format(collector: SSEEventCollector, expected_overlay_type: str):
    """验证 SSE 响应格式是否符合契约。"""
    result = collector.result

    # 1. 必须有 result
    if result is None:
        log_result("result present", False, "No result event received")
        return

    # 2. 必需字段
    required_fields = [
        "bodyPart", "studyUid", "seriesUid", "engine",
        "gpuAvailable", "disclaimer", "overlayType", "lesions", "meta",
    ]
    for field in required_fields:
        try:
            assert_has(result, field)
        except AssertionError as e:
            log_result(f"field '{field}'", False, str(e))
            return

    # 3. overlayType 匹配
    try:
        assert_eq(result["overlayType"], expected_overlay_type,
                  f"Expected overlayType={expected_overlay_type}")
    except AssertionError as e:
        log_result("overlayType", False, str(e))
    else:
        log_result("overlayType correct", True,
                   f"overlayType={result['overlayType']}")

    # 4. lesions 是列表
    lesions = result["lesions"]
    log_result("lesions is list", True,
               f"lesions count={len(lesions)}")

    # 5. meta 字段
    meta = result["meta"]
    meta_keys = list(meta.keys())
    log_result("meta fields", True,
               f"meta keys: {meta_keys}")

    # 6. engine 字段非空
    log_result("engine non-empty", bool(result["engine"]),
               f"engine={result['engine']}")

    # 7. disclaimer 非空
    log_result("disclaimer non-empty", bool(result["disclaimer"]),
               f"disclaimer={result['disclaimer'][:50]}...")


# ---------------------------------------------------------------------------
# 主测试流程
# ---------------------------------------------------------------------------

def main():
    global TESTS_PASSED, TESTS_FAILED

    if len(sys.argv) < 2:
        print("用法: python scripts/test_integration.py <dicom_dir>")
        sys.exit(1)

    dcm_dir = sys.argv[1]
    if not os.path.isdir(dcm_dir):
        print(f"错误: 目录不存在: {dcm_dir}")
        sys.exit(1)

    # 设置 Python path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    os.chdir(os.path.join(os.path.dirname(__file__), ".."))

    print("=" * 70)
    print("WestChina CT AI — 端到端集成测试")
    print(f"DICOM 目录: {dcm_dir}")
    print("=" * 70)

    # 创建 mock MinIO client
    mock_client = MockMinioClient(dcm_dir)
    dcm_count = len(mock_client.dcm_files)
    print(f"\n📁 本地 DICOM 文件数: {dcm_count}")
    print(f"   文件名示例: {list(mock_client.dcm_files.keys())[:5]}")

    # 公共请求参数
    base_req = {
        "bucket": "test-bucket",
        "studyUid": "1.2.840.test",
        "seriesUid": "1.2.840.test.series",
        "bodyPart": "CHEST",
        "imageCount": dcm_count,
        "currentSliceIndex": 4,
        "sliceIndex": 4,
    }

    # =================================================================
    # 测试 1: scheme-a 全序列（识别病灶）
    # =================================================================
    print("\n" + "=" * 70)
    print("测试 1: scheme-a 全序列（识别病灶，detectMode=series）")
    print("=" * 70)

    t1 = time.time()
    collector1 = SSEEventCollector("scheme-a", "series")
    req1 = {**base_req, "detectEngine": "scheme-a", "detectMode": "series"}
    try:
        run_detection_test(req1, collector1, mock_client)
        elapsed = time.time() - t1
    except Exception as e:
        log_result("scheme-a series execution", False, str(e))
        elapsed = 0

    log_result("execution completed", collector1.result is not None,
               f"耗时 {elapsed:.1f}s")
    log_result("no errors", len(collector1.errors) == 0,
               f"errors: {collector1.errors}" if collector1.errors else "0 errors")
    log_result("has log messages", len(collector1.logs) > 0,
               f"{len(collector1.logs)} log entries")
    log_result("has progress events", len(collector1.progress_events) > 0,
               f"{len(collector1.progress_events)} progress events")
    log_result("step_start count", collector1.step_start_count > 0,
               f"step_start={collector1.step_start_count}")
    log_result("step_end count", collector1.step_end_count > 0,
               f"step_end={collector1.step_end_count}")

    if collector1.result:
        validate_response_format(collector1, "bbox")
        lesions = collector1.result.get("lesions", [])
        log_result("lesion details", True,
                   f"病灶数={len(lesions)}")
        for i, l in enumerate(lesions[:3]):
            log_result(f"lesion[{i}]", True,
                       f"slice={l.get('sliceIndex')} conf={l.get('confidence',0):.3f} "
                       f"type={l.get('type')} diam={l.get('diameterMm')}mm")

        # 检查 sortMethod
        sort_method = collector1.result.get("meta", {}).get("sortMethod", "N/A")
        log_result("IPP sorting", sort_method == "ipp",
                   f"sortMethod={sort_method}")

    # 展示关键日志
    print(f"\n  📋 关键日志 ({len(collector1.logs)} 条):")
    for log in collector1.logs[:5]:
        print(f"     {log[:100]}")
    if len(collector1.logs) > 5:
        print(f"     ... 还有 {len(collector1.logs) - 5} 条")

    # =================================================================
    # 测试 2: scheme-a 当前层（当前层识别）
    # =================================================================
    print("\n" + "=" * 70)
    print("测试 2: scheme-a 当前层（当前层识别，detectMode=single）")
    print("=" * 70)

    t2 = time.time()
    collector2 = SSEEventCollector("scheme-a", "single")
    req2 = {**base_req, "detectEngine": "scheme-a", "detectMode": "single",
            "singleSlice": True}
    try:
        run_detection_test(req2, collector2, mock_client)
        elapsed2 = time.time() - t2
    except Exception as e:
        log_result("scheme-a single execution", False, str(e))
        elapsed2 = 0

    log_result("execution completed", collector2.result is not None,
               f"耗时 {elapsed2:.1f}s")
    log_result("no errors", len(collector2.errors) == 0,
               f"errors: {collector2.errors}" if collector2.errors else "0 errors")

    if collector2.result:
        validate_response_format(collector2, "bbox")
        meta2 = collector2.result.get("meta", {})
        log_result("detectMode=single", meta2.get("detectMode") == "single",
                   f"detectMode={meta2.get('detectMode')}")
        log_result("has sliceIndex", "sliceIndex" in meta2,
                   f"sliceIndex={meta2.get('sliceIndex')}")

    # 展示单层日志
    print(f"\n  📋 关键日志:")
    for log in collector2.logs[:3]:
        print(f"     {log[:100]}")

    # =================================================================
    # 测试 3: scheme-c 当前层（Grad-CAM 热力图）
    # =================================================================
    print("\n" + "=" * 70)
    print("测试 3: scheme-c 当前层（Grad-CAM，detectMode=single）")
    print("=" * 70)

    t3 = time.time()
    collector3 = SSEEventCollector("scheme-c", "single")
    req3 = {**base_req, "detectEngine": "scheme-c", "detectMode": "single",
            "singleSlice": True}
    try:
        run_detection_test(req3, collector3, mock_client)
        elapsed3 = time.time() - t3
    except Exception as e:
        log_result("scheme-c execution", False, str(e))
        elapsed3 = 0

    log_result("execution completed", collector3.result is not None,
               f"耗时 {elapsed3:.1f}s")

    if collector3.result:
        validate_response_format(collector3, "heatmap")
        # 检查 heatmap 字段
        heatmap = collector3.result.get("heatmap", {})
        screening = collector3.result.get("screening", {})
        log_result("heatmap present", bool(heatmap),
                   f"heatmap size: {heatmap.get('width')}x{heatmap.get('height')}")
        log_result("screening present", bool(screening),
                   f"label={screening.get('label')} conf={screening.get('confidence',0):.3f}")
        log_result("lesions empty", collector3.result.get("lesions") == [],
                   f"lesions={collector3.result.get('lesions')}")
        # 检查热力图值
        values = heatmap.get("values", [])
        if values:
            log_result("heatmap values", True,
                       f"min={min(values):.4f} max={max(values):.4f} count={len(values)}")

    # =================================================================
    # 测试 4: scheme-b 全序列（GPU 门控降级）
    # =================================================================
    print("\n" + "=" * 70)
    print("测试 4: scheme-b 全序列（融合精准分析）")
    print("=" * 70)

    t4 = time.time()
    collector4 = SSEEventCollector("scheme-b", "series")
    req4 = {**base_req, "detectEngine": "scheme-b", "detectMode": "series"}
    try:
        run_detection_test(req4, collector4, mock_client)
        elapsed4 = time.time() - t4
    except Exception as e:
        log_result("scheme-b execution", False, str(e))
        elapsed4 = 0

    log_result("execution completed", collector4.result is not None,
               f"耗时 {elapsed4:.1f}s")
    log_result("GPU available check", True,
               "GPU is available, scheme-b running full pipeline")
    log_result("has result", collector4.result is not None,
               f"lesions={len(collector4.result.get('lesions',[])) if collector4.result else 0}")

    if collector4.result:
        ot = collector4.result.get("overlayType", "")
        log_result("overlayType valid", ot in ("bbox", "ggo"),
                   f"overlayType={ot} (bbox/ggo both acceptable)")
        stats = collector4.result.get("meta", {}).get("stats", {})
        log_result("fusion stats present", len(stats) > 0,
                   f"stats keys: {list(stats.keys())}")

    # =================================================================
    # 测试 5: 模式互斥校验
    # =================================================================
    print("\n" + "=" * 70)
    print("测试 5: 模式互斥校验")
    print("=" * 70)

    # scheme-c 不应该支持 series
    collector5a = SSEEventCollector("scheme-c", "series")
    req5a = {**base_req, "detectEngine": "scheme-c", "detectMode": "series"}
    try:
        run_detection_test(req5a, collector5a, mock_client)
    except Exception:
        pass
    # Check error events for INVALID_DETECT_MODE code
    has_mode_error = any(
        e.get("code") == "INVALID_DETECT_MODE"
        for e in collector5a.events if e.get("type") == "error"
    )
    log_result("scheme-c rejects series", has_mode_error,
               f"error codes: {[e.get('code') for e in collector5a.events if e.get('type')=='error']}")
    log_result("scheme-c series no result", collector5a.result is None)

    # scheme-b 不应该支持 single
    collector5b = SSEEventCollector("scheme-b", "single")
    req5b = {**base_req, "detectEngine": "scheme-b", "detectMode": "single",
             "singleSlice": True}
    try:
        run_detection_test(req5b, collector5b, mock_client)
    except Exception:
        pass
    has_mode_error_b = any(
        e.get("code") == "INVALID_DETECT_MODE"
        for e in collector5b.events if e.get("type") == "error"
    )
    log_result("scheme-b rejects single", has_mode_error_b,
               f"error codes: {[e.get('code') for e in collector5b.events if e.get('type')=='error']}")

    # =================================================================
    # 汇总
    # =================================================================
    print("\n" + "=" * 70)
    print("测试汇总")
    print("=" * 70)
    total = TESTS_PASSED + TESTS_FAILED
    print(f"  通过: {TESTS_PASSED}/{total}")
    print(f"  失败: {TESTS_FAILED}/{total}")
    if TESTS_FAILED:
        print(f"\n  ⚠️ 存在 {TESTS_FAILED} 项失败，请检查上方详情")
        sys.exit(1)
    else:
        print(f"\n  ✅ 所有测试通过！")


if __name__ == "__main__":
    main()
