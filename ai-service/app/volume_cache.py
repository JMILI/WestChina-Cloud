"""方案 B 体数据磁盘缓存（P2 剩余项 1-P2-01）。"""
from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Optional, Tuple

import numpy as np

from .log_paths import ai_cache_dir
from .robust_ct_loader import VolumeMeta

CACHE_VERSION = 2


def _cache_enabled() -> bool:
    return os.getenv("SCHEME_B_VOLUME_CACHE", "true").lower() in ("1", "true", "yes")


def _cache_dir() -> Path:
    root = os.getenv("SCHEME_B_CACHE_DIR", "").strip()
    if root:
        return Path(root)
    return ai_cache_dir()


def _spacing_key(spacing: Tuple[float, float, float]) -> str:
    return ",".join(f"{float(s):.6f}" for s in spacing)


def _volume_fingerprint(volume: np.ndarray, spacing: Tuple[float, float, float]) -> str:
    raw = (
        f"{volume.shape}|{_spacing_key(spacing)}|"
        f"{float(np.mean(volume)):.8f}|{float(np.std(volume)):.8f}|"
        f"{float(volume.flat[0]):.4f}|{float(volume.flat[-1]):.4f}"
    )
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _cache_key(
    study_uid: str,
    series_uid: str,
    image_count: int,
    spacing: Optional[Tuple[float, float, float]] = None,
) -> str:
    raw = f"v{CACHE_VERSION}|{study_uid}|{series_uid}|{image_count}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


def _cache_paths(key: str) -> tuple[Path, Path, Path]:
    base = _cache_dir() / key
    return base / "volume.npy", base / "meta.json", base


def _ttl_sec() -> int:
    return int(os.getenv("SCHEME_B_CACHE_TTL_SEC", str(7 * 24 * 3600)))


def try_load_cached_volume(
    study_uid: str,
    series_uid: str,
    image_count: int,
) -> Optional[VolumeMeta]:
    if not _cache_enabled():
        return None
    key = _cache_key(study_uid, series_uid, image_count)
    vol_path, meta_path, base = _cache_paths(key)
    if not vol_path.exists() or not meta_path.exists():
        return None
    age = time.time() - vol_path.stat().st_mtime
    if age > _ttl_sec():
        return None
    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            meta_dict = json.load(f)
        volume = np.load(vol_path)
        spacing = tuple(meta_dict["spacing"])
        expected_fp = meta_dict.get("volumeFingerprint")
        if expected_fp:
            actual_fp = _volume_fingerprint(volume.astype(np.float32), spacing)
            if actual_fp != expected_fp:
                return None
        return VolumeMeta(
            volume=volume.astype(np.float32),
            spacing=spacing,
            rows=int(meta_dict["rows"]),
            cols=int(meta_dict["cols"]),
            slice_count=int(meta_dict["slice_count"]),
            sort_method=str(meta_dict.get("sort_method", "ipp")),
            removed_localizers=int(meta_dict.get("removed_localizers", 0)),
            file_slice_indices=list(meta_dict.get("file_slice_indices", [])),
        )
    except Exception:
        return None


def save_volume_cache(meta: VolumeMeta, study_uid: str, series_uid: str) -> None:
    if not _cache_enabled():
        return
    key = _cache_key(study_uid, series_uid, meta.slice_count, meta.spacing)
    vol_path, meta_path, base = _cache_paths(key)
    try:
        base.mkdir(parents=True, exist_ok=True)
        vol = meta.volume.astype(np.float32)
        np.save(vol_path, vol)
        payload = {
            "cacheVersion": CACHE_VERSION,
            "spacing": list(meta.spacing),
            "rows": meta.rows,
            "cols": meta.cols,
            "slice_count": meta.slice_count,
            "sort_method": meta.sort_method,
            "removed_localizers": meta.removed_localizers,
            "file_slice_indices": meta.file_slice_indices,
            "volumeFingerprint": _volume_fingerprint(vol, meta.spacing),
            "studyUid": study_uid,
            "seriesUid": series_uid,
            "cachedAt": int(time.time()),
        }
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(payload, f)
    except Exception:
        pass


def invalidate_volume_cache(study_uid: str, series_uid: str, image_count: int) -> None:
    key = _cache_key(study_uid, series_uid, image_count)
    _, _, base = _cache_paths(key)
    if base.exists():
        for p in base.glob("*"):
            try:
                p.unlink()
            except Exception:
                pass
        try:
            base.rmdir()
        except Exception:
            pass
