import { listDetectEngines } from '@/api/ct/ai'

export const ENGINE_STORAGE_KEY = 'ct_lesion_detect_engine'
export const SUB_ENGINE_STORAGE_KEY = 'ct_lesion_sub_engine'

export const DEFAULT_LESION_ENGINES = [
  {
    id: 'scheme-a',
    label: '肺区智能筛查',
    description: '肺区分割 + 形态学筛查，支持全序列与当前层',
    available: false,
    supportedModes: ['series', 'single'],
    installHint: 'pip install -r requirements-totalsegmentator.txt'
  },
  {
    id: 'scheme-b',
    label: '融合精准分析',
    description: '肺叶/血管 + 深度学习检测器 + GGO，仅全序列，需 GPU',
    available: false,
    supportedModes: ['series'],
    requiresGpu: true,
    unavailableReason: 'GPU 不可用',
    subEngines: [
      { id: 'auto', label: '自动', description: '自动选择最优检测器', available: true },
      { id: 'monai', label: 'MONAI RetinaNet', description: 'MONAI LUNA16 bundle', available: false },
      { id: 'nndet', label: 'nnDetection (LUNA16)', description: '需下载权重', available: false, unavailableReason: '权重未就绪' }
    ]
  },
  {
    id: 'scheme-c',
    label: '单层异常倾向',
    description: '分类模型 + Grad-CAM 热力图，仅当前层（参考性筛查）',
    available: false,
    supportedModes: ['single'],
    unavailableReason: 'PyTorch 未安装'
  }
]

export function readStoredEngine() {
  try {
    const v = localStorage.getItem(ENGINE_STORAGE_KEY)
    if (v === 'monai-nnunet' || v === 'heuristic' || v === 'totalsegmentator') {
      writeStoredEngine('scheme-a')
      return 'scheme-a'
    }
    const known = DEFAULT_LESION_ENGINES.map(e => e.id)
    if (v && known.includes(v)) return v
    return 'scheme-a'
  } catch (e) {
    return 'scheme-a'
  }
}

export function writeStoredEngine(engineId) {
  try {
    localStorage.setItem(ENGINE_STORAGE_KEY, engineId || 'scheme-a')
  } catch (e) {
    // ignore
  }
}

export function readStoredSubEngine() {
  try {
    const v = localStorage.getItem(SUB_ENGINE_STORAGE_KEY)
    if (v && ['auto', 'monai', 'nndet'].includes(v)) return v
    return 'auto'
  } catch (e) {
    return 'auto'
  }
}

export function writeStoredSubEngine(subEngineId) {
  try {
    localStorage.setItem(SUB_ENGINE_STORAGE_KEY, subEngineId || 'auto')
  } catch (e) {
    // ignore
  }
}

export function normalizeEngineList(res) {
  let list = null
  if (res && Array.isArray(res.data)) {
    list = res.data
  } else if (Array.isArray(res)) {
    list = res
  }
  if (!list || !list.length) return null
  return list.map((item) => ({
    id: item.id,
    label: item.label,
    description: item.description,
    available: !!item.available,
    supportedModes: item.supportedModes || ['series', 'single'],
    unavailableReason: item.unavailableReason || '',
    installHint: item.installHint,
    requiresGpu: !!item.requiresGpu,
    subEngines: item.subEngines || null
  }))
}

export function fetchLesionEngines() {
  return listDetectEngines()
    .then((res) => normalizeEngineList(res) || [...DEFAULT_LESION_ENGINES])
    .catch(() => [...DEFAULT_LESION_ENGINES])
}

export function getEngineLabel(engineId, catalog) {
  const list = catalog && catalog.length ? catalog : DEFAULT_LESION_ENGINES
  const opt = list.find((o) => o.id === engineId)
  return opt ? opt.label : engineId
}

export function getEngineDescription(engineId, catalog) {
  const list = catalog && catalog.length ? catalog : DEFAULT_LESION_ENGINES
  const opt = list.find((o) => o.id === engineId)
  if (!opt) return ''
  if (!opt.available) {
    if (opt.unavailableReason) return opt.unavailableReason
    if (opt.installHint) return `${opt.description || ''}。安装：${opt.installHint}`
  }
  return opt.description || ''
}

/**
 * 检查引擎是否支持指定检测模式。
 */
export function engineSupportsMode(engineId, mode, catalog) {
  const list = catalog && catalog.length ? catalog : DEFAULT_LESION_ENGINES
  const opt = list.find((o) => o.id === engineId)
  if (!opt) return false
  const modes = opt.supportedModes || ['series', 'single']
  return modes.includes(mode)
}

/**
 * 获取引擎的子引擎列表。
 */
export function getSubEngines(engineId, catalog) {
  const list = catalog && catalog.length ? catalog : DEFAULT_LESION_ENGINES
  const opt = list.find((o) => o.id === engineId)
  if (!opt || !opt.subEngines || !opt.subEngines.length) return null
  return opt.subEngines
}
