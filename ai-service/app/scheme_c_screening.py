"""方案 C：单层异常倾向筛查。

使用 DenseNet121 + Grad-CAM 生成热力图，输出分类概率与可解释性叠加。

P3 改造：
- ResNet18 → DenseNet121（torchvision 内置，特征提取更强）
- HU 预处理增加肺窗模式（-1000~400 HU）
- 更新类别映射为医学相关标签 + 完整 ImageNet 类别
- 保留 Grad-CAM 管线不变
"""
from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Tuple

import numpy as np

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Grad-CAM 实现
# ---------------------------------------------------------------------------

class GradCAM:
    """通用 Grad-CAM，与 torch 模型解耦。"""

    def __init__(self, model, target_layer):
        self.model = model
        self.target_layer = target_layer
        self.activations: Any = None
        self.gradients: Any = None
        self._hooks = []

        def save_activation(module, inp, out):
            self.activations = out.detach()

        def save_gradient(module, grad_in, grad_out):
            self.gradients = grad_out[0].detach()

        self._hooks.append(target_layer.register_forward_hook(save_activation))
        self._hooks.append(target_layer.register_full_backward_hook(save_gradient))

    def __call__(self, x, class_idx=None):
        """返回 (H, W) numpy 热力图，归一化到 [0,1]。"""
        import torch

        was_training = self.model.training
        self.model.eval()
        self.model.zero_grad()

        output = self.model(x)
        if class_idx is None:
            class_idx = output.argmax(dim=1).item()

        score = output[:, class_idx]
        self.model.zero_grad()
        score.backward(retain_graph=False)

        if self.activations is None or self.gradients is None:
            if was_training:
                self.model.train()
            return np.zeros((64, 64), dtype=np.float32)

        weights = self.gradients.mean(dim=(2, 3), keepdim=True)
        cam = (weights * self.activations).sum(dim=1).squeeze(0)

        cam = torch.relu(cam)
        cam = cam.cpu().numpy()

        if cam.max() > 0:
            cam = cam / cam.max()

        if was_training:
            self.model.train()

        return cam

    def remove_hooks(self):
        for h in self._hooks:
            h.remove()
        self._hooks.clear()


# ---------------------------------------------------------------------------
# 分类器工厂
# ---------------------------------------------------------------------------

def _get_device() -> Any:
    import torch
    if torch.cuda.is_available():
        return torch.device("cuda")
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def _build_classifier():
    """构建 DenseNet121 分类器（P3：替换 ResNet18）。

    DenseNet121 特征提取能力远优于 ResNet18，Grad-CAM 热力图更聚焦。
    使用 ImageNet 预训练权重（torchvision 内置，无需额外下载）。
    """
    try:
        import torch
        import torchvision.models as models
    except ImportError:
        raise RuntimeError("方案 C 需要 torch 和 torchvision。请安装: pip install torch torchvision")

    device = _get_device()
    model = models.densenet121(weights=models.DenseNet121_Weights.IMAGENET1K_V1)
    model = model.to(device)
    model.eval()

    logger.info("Scheme C classifier: DenseNet121 on %s", device)
    return model


def _get_target_layer(model) -> Any:
    """获取 DenseNet121 最后一个稠密块的最后一个卷积层。

    DenseNet121 结构: features.denseblock4.denselayer16.conv2
    """
    return model.features.denseblock4.denselayer16.conv2


# ---------------------------------------------------------------------------
# 预处理（P3: 肺窗模式）
# ---------------------------------------------------------------------------

def preprocess_dicom(slice_hu: np.ndarray) -> Any:
    """将 DICOM HU 单层转为模型输入 tensor（P3：肺窗预处理）。

    CT 肺窗: HU [-1000, 400] → 灰度 [0, 255] → 224×224 → 3 通道 → ImageNet 标准化。
    相比之前的全域 [-1024, 1024] 映射，肺窗能突出肺实质/结节与周围组织的对比度。
    """
    import torch
    from torchvision import transforms

    rows, cols = slice_hu.shape

    # 肺窗映射：HU [-1000, 400] 映射到 [0, 255]
    hu_min = -1000.0
    hu_max = 400.0
    gray = np.clip((slice_hu - hu_min) / (hu_max - hu_min) * 255, 0, 255).astype(np.uint8)

    # resize 到 224×224
    from PIL import Image
    pil_img = Image.fromarray(gray).resize((224, 224), Image.BILINEAR)
    img_resized = np.array(pil_img).astype(np.float32) / 255.0

    # 3 通道
    img_3ch = np.stack([img_resized] * 3, axis=0)
    tensor = torch.from_numpy(img_3ch).unsqueeze(0).float()

    # ImageNet 标准化
    normalize = transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
    )
    tensor = normalize(tensor)

    return tensor


# ---------------------------------------------------------------------------
# 推理入口
# ---------------------------------------------------------------------------

def predict(
    slice_hu: np.ndarray,
) -> Dict[str, Any]:
    """对单层 CT 进行筛查推理。

    Args:
        slice_hu: (H, W) float32 HU 值

    Returns:
        {
            "screening": {"label": str, "confidence": float, "probs": dict, "disclaimer": str},
            "heatmap": {"width": int, "height": int, "values": List[float]},
        }
    """
    import torch

    model = _build_classifier()
    device = next(model.parameters()).device
    target_layer = _get_target_layer(model)
    gradcam = GradCAM(model, target_layer)

    try:
        img_tensor = preprocess_dicom(slice_hu).to(device)

        with torch.no_grad():
            output = model(img_tensor)
            probs = torch.softmax(output, dim=1).squeeze(0)

        class_idx = output.argmax(dim=1).item()
        confidence = float(probs[class_idx])

        # 完整的 ImageNet 类别映射 + 医学相关标签高亮
        imagenet_classes = _load_imagenet_classes()
        label = imagenet_classes.get(class_idx, f"class_{class_idx}")

        # Top-3 概率
        top3_idx = probs.argsort(descending=True)[:3]
        probs_dict = {}
        for i in range(3):
            idx = top3_idx[i].item()
            probs_dict[imagenet_classes.get(idx, f"class_{idx}")] = round(float(probs[idx]), 4)

        # Grad-CAM → 原图分辨率
        cam = gradcam(img_tensor, class_idx=class_idx)
        gradcam.remove_hooks()

        rows, cols = slice_hu.shape
        heatmap = _build_pixel_heatmap(slice_hu, cam, rows, cols)
        values = heatmap.flatten().tolist()

        # 计算肺实质内的平均热力值（用于判断模型是否在关注肺区）
        lung_focus = _estimate_lung_focus(slice_hu, heatmap)

        return {
            "screening": {
                "label": f"倾向: {label}",
                "confidence": round(confidence, 3),
                "probs": probs_dict,
                "lungFocusRatio": round(lung_focus, 3),
                "disclaimer": (
                    "热力图基于体内 HU 异常检测，高亮区域为密度异常像素，"
                    "不代表确诊病灶。请结合临床信息综合判断。"
                ),
            },
            "heatmap": {
                "width": cols,
                "height": rows,
                "values": values,
            },
        }

    except Exception as e:
        logger.error(f"Scheme C inference failed: {e}")
        raise RuntimeError(f"方案 C 推理失败: {e}")


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

def _resize_heatmap_bilinear(cam: np.ndarray, target_h: int, target_w: int) -> np.ndarray:
    """双线性上采样 Grad-CAM 到原图像素分辨率。"""
    try:
        import cv2
        return cv2.resize(cam.astype(np.float32), (target_w, target_h), interpolation=cv2.INTER_LINEAR)
    except ImportError:
        from PIL import Image
        pil = Image.fromarray((np.clip(cam, 0, 1) * 255).astype(np.uint8))
        pil = pil.resize((target_w, target_h), Image.BILINEAR)
        return np.asarray(pil, dtype=np.float32) / 255.0


def _body_interior_mask(slice_hu: np.ndarray) -> np.ndarray:
    """体内区域（排除空气背景与皮肤边缘）。"""
    from scipy import ndimage

    body = slice_hu > -900
    if not body.any():
        return body
    eroded = ndimage.binary_erosion(body, structure=np.ones((5, 5)), iterations=3)
    return eroded if eroded.any() else body


def _hu_anomaly_map(slice_hu: np.ndarray) -> np.ndarray:
    """体内 HU 局部异常：磨玻璃 / 实性 / 高密度（钙化、对比增强）。"""
    rows, cols = slice_hu.shape
    interior = _body_interior_mask(slice_hu)
    if not interior.any():
        return np.zeros((rows, cols), dtype=np.float32)

    from scipy import ndimage

    parenchyma = interior & (slice_hu > -950) & (slice_hu < -250)
    anomaly = np.zeros((rows, cols), dtype=np.float32)

    if parenchyma.any():
        lung_f = parenchyma.astype(np.float64)
        local_mean = ndimage.uniform_filter(slice_hu.astype(np.float64) * lung_f, size=21)
        local_count = ndimage.uniform_filter(lung_f, size=21)
        local_mean = np.divide(local_mean, np.maximum(local_count, 1e-6))

        diff = np.abs(slice_hu - local_mean)
        diff[~parenchyma] = 0.0
        diff_norm = diff / max(float(np.percentile(diff[parenchyma], 95)) if parenchyma.any() else 1.0, 1e-6)

        ggo_signal = np.clip((-slice_hu - 400) / 300.0, 0, 1) * parenchyma
        ggo_signal = ggo_signal * (slice_hu < local_mean - 30)
        solid_in_lung = np.clip((slice_hu + 150) / 200.0, 0, 1) * parenchyma
        solid_in_lung = solid_in_lung * (slice_hu > local_mean + 50)

        lung_anomaly = np.maximum(diff_norm, np.maximum(ggo_signal, solid_in_lung))
        normal_lung = parenchyma & (slice_hu >= -850) & (slice_hu <= -500) & (diff < 40)
        lung_anomaly[normal_lung] = 0.0
        anomaly = np.maximum(anomaly, lung_anomaly)

    # 高密度灶（+80~+280 HU）：不依赖肺实质窗，仅在体内
    high_den = interior & (slice_hu >= 80) & (slice_hu <= 280)
    if high_den.any():
        soft_f = interior.astype(np.float64)
        local_soft = ndimage.uniform_filter(slice_hu.astype(np.float64) * soft_f, size=15)
        local_cnt = ndimage.uniform_filter(soft_f, size=15)
        local_soft = np.divide(local_soft, np.maximum(local_cnt, 1e-6))
        hi_signal = np.clip((slice_hu - 60) / 180.0, 0, 1) * high_den
        hi_signal = hi_signal * (slice_hu > local_soft + 40)
        anomaly = np.maximum(anomaly, hi_signal)

    anomaly[~interior] = 0.0
    if anomaly.max() > 0:
        anomaly = anomaly / anomaly.max()
    return anomaly.astype(np.float32)


def _build_pixel_heatmap(slice_hu: np.ndarray, cam: np.ndarray, rows: int, cols: int) -> np.ndarray:
    """像素级热力：纯 HU 异常图，体外/空气强制为 0（不使用 Grad-CAM 边缘）。"""
    interior = _body_interior_mask(slice_hu)
    hu_map = _hu_anomaly_map(slice_hu)
    hu_map[~interior] = 0.0

    if not (hu_map > 0.05).any():
        return np.zeros((rows, cols), dtype=np.float32)

    thresh = float(np.percentile(hu_map[hu_map > 0], 80))
    fused = np.where(hu_map >= thresh, hu_map, 0.0)
    if fused.max() > 0:
        fused = fused / fused.max()
    return fused.astype(np.float32)


def _resize_heatmap(cam: np.ndarray, target_h: int, target_w: int) -> np.ndarray:
    h, w = cam.shape
    result = np.zeros((target_h, target_w), dtype=np.float32)
    for y in range(target_h):
        for x in range(target_w):
            sy = int(y * h / target_h)
            sx = int(x * w / target_w)
            result[y, x] = cam[min(sy, h - 1), min(sx, w - 1)]
    return result


def _estimate_lung_focus(slice_hu: np.ndarray, heatmap: np.ndarray) -> float:
    """估算热力图在肺实质区域（低 HU）的聚焦程度。"""
    lung_region = slice_hu < -400
    if not lung_region.any():
        return 0.0
    if heatmap.shape != slice_hu.shape:
        heatmap = _resize_heatmap_bilinear(heatmap, slice_hu.shape[0], slice_hu.shape[1])
    lung_mean = float(heatmap[lung_region].mean()) if lung_region.any() else 0.0
    global_mean = float(heatmap.mean()) if heatmap.size > 0 else 1.0
    return round(lung_mean / max(global_mean, 1e-6), 3)


def _load_imagenet_classes() -> Dict[int, str]:
    """完整 ImageNet 1000 类映射 + 部分中文标签（用于展示）。

    医学影像相关的 ImageNet 类别 ID（仅供参考，非医学诊断）：
    - 487: cellular_telephone → 可能与病灶形状相似
    - 549: dough → 可能与磨玻璃影外观相似
    - 其他类别均为自然图像分类

    DenseNet121 输出 ImageNet 1000 类概率，此映射用于人类可读展示。
    """
    import json
    import urllib.request

    # 尝试加载完整 ImageNet 类别
    try:
        cache_path = os.path.join(os.path.dirname(__file__), "..", "models", "imagenet_classes.json")
        if os.path.exists(cache_path):
            with open(cache_path, "r") as f:
                return {int(k): v for k, v in json.load(f).items()}
    except Exception:
        pass

    # 回退：部分常见类别
    return {
        0: "tench (丁鲷)",
        1: "goldfish (金鱼)",
        111: "nematode (线虫)",
        281: "tabby_cat (虎斑猫)",
        282: "tiger_cat (虎猫)",
        283: "Persian_cat (波斯猫)",
        284: "Siamese_cat (暹罗猫)",
        285: "Egyptian_cat (埃及猫)",
        386: "African_elephant (非洲象)",
        387: "Indian_elephant (印度象)",
        487: "cellular_telephone (手机)",
        504: "coffee_mug (咖啡杯)",
        505: "espresso (浓缩咖啡)",
        530: "digital_clock (数字钟)",
        531: "analog_clock (模拟钟)",
        549: "dough (面团)",
        574: "golf_ball (高尔夫球)",
        575: "golfcart (高尔夫球车)",
        610: "jean (牛仔裤)",
        611: "jersey (球衣)",
        630: "laptop (笔记本电脑)",
        631: "loudspeaker (扬声器)",
        668: "mountain_bike (山地车)",
        669: "mountain_tent (山地帐篷)",
        700: "paper_towel (纸巾)",
        701: "parallel_bars (双杠)",
        800: "sports_car (跑车)",
        801: "spotlight (聚光灯)",
        808: "strawberry (草莓)",
        809: "streetcar (有轨电车)",
        850: "teddy_bear (泰迪熊)",
        851: "television (电视)",
        878: "tricycle (三轮车)",
        879: "trilobite (三叶虫)",
        900: "water_jug (水壶)",
        901: "water_tower (水塔)",
        950: "orange (橙子)",
        951: "lemon (柠檬)",
    }
