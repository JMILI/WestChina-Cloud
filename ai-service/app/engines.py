"""识别引擎注册与可用性探测。"""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List

from .monai_bundle_manager import is_monai_available, is_monai_bundle_ready
from .nndet_wrapper import is_nndet_available, is_nndet_weights_ready


@dataclass
class EngineMeta:
    id: str
    label: str
    description: str
    available: bool = True
    supported_modes: List[str] = field(default_factory=lambda: ["series", "single"])
    unavailable_reason: str = ""
    install_hint: str = ""
    requires_gpu: bool = False
    # 方案 B 子引擎列表，其他引擎为 None
    sub_engines: List[Dict[str, Any]] | None = None

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "id": self.id,
            "label": self.label,
            "description": self.description,
            "available": self.available,
            "supportedModes": self.supported_modes,
        }
        if self.unavailable_reason:
            d["unavailableReason"] = self.unavailable_reason
        if self.install_hint:
            d["installHint"] = self.install_hint
        if self.requires_gpu:
            d["requiresGpu"] = True
        if self.sub_engines:
            d["subEngines"] = self.sub_engines
        return d


def _totalsegmentator_available() -> bool:
    try:
        import totalsegmentator  # noqa: F401
        return True
    except Exception:
        return False


def _torch_available() -> bool:
    try:
        import torch  # noqa: F401
        return True
    except Exception:
        return False


def _gpu_available() -> bool:
    try:
        import torch
        return torch.cuda.is_available()
    except Exception:
        return False


_ENGINES: List[EngineMeta] = []
_CATALOG_CACHE: List[Dict[str, Any]] | None = None
_CATALOG_TS = 0.0
_CATALOG_TTL_SEC = 60.0
_CATALOG_LOCK = threading.Lock()


def _build_scheme_b_sub_engines() -> List[Dict[str, Any]]:
    """构建方案 B 子引擎列表。"""
    monai_ready = is_monai_available() and is_monai_bundle_ready()
    nndet_ready = is_nndet_available() and is_nndet_weights_ready()
    return [
        {
            "id": "auto",
            "label": "自动",
            "description": "自动选择最优检测器（nnDetection 优先 → MONAI 回退）",
            "available": True,
        },
        {
            "id": "monai",
            "label": "MONAI RetinaNet",
            "description": "MONAI LUNA16 bundle (RetinaNet) — 当前可用",
            "available": monai_ready,
            "unavailableReason": "MONAI bundle 未就绪" if not monai_ready else "",
        },
        {
            "id": "nndet",
            "label": "nnDetection (LUNA16)",
            "description": "nnDetection Retina U-Net — 需下载权重",
            "available": nndet_ready,
            "unavailableReason": (
                "nnDetection 权重未就绪。请设置 NNDET_LUNA16_WEIGHT_DIR 环境变量。"
                if not nndet_ready else ""
            ),
        },
    ]


def _build_catalog() -> List[EngineMeta]:
    ts_ok = _totalsegmentator_available()
    gpu_ok = _gpu_available()
    monai_ok = is_monai_available()
    scheme_b_sub = _build_scheme_b_sub_engines()

    return [
        EngineMeta(
            id="scheme-a",
            label="肺区智能筛查",
            description="肺区分割 + 形态学筛查，支持全序列与当前层",
            available=ts_ok,
            supported_modes=["series", "single"],
            install_hint="pip install -r requirements-totalsegmentator.txt" if not ts_ok else "",
        ),
        EngineMeta(
            id="scheme-b",
            label="融合精准分析",
            description="肺叶/血管 + 深度学习检测器 + GGO，仅全序列，需 GPU",
            available=ts_ok and gpu_ok,
            supported_modes=["series"],
            requires_gpu=True,
            sub_engines=scheme_b_sub,
            unavailable_reason=(
                "GPU 不可用" if ts_ok and not gpu_ok
                else "TotalSegmentator 未安装" if not ts_ok
                else ""
            ),
            install_hint="pip install -r requirements-totalsegmentator.txt" if not ts_ok else "",
        ),
        EngineMeta(
            id="scheme-c",
            label="单层异常倾向",
            description="分类模型 + Grad-CAM 热力图，仅当前层（参考性筛查）",
            available=_torch_available(),
            supported_modes=["single"],
            unavailable_reason="PyTorch 未安装，请执行 pip install torch torchvision" if not _torch_available() else "",
            install_hint="pip install torch torchvision" if not _torch_available() else "",
        ),
    ]


def refresh_engine_catalog(force: bool = False) -> List[Dict[str, Any]]:
    """构建并缓存引擎目录，避免 /engines 每次触发重型依赖探测。"""
    global _CATALOG_CACHE, _CATALOG_TS
    with _CATALOG_LOCK:
        now = time.time()
        if not force and _CATALOG_CACHE is not None and (now - _CATALOG_TS) < _CATALOG_TTL_SEC:
            return list(_CATALOG_CACHE)
        _CATALOG_CACHE = [e.to_dict() for e in _build_catalog()]
        _CATALOG_TS = now
        return list(_CATALOG_CACHE)


def get_engine_catalog() -> List[Dict[str, Any]]:
    return refresh_engine_catalog()


def normalize_engine(engine_id: str | None) -> str:
    value = (engine_id or "scheme-a").strip().lower()
    if value in ("scheme-a", "scheme-b", "scheme-c"):
        return value
    return "scheme-a"


def assert_engine_available(engine_id: str) -> None:
    if engine_id == "monai-retinanet" and not is_monai_available():
        raise RuntimeError(
            "MONAI 未安装。请在 ai-service 目录执行: "
            "pip install -r requirements-monai.txt"
        )
    if engine_id in ("totalsegmentator", "scheme-a", "scheme-b") and not _totalsegmentator_available():
        raise RuntimeError(
            "TotalSegmentator 未安装。请在 ai-service 目录执行: "
            "pip install -r requirements-totalsegmentator.txt"
        )
    if engine_id == "scheme-c" and not _torch_available():
        raise RuntimeError(
            "方案 C 需要 PyTorch。请安装: pip install torch torchvision"
        )
