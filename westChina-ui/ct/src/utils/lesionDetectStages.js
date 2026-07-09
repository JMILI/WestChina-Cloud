/** AI 识别进度：按阶段映射百分比，避免长期停在 0%。 */

export const STAGE_PIPELINES = {
  'scheme-b': [
    { id: 'prepare', label: '准备', keys: ['init', 'queued', 'connect', 'running'], weight: 4 },
    { id: 'download', label: '下载', keys: ['download'], weight: 20 },
    { id: 'volume', label: '体数据', keys: ['volume'], weight: 14 },
    { id: 'fusion', label: '融合', keys: ['segment', 'detect', 'infer'], weight: 57 },
    { id: 'enhanced', label: 'ΔHU', keys: ['enhanced'], weight: 5 },
    { id: 'done', label: '完成', keys: ['done'], weight: 0 }
  ],
  'scheme-c': [
    { id: 'prepare', label: '准备', keys: ['init', 'queued', 'connect', 'running'], weight: 5 },
    { id: 'download', label: '下载', keys: ['download'], weight: 22 },
    { id: 'infer', label: '模型推理', keys: ['volume', 'infer', 'detect'], weight: 68 },
    { id: 'done', label: '完成', keys: ['done'], weight: 0 }
  ],
  default: [
    { id: 'prepare', label: '准备', keys: ['init', 'queued', 'connect', 'running'], weight: 5 },
    { id: 'download', label: '下载', keys: ['download'], weight: 22 },
    { id: 'volume', label: '体数据', keys: ['volume'], weight: 14 },
    { id: 'segment', label: '肺分割', keys: ['segment'], weight: 14 },
    { id: 'detect', label: '病灶检测', keys: ['detect', 'infer'], weight: 40 },
    { id: 'done', label: '完成', keys: ['done'], weight: 0 }
  ]
}

export function getStagePipeline(engine) {
  const id = String(engine || '')
  if (id.startsWith('scheme-b')) return STAGE_PIPELINES['scheme-b']
  if (id.startsWith('scheme-c')) return STAGE_PIPELINES['scheme-c']
  return STAGE_PIPELINES.default
}

export function resolveStageIndex(pipeline, stage) {
  if (!stage) return -1
  for (let i = 0; i < pipeline.length; i++) {
    const item = pipeline[i]
    if (item.keys.includes(stage) || item.id === stage) return i
  }
  return -1
}

export function computeStageProgress(pipeline, stage, rawPercent = 0) {
  if (!pipeline || !pipeline.length) return Math.min(100, Math.max(0, rawPercent))

  if (stage === 'done') return 100
  if (stage === 'cancelled') return Math.min(100, Math.max(0, rawPercent))

  const totalWeight = pipeline.reduce((sum, item) => sum + item.weight, 0) || 100
  const idx = resolveStageIndex(pipeline, stage)

  if (idx < 0) {
    if (stage) return 3
    return Math.max(1, Math.min(99, Number(rawPercent) || 0))
  }

  let cumulative = 0
  for (let i = 0; i < idx; i++) cumulative += pipeline[i].weight

  const current = pipeline[idx]
  if (current.id === 'done') return 100

  const intra = Math.min(100, Math.max(0, Number(rawPercent) || 0)) / 100
  const weighted = cumulative + current.weight * intra
  return Math.min(99, Math.round((weighted / totalWeight) * 100))
}

export function getStageDetailText(stage, engine) {
  if (stage === 'download') return '从 MinIO 下载 DICOM 序列'
  if (stage === 'queued') return '任务已提交，等待执行'
  if (stage === 'connect' || stage === 'running') return '连接 AI 推理服务'
  if (stage === 'cancelled') return '任务已取消'
  if (stage === 'volume') return 'IPP 排序并构建 3D 体数据'
  if (stage === 'segment') return 'TotalSegmentator 肺野分割'
  if (stage === 'detect') {
    return String(engine || '').startsWith('scheme-b')
      ? '肺叶分割 + 深度学习检测 + P1 过滤与 enrich'
      : '形态学候选筛选与 HU 分类'
  }
  if (stage === 'enhanced') return '加载配对增强 CT，计算 ΔHU'
  if (stage === 'infer') return '单层 HU 异常建模与热力图'
  if (stage === 'done') return '识别完成'
  if (stage === 'init') return '初始化识别任务'
  return '准备中…'
}
