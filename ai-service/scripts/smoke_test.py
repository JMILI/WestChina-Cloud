#!/usr/bin/env python3
"""冒烟测试：验证所有方案引擎注册 + 本地 DICOM 链路。

用法:
    cd ai-service
    python scripts/smoke_test.py [dicom_dir]
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_engine_catalog():
    """测试 1：引擎列表。"""
    print("[TEST 1] Engine catalog")
    from app.engines import get_engine_catalog

    catalog = get_engine_catalog()
    ids = {e["id"] for e in catalog}
    print(f"  Engines: {ids}")

    assert "scheme-a" in ids, "scheme-a missing"
    assert "scheme-b" in ids, "scheme-b missing"
    assert "scheme-c" in ids, "scheme-c missing"
    assert "heuristic" not in ids, "heuristic should be removed"

    for e in catalog:
        assert "supportedModes" in e, f"{e['id']} missing supportedModes"
        assert isinstance(e["supportedModes"], list)

    print("  ✅ PASSED")


def test_robust_ct_loader():
    """测试 2：健壮 DICOM 加载器（子集）。"""
    print("[TEST 2] robust_ct_loader")
    from app.robust_ct_loader import sort_by_ipp
    import pydicom
    import numpy as np

    def fake_dicom(ipp_z=0.0, instance_number=1):
        ds = pydicom.Dataset()
        ds.ImagePositionPatient = [0.0, 0.0, ipp_z]
        ds.InstanceNumber = instance_number
        ds.Rows = 64
        ds.Columns = 64
        ds.PixelSpacing = [0.5, 0.5]
        ds.SliceThickness = 1.25
        ds.RescaleSlope = 1
        ds.RescaleIntercept = -1024
        ds.BitsStored = 16
        ds.BitsAllocated = 16
        ds.SamplesPerPixel = 1
        ds.PhotometricInterpretation = "MONOCHROME2"
        ds.PixelRepresentation = 0
        ds.PixelData = np.zeros((64, 64), dtype=np.uint16).tobytes()
        return ds

    dss = [fake_dicom(ipp_z=i) for i in range(3)]
    sorted_ds, method = sort_by_ipp(dss)
    assert method == "ipp", f"expected ipp, got {method}"
    print(f"  Sort method: {method}")
    print("  ✅ PASSED")


def test_scheme_a_detector():
    """测试 3：方案 A 检测器（模拟数据）。"""
    print("[TEST 3] scheme_a_detector")
    import numpy as np
    from app.scheme_a_detector import detect_single_slice
    from app.lung_segment_2d import segment_lungs_2d

    # 创建模拟肺区 CT
    slice_hu = np.full((512, 512), -1000.0, dtype=np.float32)  # 空气
    # 添加体部轮廓
    slice_hu[100:412, 100:412] = 0.0  # 软组织
    # 添加肺区（低密度）
    slice_hu[150:200, 120:250] = -800.0
    slice_hu[150:200, 262:392] = -800.0
    # 添加一个小结节
    slice_hu[175:180, 180:185] = 50.0

    lung_mask = segment_lungs_2d(slice_hu)
    lung_pixels = int(lung_mask.sum())
    print(f"  Lung pixels: {lung_pixels}")

    result = detect_single_slice(slice_hu, 0.5, 0.5, 0, lung_mask)
    n = len(result["lesions"])
    print(f"  Lesions found: {n}")
    print("  ✅ PASSED")


def test_volume_subsample():
    """测试 5：CPU 大序列降采样。"""
    print("[TEST 5] volume_subsample")
    import numpy as np
    from app.volume_subsample import subsample_volume_z, remap_lesions_slice_index

    vol = np.zeros((400, 64, 64), dtype=np.float32)
    spacing = (1.0, 0.5, 0.5)
    new_vol, new_sp, remap, info = subsample_volume_z(vol, spacing, 128)
    assert info["subsampled"] is True
    assert new_vol.shape[0] == 128
    assert new_sp[0] > spacing[0]
    lesions = [{"sliceIndex": 10, "id": "L1"}]
    out = remap_lesions_slice_index(lesions, remap)
    assert out[0]["sliceIndex"] == remap[10]
    print(f"  400→{new_vol.shape[0]} slices, z_spacing={new_sp[0]:.2f}")
    print("  ✅ PASSED")


def test_local_dicom_if_available():
    """测试 4：真实 DICOM（如可用）。"""
    print("[TEST 4] Local DICOM")
    dicom_dir = sys.argv[1] if len(sys.argv) > 1 else None
    if not dicom_dir or not os.path.isdir(dicom_dir):
        print("  ℹ️ 跳过（无 DICOM 目录）")
        return

    from scripts.test_local_dicom import find_dicom_files
    dcm_paths = find_dicom_files(dicom_dir)[:5]  # 只测 5 张
    if not dcm_paths:
        print("  ℹ️ 跳过（未找到 DICOM）")
        return

    from app.robust_ct_loader import load_series_dicoms
    raw_list = [open(p, "rb").read() for p in dcm_paths]
    meta = load_series_dicoms(raw_list)
    print(f"  Slices: {meta.slice_count}, Sort: {meta.sort_method}")
    print("  ✅ PASSED")


def main():
    print("=" * 60)
    print("WestChina CT AI — Smoke Tests")
    print("=" * 60)

    failed = 0
    for test_fn in [test_engine_catalog, test_robust_ct_loader,
                    test_scheme_a_detector, test_volume_subsample,
                    test_local_dicom_if_available]:
        try:
            test_fn()
        except Exception as e:
            print(f"  ❌ FAILED: {e}")
            failed += 1

    print(f"\n{'='*60}")
    if failed:
        print(f"{failed} TEST(S) FAILED")
        sys.exit(1)
    else:
        print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
