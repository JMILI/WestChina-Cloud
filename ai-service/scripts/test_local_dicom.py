#!/usr/bin/env python3
"""本地 DICOM 测试脚本。

从本地文件系统读取 DICOM 文件，测试各方案链路，不依赖 MinIO。

用法:
    cd ai-service
    python scripts/test_local_dicom.py ../ct_file/翁倩/翁倩/20210819000536
"""
from __future__ import annotations

import os
import sys
import time
from typing import List


def find_dicom_files(dir_path: str) -> List[str]:
    """递归查找目录中的 DICOM 文件（排除 DICOMDIR 和 StudyInfo.dat）。"""
    dcm_files = []
    for root, dirs, files in os.walk(dir_path):
        for f in sorted(files):
            if f in ("DICOMDIR", "StudyInfo.dat"):
                continue
            path = os.path.join(root, f)
            # 尝试判断是否为 DICOM（检查文件头）
            try:
                with open(path, "rb") as fh:
                    header = fh.read(132)
                if header[128:132] == b"DICM":
                    dcm_files.append(path)
                else:
                    # 可能是无头 DICOM，仍加入
                    dcm_files.append(path)
            except Exception:
                dcm_files.append(path)
    return dcm_files


def test_robust_ct_loader(dcm_paths: List[str]):
    """测试 1：robust_ct_loader IPP 排序。"""
    print("\n" + "=" * 60)
    print("测试 1: robust_ct_loader（IPP 排序 + 过滤定位像）")
    print("=" * 60)

    raw_list = []
    for p in dcm_paths:
        with open(p, "rb") as f:
            raw_list.append(f.read())

    from app.robust_ct_loader import load_series_dicoms, sort_by_ipp, filter_localizer

    t0 = time.time()
    meta = load_series_dicoms(raw_list)
    elapsed = time.time() - t0

    print(f"  文件数: {len(dcm_paths)}")
    print(f"  有效切片: {meta.slice_count}")
    print(f"  移除定位像: {meta.removed_localizers}")
    print(f"  排序方式: {meta.sort_method}")
    print(f"  体数据形状: {meta.volume.shape}")
    print(f"  Spacing (z,y,x): {meta.spacing}")
    print(f"  HU 范围: [{meta.volume.min():.0f}, {meta.volume.max():.0f}]")
    print(f"  耗时: {elapsed:.2f}s")

    # 验证排序
    if meta.sort_method == "ipp":
        print("  ✅ IPP 排序成功")
    elif meta.sort_method == "instance_number":
        print("  ⚠️ 回退到 InstanceNumber 排序")
    else:
        print("  ⚠️ 回退到文件名顺序")

    return meta


def test_lung_segment_2d(meta):
    """测试 2：2D 肺分割。"""
    print("\n" + "=" * 60)
    print("测试 2: lung_segment_2d（2D 肺区分割）")
    print("=" * 60)

    from app.lung_segment_2d import segment_lungs_2d

    # 取中间层
    mid = meta.volume.shape[0] // 2
    slice_hu = meta.volume[mid]

    t0 = time.time()
    lung_mask = segment_lungs_2d(slice_hu)
    elapsed = time.time() - t0

    lung_pixels = int(lung_mask.sum())
    total_pixels = slice_hu.size

    print(f"  测试层: {mid}")
    print(f"  图像尺寸: {slice_hu.shape}")
    print(f"  肺区像素: {lung_pixels} ({100 * lung_pixels / total_pixels:.1f}%)")
    print(f"  耗时: {elapsed:.3f}s")

    if lung_pixels > 500:
        print(f"  ✅ 肺分割成功")
    else:
        print(f"  ❌ 肺区过小（可能非胸部 CT 或算法问题）")

    return lung_mask, slice_hu, mid


def test_scheme_a_single(slice_hu, spacing, slice_index, lung_mask):
    """测试 3：方案 A 单层检测。"""
    print("\n" + "=" * 60)
    print("测试 3: scheme_a_detector.detect_single_slice（方案 A 单层）")
    print("=" * 60)

    from app.scheme_a_detector import detect_single_slice

    t0 = time.time()
    result = detect_single_slice(
        slice_hu, spacing[1], spacing[2], slice_index, lung_mask
    )
    elapsed = time.time() - t0

    lesions = result["lesions"]
    stats = result["stats"]

    print(f"  候选区域: {stats['candidates']}")
    print(f"  检出病灶: {len(lesions)}")
    print(f"  HU 阈值: {stats.get('huThreshold', 'N/A')}")
    print(f"  Solidity 阈值: {stats.get('solidityMin', 'N/A')}")
    print(f"  耗时: {elapsed:.3f}s")

    for i, l in enumerate(lesions[:5]):
        print(f"\n  病灶 {i + 1}:")
        print(f"    ID: {l['id']}")
        print(f"    类型: {l['type']} ({l['label']})")
        print(f"    置信度: {l['confidence']:.3f}")
        print(f"    直径: {l['diameterMm']} mm")
        print(f"    HU: {l.get('hu', 'N/A')}")
        print(f"    BBox: x={l['bbox']['x']:.3f} y={l['bbox']['y']:.3f} "
              f"w={l['bbox']['width']:.3f} h={l['bbox']['height']:.3f}")
        print(f"    SliceIndex: {l['sliceIndex']}")

    if lesions:
        print(f"\n  ✅ 方案 A 单层检测成功")
    else:
        print(f"\n  ℹ️ 未检出病灶（可能该层面无可疑区域）")

    return result


def test_png_export(meta, result, lung_mask, slice_index):
    """导出标注结果到 PNG 便于人工检查。"""
    import numpy as np

    print("\n" + "=" * 60)
    print("测试 4: 导出标注 PNG")
    print("=" * 60)

    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("  ⚠️ Pillow 未安装，跳过 PNG 导出")
        return

    slice_hu = meta.volume[slice_index]
    hu_clipped = np.clip(slice_hu, -1024, 400)
    gray = ((hu_clipped + 1024) / 1424.0 * 255).astype(np.uint8)
    img = Image.fromarray(gray).convert("RGB")
    draw = ImageDraw.Draw(img)
    rows, cols = slice_hu.shape

    # 画肺区轮廓（半透明）
    try:
        from skimage.measure import find_contours
        import numpy as np
        contours = find_contours(lung_mask.astype(float), 0.5)
        for contour in contours:
            pts = [(c[1], c[0]) for c in contour[::3]]
            if len(pts) >= 2:
                for i in range(len(pts) - 1):
                    draw.line([pts[i], pts[i + 1]], fill=(0, 100, 255), width=1)
    except Exception as e:
        print(f"  肺轮廓绘制跳过: {e}")

    # 画病灶 bbox
    for l in result["lesions"]:
        b = l["bbox"]
        x0 = int(b["x"] * cols)
        y0 = int(b["y"] * rows)
        x1 = int((b["x"] + b["width"]) * cols)
        y1 = int((b["y"] + b["height"]) * rows)
        draw.rectangle([x0, y0, x1, y1], outline=(255, 50, 50), width=2)

    out_path = "/tmp/scheme_a_annotated.png"
    img.save(out_path)
    print(f"  标注图保存到: {out_path}")
    print(f"  蓝色轮廓 = 肺区, 红色框 = 病灶")
    print(f"  ✅ PNG 导出成功")


def main():
    if len(sys.argv) < 2:
        print("用法: python scripts/test_local_dicom.py <dicom_dir>")
        print("示例: python scripts/test_local_dicom.py ../ct_file/翁倩/翁倩/20210819000536")
        sys.exit(1)

    dcm_dir = sys.argv[1]
    if not os.path.isdir(dcm_dir):
        print(f"错误: 目录不存在: {dcm_dir}")
        sys.exit(1)

    # 将 ai-service/app 加入 path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    os.chdir(os.path.join(os.path.dirname(__file__), ".."))

    print("=" * 60)
    print("WestChina CT AI — 本地 DICOM 测试")
    print("=" * 60)
    print(f"DICOM 目录: {dcm_dir}")

    dcm_paths = find_dicom_files(dcm_dir)
    print(f"找到 {len(dcm_paths)} 个 DICOM 文件")

    if not dcm_paths:
        print("错误: 未找到 DICOM 文件")
        sys.exit(1)

    # 测试 1: robust_ct_loader
    meta = test_robust_ct_loader(dcm_paths)

    # 测试 2: 2D 肺分割
    lung_mask, slice_hu, slice_index = test_lung_segment_2d(meta)

    # 测试 3: 方案 A 单层检测
    result = test_scheme_a_single(slice_hu, meta.spacing, slice_index, lung_mask)

    # 测试 4: PNG 导出
    test_png_export(meta, result, lung_mask, slice_index)

    # 测试 5: 方案 C Grad-CAM（尝试）
    print("\n" + "=" * 60)
    print("测试 5: scheme_c_screening（Grad-CAM 热力图）")
    print("=" * 60)
    try:
        from app.scheme_c_screening import predict
        t0 = time.time()
        result_c = predict(slice_hu)
        elapsed = time.time() - t0

        screening = result_c["screening"]
        heatmap = result_c["heatmap"]
        print(f"  分类: {screening['label']}")
        print(f"  置信度: {screening['confidence']:.3f}")
        print(f"  热力图尺寸: {heatmap['width']}×{heatmap['height']}")
        print(f"  热力图值范围: [{min(heatmap['values']):.3f}, {max(heatmap['values']):.3f}]")
        print(f"  耗时: {elapsed:.2f}s")
        print(f"  免责声明: {screening.get('disclaimer', 'N/A')}")
        print(f"  ✅ 方案 C Grad-CAM 管线可用")
    except ImportError as e:
        print(f"  ⚠️ 方案 C 跳过（依赖缺失: {e}）")
    except Exception as e:
        print(f"  ⚠️ 方案 C 执行失败: {e}")

    print("\n" + "=" * 60)
    print("全部测试完成")
    print("=" * 60)


if __name__ == "__main__":
    import numpy as np
    main()
