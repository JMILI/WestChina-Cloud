#!/usr/bin/env python3
"""将本地 DICOM 目录上传到 MinIO（按 IPP 排序后 1..N 命名）。

用法:
    cd ai-service
    PYTHONPATH=. python scripts/upload_dicom_to_minio.py \\
        ../ct_file/翁倩/翁倩/20210819000536 \\
        --bucket superadmin

可选:
    --max-slices 128    仅上传前 N 层（降采样后顺序仍正确）
    --dry-run           只打印 UID 与层数，不上传
"""
from __future__ import annotations

import argparse
import io
import json
import os
import sys

import pydicom

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.config import settings
from app.dicom_volume import _client, _object_key
from app.robust_ct_loader import filter_localizer, sort_by_ipp


def find_dicom_files(dir_path: str) -> list[str]:
    paths: list[str] = []
    for root, _dirs, files in os.walk(dir_path):
        for name in sorted(files):
            if name in ("DICOMDIR", "StudyInfo.dat"):
                continue
            paths.append(os.path.join(root, name))
    return paths


def prepare_sorted_datasets(dicom_dir: str, max_slices: int | None) -> tuple[list, dict]:
    paths = find_dicom_files(dicom_dir)
    if not paths:
        raise SystemExit(f"未找到 DICOM: {dicom_dir}")

    datasets = []
    for path in paths:
        try:
            datasets.append(pydicom.dcmread(path, force=True))
        except Exception as exc:
            print(f"  跳过无法解析: {path} ({exc})")

    kept, removed = filter_localizer(datasets)
    sorted_ds, sort_method = sort_by_ipp(kept)
    if not sorted_ds:
        raise SystemExit("过滤后无有效 CT 切片")

    if max_slices and len(sorted_ds) > max_slices:
        import numpy as np
        indices = np.linspace(0, len(sorted_ds) - 1, max_slices, dtype=int)
        indices = np.unique(indices)
        sorted_ds = [sorted_ds[i] for i in indices]

    study_uid = str(getattr(sorted_ds[0], "StudyInstanceUID", "") or "TEST.STUDY")
    series_uid = str(getattr(sorted_ds[0], "SeriesInstanceUID", "") or "TEST.SERIES")
    body_part = str(getattr(sorted_ds[0], "BodyPartExamined", "") or "CHEST")

    meta = {
        "bucket": None,
        "studyUid": study_uid,
        "seriesUid": series_uid,
        "imageCount": len(sorted_ds),
        "bodyPart": body_part,
        "sortMethod": sort_method,
        "removedLocalizers": removed,
        "sourceDir": os.path.abspath(dicom_dir),
    }
    return sorted_ds, meta


def upload_series(
    datasets: list,
    meta: dict,
    bucket: str,
    dry_run: bool = False,
) -> dict:
    meta = {**meta, "bucket": bucket}
    client = _client()

    if not dry_run:
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)

    for i, ds in enumerate(datasets, start=1):
        key = _object_key(meta["studyUid"], meta["seriesUid"], i)
        if dry_run:
            print(f"  [dry-run] {bucket}/{key}")
            continue
        buf = io.BytesIO()
        pydicom.dcmwrite(buf, ds, write_like_original=False)
        data = buf.getvalue()
        client.put_object(
            bucket,
            key,
            io.BytesIO(data),
            length=len(data),
            content_type="application/dicom",
        )
        if i % 100 == 0 or i == len(datasets):
            print(f"  已上传 {i}/{len(datasets)}")

    return meta


def main():
    parser = argparse.ArgumentParser(description="上传本地 DICOM 到 MinIO")
    parser.add_argument("dicom_dir", help="DICOM 目录")
    parser.add_argument("--bucket", default=os.getenv("MINIO_BUCKET", "superadmin"))
    parser.add_argument("--max-slices", type=int, default=0, help="最多上传层数，0=全部")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--out", default="", help="将 meta JSON 写入文件")
    args = parser.parse_args()

    max_slices = args.max_slices if args.max_slices > 0 else None
    print(f"准备上传: {args.dicom_dir}")
    print(f"MinIO: {settings.minio_endpoint}  bucket={args.bucket}")

    datasets, meta = prepare_sorted_datasets(args.dicom_dir, max_slices)
    print(
        f"Study={meta['studyUid']}\n"
        f"Series={meta['seriesUid']}\n"
        f"层数={meta['imageCount']} 排序={meta['sortMethod']} "
        f"部位={meta['bodyPart']}"
    )

    meta = upload_series(datasets, meta, args.bucket, dry_run=args.dry_run)
    print(json.dumps(meta, ensure_ascii=False, indent=2))

    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(meta, fh, ensure_ascii=False, indent=2)
        print(f"已写入 {args.out}")


if __name__ == "__main__":
    main()
