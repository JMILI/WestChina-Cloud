#!/usr/bin/env python3
"""将 MinIO 中已上传的 DICOM 序列按 IPP/InstanceNumber 重排为 1.dcm…N.dcm。

用法:
  python scripts/resort-minio-series.py \\
    --bucket renmin \\
    --series-uid 1.3.12.2.1107.5.1.4.77426.30000021081723585752900180617
"""
from __future__ import annotations

import argparse
import io
import os
import sys
import tempfile

import pydicom
from minio import Minio

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ai-service"))

from app.robust_ct_loader import _get_ipp, sort_by_ipp  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Resort DICOM series in MinIO")
    parser.add_argument("--bucket", required=True)
    parser.add_argument("--series-uid", required=True)
    parser.add_argument("--endpoint", default=os.getenv("MINIO_ENDPOINT", "127.0.0.1:9000"))
    parser.add_argument("--access-key", default=os.getenv("MINIO_ACCESS_KEY", "admin"))
    parser.add_argument("--secret-key", default=os.getenv("MINIO_SECRET_KEY", "admin123456"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    client = Minio(args.endpoint, access_key=args.access_key, secret_key=args.secret_key, secure=False)
    prefix = ""
    folder = None
    objects = []
    for obj in client.list_objects(args.bucket, prefix="", recursive=True):
        if args.series_uid in obj.object_name and obj.object_name.endswith(".dcm"):
            objects.append(obj.object_name)
    if not objects:
        print("未找到 DICOM 对象")
        sys.exit(1)
    sample = objects[0]
    folder = sample.rsplit("/", 1)[0]
    print(f"bucket={args.bucket} folder={folder} count={len(objects)}")

    datasets = []
    for name in sorted(objects, key=lambda p: int(p.rsplit("/", 1)[-1].replace(".dcm", "") or 0)):
        resp = client.get_object(args.bucket, name)
        raw = resp.read()
        resp.close()
        resp.release_conn()
        ds = pydicom.dcmread(io.BytesIO(raw), force=True)
        datasets.append((name, ds, raw))

    sorted_ds, method = sort_by_ipp([ds for _, ds, _ in datasets])
    name_map = {id(ds): name for name, ds, _ in datasets}
    raw_map = {id(ds): raw for _, ds, raw in datasets}

    print(f"sort_method={method}")
    for i, ds in enumerate(sorted_ds[:5]):
        ipp = _get_ipp(ds)
        inum = getattr(ds, "InstanceNumber", None)
        z = ipp[2] if ipp else None
        print(f"  -> {i+1}.dcm  instance={inum}  ipp_z={z}")
    print("  ...")

    if args.dry_run:
        print("dry-run，未写入 MinIO")
        return

    tmp_prefix = f"{folder}/.__resort_tmp__/"
    # 先写到临时 key，避免覆盖
    for i, ds in enumerate(sorted_ds):
        tmp_key = f"{tmp_prefix}{i+1}.dcm"
        client.put_object(args.bucket, tmp_key, io.BytesIO(raw_map[id(ds)]), len(raw_map[id(ds)]))

    for i in range(len(sorted_ds)):
        src = f"{tmp_prefix}{i+1}.dcm"
        dst = f"{folder}/{i+1}.dcm"
        client.copy_object(args.bucket, dst, f"/{args.bucket}/{src}")

    for obj in objects:
        client.remove_object(args.bucket, obj)
    for i in range(len(sorted_ds)):
        client.remove_object(args.bucket, f"{tmp_prefix}{i+1}.dcm")

    print(f"完成：{len(sorted_ds)} 张已按 {method} 重排为 1.dcm…{len(sorted_ds)}.dcm")


if __name__ == "__main__":
    main()
