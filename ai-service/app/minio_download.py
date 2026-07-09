"""MinIO 并行下载 DICOM 序列（方案 B P2）。"""
from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, List, Optional, Tuple

from .dicom_volume import _client, _object_key


def _download_one(bucket: str, study_uid: str, series_uid: str, index: int) -> Tuple[int, bytes]:
    client = _client()
    key = _object_key(study_uid, series_uid, index)
    response = client.get_object(bucket, key)
    try:
        return index, response.read()
    finally:
        response.close()
        response.release_conn()


def download_series_parallel(
    bucket: str,
    study_uid: str,
    series_uid: str,
    image_count: int,
    *,
    max_workers: Optional[int] = None,
    on_progress: Optional[Callable[[int, int], None]] = None,
    cancel_check: Optional[Callable[[], bool]] = None,
) -> List[bytes]:
    """并行下载 1..image_count，按序号返回 bytes 列表。"""
    if image_count <= 0:
        return []

    workers = max_workers or int(os.getenv("MINIO_DOWNLOAD_WORKERS", "8"))
    workers = max(1, min(workers, image_count))

    if workers == 1 or image_count <= 4:
        raw_list: List[Optional[bytes]] = [None] * image_count
        for i in range(1, image_count + 1):
            if cancel_check and cancel_check():
                raise RuntimeError("任务已取消")
            _, data = _download_one(bucket, study_uid, series_uid, i)
            raw_list[i - 1] = data
            if on_progress:
                on_progress(i, image_count)
        return [b for b in raw_list if b is not None]

    raw_map: dict[int, bytes] = {}
    completed = 0
    with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="minio-dl") as pool:
        futures = {
            pool.submit(_download_one, bucket, study_uid, series_uid, i): i
            for i in range(1, image_count + 1)
        }
        for fut in as_completed(futures):
            if cancel_check and cancel_check():
                for pending in futures:
                    pending.cancel()
                raise RuntimeError("任务已取消")
            idx, data = fut.result()
            raw_map[idx] = data
            completed += 1
            if on_progress:
                on_progress(completed, image_count)

    return [raw_map[i] for i in range(1, image_count + 1)]
