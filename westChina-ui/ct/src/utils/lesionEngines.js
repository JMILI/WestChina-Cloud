import { listDetectEngines } from '@/api/ct/ai'

export const ENGINE_STORAGE_KEY = 'ct_lesion_detect_engine'
export const SUB_ENGINE_STORAGE_KEY = 'ct_lesion_sub_engine'

/** 前端暂不开放选择的引擎（仍可查看历史识别结果） */
export const HIDDEN_LESION_ENGINE_IDS = ['scheme-a']

/** 屏蔽方案 A 后的默认引擎 */
export const DEFAULT_ACTIVE_LESION_ENGINE = 'scheme-b'

export const DEFAULT_LESION_ENGINES = [
  {
    id: 'scheme-a',
    label: '肺区智能筛查',
    description: '肺区分割 + 形态学筛查，支持全序列与当前层',
    available: false,
    supportedModes: ['series', 'single'],
    installHint: 'pip install -r requirements-totalsegmentator.txt',
    hidden: true
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

export function isHiddenLesionEngine(engineId) {
  return HIDDEN_LESION_ENGINE_IDS.includes(engineId)
}

/** 过滤掉前端屏蔽的引擎选项 */
export function filterVisibleEngines(list) {
  if (!list || !list.length) return []
  return list.filter((item) => !isHiddenLesionEngine(item.id))
}

export function pickDefaultEngine(catalog) {
  const visible = filterVisibleEngines(
    catalog && catalog.length ? catalog : DEFAULT_LESION_ENGINES
  )
  const preferred = visible.find((o) => o.id === DEFAULT_ACTIVE_LESION_ENGINE && o.available)
  if (preferred) return preferred.id
  const anyAvailable = visible.find((o) => o.available)
  if (anyAvailable) return anyAvailable.id
  return visible.length ? visible[0].id : DEFAULT_ACTIVE_LESION_ENGINE
}

export function normalizeActiveEngine(engineId, catalog) {
  if (!engineId || isHiddenLesionEngine(engineId)) {
    return pickDefaultEngine(catalog)
  }
  const visible = filterVisibleEngines(
    catalog && catalog.length ? catalog : DEFAULT_LESION_ENGINES
  )
  const opt = visible.find((o) => o.id === engineId)
  if (!opt) return pickDefaultEngine(catalog)
  if (!opt.available) return pickDefaultEngine(catalog)
  return engineId
}

export function readStoredEngine() {
  try {
    const v = localStorage.getItem(ENGINE_STORAGE_KEY)
    if (v === 'monai-nnunet' || v === 'heuristic' || v === 'totalsegmentator') {
      writeStoredEngine(DEFAULT_ACTIVE_LESION_ENGINE)
      return DEFAULT_ACTIVE_LESION_ENGINE
    }
    if (v && isHiddenLesionEngine(v)) {
      writeStoredEngine(DEFAULT_ACTIVE_LESION_ENGINE)
      return DEFAULT_ACTIVE_LESION_ENGINE
    }
    const visibleIds = filterVisibleEngines(DEFAULT_LESION_ENGINES).map((e) => e.id)
    if (v && visibleIds.includes(v)) return v
    return DEFAULT_ACTIVE_LESION_ENGINE
  } catch (e) {
    return DEFAULT_ACTIVE_LESION_ENGINE
  }
}

export function writeStoredEngine(engineId) {
  try {
    const id = engineId && !isHiddenLesionEngine(engineId)
      ? engineId
      : DEFAULT_ACTIVE_LESION_ENGINE
    localStorage.setItem(ENGINE_STORAGE_KEY, id)
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
  return filterVisibleEngines(list.map((item) => ({
    id: item.id,
    label: item.label,
    description: item.description,
    available: !!item.available,
    supportedModes: item.supportedModes || ['series', 'single'],
    unavailableReason: item.unavailableReason || '',
    installHint: item.installHint,
    requiresGpu: !!item.requiresGpu,
    subEngines: item.subEngines || null
  })))
}

export function fetchLesionEngines() {
  return listDetectEngines()
    .then((res) => normalizeEngineList(res) || filterVisibleEngines([...DEFAULT_LESION_ENGINES]))
    .catch(() => filterVisibleEngines([...DEFAULT_LESION_ENGINES]))
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
