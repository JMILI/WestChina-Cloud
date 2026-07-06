/**
 * DICOM 像素 / HU / 窗宽窗位 通俗说明
 * 与 ai-service/app/dicom_volume.py 中 HU 换算逻辑一致
 */

/** 资料勘误与补充（相对网络科普文） */
export const DICOM_PIXEL_ACCURACY_NOTES = [
  'DICOM 文件 = 文件元信息(0002组) + 数据集标签 + 像素数据；不只有「文件头」，患者/检查等标签在数据集中。',
  '像素里存的是「原始整数」，不是屏幕灰度；CT 常用 Rescale Slope/Intercept 换成 HU（亨氏单位）。',
  'HU 公式：HU = 存储值 × Slope + Intercept；胸部 CT 常见 Slope=1、Intercept=-1024，即 HU ≈ 存储值 - 1024。',
  '窗宽/窗位只影响「人眼在显示器上怎么看」，AI 识别通常直接读 HU 矩阵，不依赖当前窗设置。',
  '判断病灶不能只看一个点的 HU：还要看位置（是否在肺内）、形状、周围纹理等——这是 3D 模式识别，不是查表。'
]

/** 常见组织 HU 参考（教学用，个体差异存在） */
export const HU_REFERENCE_BANDS = [
  { label: '空气', hu: -1000, color: '#1a1a2e', note: '肺外气体' },
  { label: '肺实质', hu: -750, color: '#3d5a80', note: '约 -950 ~ -500' },
  { label: '脂肪', hu: -80, color: '#6b5b4f', note: '约 -120 ~ -60' },
  { label: '水/液体', hu: 0, color: '#4a90a4', note: '校准基准' },
  { label: '软组织', hu: 40, color: '#8b7355', note: '肌肉、纵隔等' },
  { label: '钙化', hu: 200, color: '#c9b896', note: '> 100 常提示钙化' },
  { label: '骨骼', hu: 700, color: '#e8e0d0', note: '> 300 骨质' }
]

/** 常用 CT 显示窗（教学） */
export const WINDOW_PRESETS = [
  {
    id: 'lung',
    name: '肺窗',
    level: -600,
    width: 1500,
    desc: '看肺纹理、小结节；肺组织从黑背景中「拉出来」'
  },
  {
    id: 'mediastinum',
    name: '纵隔窗',
    level: 40,
    width: 400,
    desc: '看心脏、大血管、纵隔软组织'
  },
  {
    id: 'bone',
    name: '骨窗',
    level: 300,
    width: 1500,
    desc: '看肋骨、椎体等骨性结构'
  }
]

export const DICOM_PIXEL_FLOW_STEPS = [
  {
    title: '① DICOM 文件里有什么？',
    text: '可以想成「说明书 + 照片」。说明书是各种标签（患者、检查、层厚、Slope/Intercept）；照片是像素矩阵（每个格子一个整数）。'
  },
  {
    title: '② 整数怎么变成 HU？',
    text: 'CT 用 HU 表示组织密度：空气约 -1000，水 = 0，骨可达 +1000。换算靠 Rescale Slope 和 Intercept 两个参数（在 DICOM 标签里）。'
  },
  {
    title: '③ 医生在屏幕上看到什么？',
    text: '显示器只显示 0~255 灰度。窗位 = 中间灰对应多少 HU；窗宽 = 一共显示多宽的 HU 范围。调窗 = 换「观察滤镜」，不改变文件里的真实 HU。'
  },
  {
    title: '④ AI 识别用什么？',
    text: '本系统 AI 先还原 HU 体数据，再按算法分析（启发式阈值、肺分割、深度学习检测等）。输出病灶框/轮廓叠回到当前图像上供医生参考。'
  }
]
