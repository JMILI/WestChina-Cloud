# CT AI 推理服务

> Python FastAPI 服务，默认端口 **9810**。为阅片前端提供胸部 CT 病灶识别（方案 A/B/C）与 SSE 进度推送。

---

## 1. 在整体架构中的位置

```
阅片前端 (ct, :5000)
    │  POST /ct/ai/detectLesionStream
    ▼
CT 模块 (westChina-ct, :9800)     ← Java 代理，配置 ct.ai.base-url
    │  POST http://127.0.0.1:9810/detectLesion/stream
    ▼
AI Service (本服务, :9810)
    │  从 MinIO 读取 DICOM
    ▼
识别结果 → 返回 JSON/SSE → 前端叠加 contour / 热力图
    │  可选落库
    ▼
租户子库 dicom_ai_lesion（westsql/slave-init.sql）
```

**说明：** AI 服务地址在 Nacos / `CtAiProperties` 中配置（`ct.ai.base-url`），不写入数据库。

---

## 2. 三种识别方案

| 方案 ID | 名称 | 模式 | GPU | 依赖 | 输出 |
|---------|------|------|:---:|------|------|
| `scheme-a` | 肺区智能筛查 | 全序列 / 当前层 | 否* | TotalSegmentator | 病灶轮廓 + 置信度 + HU |
| `scheme-b` | 融合精准分析 | 仅全序列 | **是** | TotalSegmentator + MONAI RetinaNet | 轮廓 + GGO 区域 |
| `scheme-c` | 单层异常倾向 | 仅当前层 | 否* | PyTorch + torchvision | 原图分辨率 HU 异常热力图 |

\* CPU 可运行；方案 B 强制要求 CUDA。

### 方案 A — 肺区分割 + 形态学 + HU 分类

1. `robust_ct_loader` 从 MinIO 加载序列，按 IPP 排序，并记录 **文件序号映射**（`file_slice_indices`）。
2. TotalSegmentator / 2D 回退做肺野 mask。
3. `hu_utils.nodule_candidate_mask` 在肺野内筛选 GGO / 实性 / 高密度候选。
4. 3D 连通域过滤（体积、实心度、跨层连续性、肺门抑制）。
5. `classify_nodule_hu` 按临床 HU 范围分类，输出 `contour`（归一化坐标）与 `sliceIndex`（**已映射为前端 stack 序号**）。

关键文件：`scheme_a_detector.py`、`hu_utils.py`、`lung_segment_2d.py`。

### 方案 B — 深度学习检测 + 融合过滤

1. 同样加载体数据与肺 mask。
2. 子引擎（`detectSubEngine`）：
   - `auto`：nnDetection 权重就绪时优先，否则 MONAI RetinaNet
   - `monai`：强制 MONAI LUNA16 bundle
   - `nndet`：强制 nnDetection（需 `NNDET_LUNA16_WEIGHT_DIR`）
3. MONAI 检测框 → ROI 内按 HU mask 提取 **真实轮廓**（非矩形框）。
4. 与肺野重叠、血管形态等规则融合过滤。
5. `slice_index_map` 将层索引转为前端文件序号。

关键文件：`scheme_b_fusion.py`、`monai_nnunet_detector.py`、`nndet_wrapper.py`。

### 方案 C — 单层 HU 异常热力图

1. 仅处理当前层 HU 数组（`pixel_array × RescaleSlope + RescaleIntercept`）。
2. 体内 mask 排除空气 / 皮肤边缘。
3. 肺实质内 GGO/实性偏离 + 高密度灶（约 +80～+280 HU）生成热力图。
4. **不以 Grad-CAM 边缘为主**（避免皮肤/背景假阳性）。
5. 返回 `heatmap.values`（与原图同宽高的一维数组）。

关键文件：`scheme_c_screening.py`、`hu_utils.py`。

---

## 3. HTTP API

### `GET /health`

```json
{
  "status": "ok",
  "gpuAvailable": true,
  "engines": [ { "id": "scheme-a", "available": true, ... } ]
}
```

### `GET /engines`

返回引擎目录（与 `/health` 中 `engines` 相同）。

### `POST /detectLesion`

同步识别（少用，CT 模块主要用 stream）。

### `POST /detectLesion/stream`

SSE 事件流。请求体示例：

```json
{
  "bucket": "tenant-bucket",
  "studyUid": "1.2.3...",
  "seriesUid": "1.2.4...",
  "dicomCtPath": "path/to/series/",
  "imageCount": 48,
  "bodyPart": "CHEST",
  "detectEngine": "scheme-a",
  "detectMode": "series",
  "detectSubEngine": "auto",
  "currentSliceIndex": 12,
  "sliceIndex": 12
}
```

| 字段 | 说明 |
|------|------|
| `detectEngine` | `scheme-a` / `scheme-b` / `scheme-c` |
| `detectMode` | `series` 全序列 / `single` 当前层 |
| `detectSubEngine` | 仅方案 B：`auto` / `monai` / `nndet` |
| `sliceIndex` | 当前层在 **前端 stack** 中的 0-based 序号 |

SSE 事件类型：`progress`、`log`、`stats`、`result`、`error`。

---

## 4. 环境变量

| 变量 | 默认 | 说明 |
|------|------|------|
| `AI_HOST` | `0.0.0.0` | 监听地址 |
| `AI_PORT` | `9810` | 端口 |
| `MINIO_ENDPOINT` | `127.0.0.1:9000` | MinIO 地址 |
| `MINIO_ACCESS_KEY` | `admin` | MinIO 密钥 |
| `MINIO_SECRET_KEY` | `admin123456` | MinIO 密钥 |
| `SERIES_MAX_SLICES_CPU` | `128` | CPU 全序列最大层数（超出则降采样） |
| `AI_LOG_JSON` | `true` | 结构化 JSON 日志 |
| `AI_LOG_PATH` | `../deploymentServer/logs/ai-service.log` | 日志路径 |
| `NNDET_LUNA16_WEIGHT_DIR` | - | nnDetection 权重目录 |
| `AI_LOG_LEVEL` | `INFO` | 日志级别 |

结节筛选相关见 `app/config.py`（`MIN_NODULE_MM`、`GGO_HU_MIN` 等）。

---

## 5. 安装与启动

### 5.1 基础依赖（必需）

```bash
cd ai-service
python3 -m venv .venv    # 或使用 .conda
source .venv/bin/activate
pip install -r requirements.txt
```

### 5.2 AI 引擎（按需）

```bash
# 方案 A/B：TotalSegmentator
pip install -r requirements-totalsegmentator.txt

# 方案 B：MONAI RetinaNet bundle
pip install -r requirements-monai.txt

# 方案 C：PyTorch（CPU）
pip install torch torchvision

# GPU 版 PyTorch（方案 B 推荐）
bash ../scripts/install-pytorch-gpu.sh
```

或使用项目脚本：

```bash
bash scripts/setup_env.sh ai-engines   # CPU 引擎
bash scripts/setup_env.sh gpu          # GPU PyTorch
```

### 5.3 启动

```bash
# 推荐：项目根目录
bash scripts/start-ai.sh

# 或手动
cd ai-service && .conda/bin/python run.py
```

验证：

```bash
curl http://127.0.0.1:9810/health
curl http://127.0.0.1:9810/engines
```

---

## 6. 目录结构

```
ai-service/
├── README.md                 # 本文档
├── run.py                    # uvicorn 入口
├── requirements.txt          # 基础依赖
├── requirements-monai.txt
├── requirements-totalsegmentator.txt
├── app/
│   ├── main.py               # FastAPI 路由
│   ├── detection_runner.py   # 识别流水线 + SSE
│   ├── engines.py            # 引擎注册与可用性
│   ├── schemas.py            # 请求/响应模型
│   ├── config.py             # 环境变量与阈值
│   ├── robust_ct_loader.py   # MinIO DICOM 加载 + 层序映射
│   ├── hu_utils.py           # HU 转换与候选 mask
│   ├── slice_index_map.py    # AI 层号 → 前端 stack 序号
│   ├── scheme_a_detector.py
│   ├── scheme_b_fusion.py
│   ├── scheme_c_screening.py
│   ├── monai_nnunet_detector.py
│   └── nndet_wrapper.py
└── models/                   # MONAI bundle 等权重
```

---

## 7. HU 与坐标约定

### HU 换算

```
HU = pixel_value × RescaleSlope + RescaleIntercept
```

每张 DICOM 单独读取 `(0028,1053)` / `(0028,1052)`，与阅片探针一致。

### 病灶分类参考（`classify_nodule_hu`）

| HU 范围 | 类型 |
|---------|------|
| -850 ~ -280 | 磨玻璃 |
| 12 ~ 90 | 实性结节 |
| 80 ~ 280 | 高密度（钙化/增强） |

### 前端标记

- `bbox` / `contour` 坐标为 **相对图像宽高归一化** [0, 1]。
- `sliceIndex` 为 **MinIO 文件顺序**（0-based），与 Cornerstone stack 的 `currentImageIdIndex` 一致。
- 有 `contour` 时前端只绘制轮廓，不绘制虚线矩形。

---

## 8. 常见问题

### `/engines` 中 scheme-a/b `available: false`

```bash
pip install -r requirements-totalsegmentator.txt
```

### scheme-b 提示 GPU 不可用

```bash
nvidia-smi
bash scripts/install-pytorch-gpu.sh
```

### 标记位置与探针 HU 对不上

1. 确认 AI 服务已更新（含 `slice_index_map`）。
2. 前端硬刷新（Ctrl+Shift+R）。
3. 对比同一 `sliceIndex` 层，而非 IPP 排序后的内部层号。

### 方案 C 热力图在体外高亮

确认已部署最新 `scheme_c_screening.py`（体内 HU 异常 mask，非 Grad-CAM 边缘）。

### 识别结果无法保存到序列

租户子库需有 `dicom_ai_lesion` 表：

```bash
bash scripts/init-tenant-db.sh <数据库名> docker
```

表结构见 `westsql/slave-init.sql`。

---

## 9. 相关文档

- [部署与开发指南](../docs/DEPLOY.md)
- [从零部署](../docs/09-from-scratch.md)
- [SQL 与租户子库](../westsql/readme.txt)
