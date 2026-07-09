# GGO 深度学习分割模型目录

将 ONNX 或 TorchScript 权重放在此目录，并设置：

```bash
export GGO_MODEL_DIR=/path/to/ai-service/models/ggo
export SCHEME_B_GGO_BACKEND=model
```

## 文件结构

```
ggo/
  model.onnx          # 推荐：2D 单层 GGO 概率图
  model.pt            # 或 TorchScript
  config.json         # 推理参数（见下方示例）
  README.md
```

## config.json 示例

```json
{
  "input_size": [512, 512],
  "hu_min": -1024,
  "hu_max": 400,
  "threshold": 0.45,
  "input_name": "input",
  "output_name": "output"
}
```

## 输入输出约定

- 输入：单通道 HU 归一化到 [0,1]，shape `(1, 1, H, W)`
- 输出：GGO 概率图，shape `(1, 1, H, W)` 或与 input 同尺寸
- 推理在肺野 mask 内逐层（或降采样层）滑窗，与启发式结果经 IoU 合并

未放置权重时，`model` 后端自动回退 `adaptive` 局部 HU 分割。
