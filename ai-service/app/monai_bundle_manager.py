"""MONAI Model Zoo bundle 下载与管理。"""
from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

BUNDLE_NAME = "lung_nodule_ct_detection"
BUNDLE_VERSION = "0.6.10"


def get_models_root() -> Path:
    return Path(__file__).resolve().parent.parent / "models"


def get_bundle_dir() -> Path:
    return get_models_root() / BUNDLE_NAME


def is_monai_available() -> bool:
    try:
        import monai  # noqa: F401
        import torch  # noqa: F401

        return True
    except Exception:
        return False


def is_monai_bundle_ready() -> bool:
    bundle_dir = get_bundle_dir()
    return (bundle_dir / "models" / "model.pt").exists() and (
        bundle_dir / "configs" / "inference.json"
    ).exists()


def ensure_monai_bundle() -> Path:
    if not is_monai_available():
        raise RuntimeError(
            "MONAI 未安装。请执行: pip install monai torch torchvision nibabel"
        )

    bundle_dir = get_bundle_dir()
    if is_monai_bundle_ready():
        return bundle_dir

    models_root = get_models_root()
    models_root.mkdir(parents=True, exist_ok=True)
    logger.info("[MONAI] 正在下载 bundle %s v%s …", BUNDLE_NAME, BUNDLE_VERSION)

    try:
        from monai.bundle import download

        download(
            name=BUNDLE_NAME,
            version=BUNDLE_VERSION,
            bundle_dir=str(models_root),
            source="monaihosting",
        )
    except Exception as exc:
        raise RuntimeError(
            f"MONAI bundle 下载失败: {exc}。"
            "请检查网络或手动下载 lung_nodule_ct_detection 到 ai-service/models/"
        ) from exc

    if not is_monai_bundle_ready():
        raise RuntimeError(
            f"MONAI bundle 不完整，请确认 {bundle_dir}/models/model.pt 存在"
        )
    return bundle_dir
