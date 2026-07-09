import * as cornerstone from 'cornerstone-core'
import * as cornerstoneTools from '@cornerstoneTools'
import * as dicomParser from 'dicom-parser'

const CHEST_KEYWORDS = ['CHEST', 'THORAX', 'THORACIC', 'LUNG', '胸部', '胸', '肺']

const overlayRegistry = new WeakMap()
const heatmapRegistry = new WeakMap()
const ggoRegistry = new WeakMap()
const bboxCanvasRegistry = new WeakMap()
let tooltipEl = null
let stylesInjected = false

/** cornerstone 启用的是 div 容器，真正绘图在内部 canvas 上 */
function getViewportInfo(element) {
  if (!element) return null
  try {
    const ee = cornerstone.getEnabledElement(element)
    if (!ee || !ee.canvas) return null
    return { host: element, drawCanvas: ee.canvas, image: ee.image }
  } catch (e) {
    return null
  }
}

function sizeOverlayCanvas(overlayCanvas, drawCanvas, host) {
  if (!overlayCanvas || !drawCanvas) return
  overlayCanvas.width = drawCanvas.width || 1
  overlayCanvas.height = drawCanvas.height || 1
  const w = drawCanvas.clientWidth || host.clientWidth || drawCanvas.width
  const h = drawCanvas.clientHeight || host.clientHeight || drawCanvas.height
  overlayCanvas.style.width = `${w}px`
  overlayCanvas.style.height = `${h}px`
}

function appendOverlayCanvas(host, registry, className, extraStyle = '') {
  let canvas = registry.get(host)
  if (!canvas || canvas.parentElement !== host) {
    canvas = document.createElement('canvas')
    canvas.className = className
    canvas.style.cssText =
      `position:absolute;top:0;left:0;pointer-events:none;z-index:99;${extraStyle}`
    if (!host.style.position || host.style.position === 'static') {
      host.style.position = 'relative'
    }
    host.appendChild(canvas)
    registry.set(host, canvas)
  }
  return canvas
}

export function getImageInstanceUid(element) {
  if (!element) return null
  try {
    const image = cornerstone.getImage(element)
    if (!image || !image.data || !image.data.byteArray) return null
    const dataSet = dicomParser.parseDicom(image.data.byteArray)
    return dataSet.string('x00080018') || null
  } catch (e) {
    return null
  }
}

export function truncateUid(uid, head = 10, tail = 8) {
  if (!uid || uid.length <= head + tail + 3) return uid || ''
  return `${uid.slice(0, head)}...${uid.slice(-tail)}`
}

const SUBTYPE_LABELS = {
  pureGGO: '磨玻璃',
  mixedGGO: '混合磨玻璃',
  solid: '实性',
  calcified: '钙化',
  other: '其他'
}

const DETECTION_CLASS_LABELS = {
  ggo: '磨玻璃',
  solid: '实性结节',
  solid_suspicious: '实性可疑',
  mixed_ggo: '混合磨玻璃',
  calcified: '钙化/高密度',
  unknown: '待复核'
}

/** 优先用 subType/detectionClass 映射，避免后端汉字在部分环境乱码 */
export function formatLesionDisplayLabel(lesion) {
  if (!lesion) return '疑似病灶'
  if (lesion.detectionClass && DETECTION_CLASS_LABELS[lesion.detectionClass]) {
    return DETECTION_CLASS_LABELS[lesion.detectionClass]
  }
  if (lesion.subType && SUBTYPE_LABELS[lesion.subType]) {
    return SUBTYPE_LABELS[lesion.subType]
  }
  const raw = lesion.detectionClassLabel || lesion.label || lesion.type || ''
  if (raw && !isGarbledText(raw)) return raw
  return '疑似病灶'
}

const DEFAULT_DISCLAIMER = 'AI 辅助结果仅供临床参考，不能替代医生诊断。'

export function formatDisclaimer(text) {
  if (!text || isGarbledText(text)) return DEFAULT_DISCLAIMER
  return text
}

function isGarbledText(text) {
  if (!text) return true
  const s = String(text).trim()
  if (!s) return true
  // 含中文则视为正常
  if (/[\u4e00-\u9fff]/.test(s)) return false
  // 纯问号、或含大量 ? 的占位符（如 ???/???）
  if (/^[\s?？./\\|]+$/.test(s)) return true
  if ((s.match(/\?/g) || []).length >= 2) return true
  return false
}

/** 从数值字段推断展示文案（历史记录汉字损坏时的兜底） */
export function formatPleuralHint(lesion) {
  if (lesion.pleuralHint && !isGarbledText(lesion.pleuralHint)) {
    return lesion.pleuralHint
  }
  const d = lesion.pleuralDistanceMm
  if (d == null) return null
  if (d <= 3) return '胸膜下/贴胸膜'
  if (d <= 8) return '近胸膜'
  return null
}

export function formatLobeLabel(lesion) {
  if (lesion.lobeLabel && !isGarbledText(lesion.lobeLabel)) {
    return lesion.lobeLabel
  }
  return null
}

export function formatMorphologyHints(lesion) {
  const hints = []
  const pleural = formatPleuralHint(lesion)
  if (pleural) hints.push({ type: 'pleural', text: pleural })

  const morph = lesion.morphology || {}
  const spic = lesion.spiculationHint || morph.spiculationHint
  if (spic && spic !== '未见明显' && !isGarbledText(spic)) {
    hints.push({ type: 'spiculation', text: spic })
  }
  const cav = lesion.cavitationHint || morph.cavitationHint
  if (cav && !isGarbledText(cav)) {
    hints.push({ type: 'cavitation', text: cav })
  }
  if (lesion.enhancementHint && !isGarbledText(lesion.enhancementHint)) {
    hints.push({ type: 'enhance', text: lesion.enhancementHint })
  }
  const lob = lesion.lobulationHint || morph.lobulationHint
  if (lob && lob !== '光滑' && !isGarbledText(lob)) {
    hints.push({ type: 'lobulation', text: lob })
  }
  return hints
}

export function isChestBodyPart(bodyPart) {
  if (!bodyPart) return false
  const upper = String(bodyPart).toUpperCase()
  return CHEST_KEYWORDS.some((kw) => upper.includes(kw))
}

export function findSeriesMeta(studySeriesList, dicomId) {
  if (!studySeriesList || dicomId == null) return null
  for (const studyUid in studySeriesList) {
    const seriesMap = studySeriesList[studyUid]
    if (!seriesMap) continue
    for (const key in seriesMap) {
      const series = seriesMap[key]
      if (series && String(series.dicomId) === String(dicomId)) {
        return { studyUid, series }
      }
    }
  }
  return null
}

/** 从 cornerstone stack 工具状态同步并返回当前层索引 */
export function getSyncedStackIndex(element, canvasStack) {
  if (!element || !canvasStack) return 0
  try {
    const state = cornerstoneTools.getToolState(element, 'stack')
    if (state && state.data && state.data.length) {
      const idx = state.data[0].currentImageIdIndex
      if (idx != null && !Number.isNaN(idx)) {
        canvasStack.currentImageIdIndex = idx
        if (canvasStack.imageIds && canvasStack.imageIds[idx]) {
          canvasStack.currentImageId = canvasStack.imageIds[idx]
        }
        return idx
      }
    }
  } catch (e) { /* ignore */ }
  return canvasStack.currentImageIdIndex || 0
}

/** 将 canvasStack 写回 cornerstone stack 工具状态 */
export function syncCornerstoneStackState(element, canvasStack) {
  if (!element || !canvasStack) return
  try {
    const state = cornerstoneTools.getToolState(element, 'stack')
    if (state && state.data && state.data.length) {
      const stack = state.data[0]
      stack.currentImageIdIndex = canvasStack.currentImageIdIndex
      stack.imageIds = canvasStack.imageIds
      stack.currentImageId = canvasStack.imageIds[canvasStack.currentImageIdIndex] || null
    }
  } catch (e) { /* ignore */ }
}

/** 展平 study 下所有序列，带序号 */
export function flattenStudySeries(studySeriesList) {
  const items = []
  let index = 1
  const list = studySeriesList || {}
  for (const studyUid in list) {
    const seriesMap = list[studyUid]
    if (!seriesMap) continue
    Object.values(seriesMap).forEach((series) => {
      if (!series || !series.dicomId) return
      const imageCount = (series.imageIds && series.imageIds.length) ||
        Number(series.dicomCtCount) || 0
      items.push({
        index: index++,
        studyUid,
        series,
        dicomId: series.dicomId,
        bodyPart: series.dicomCtBody || '未知',
        imageCount,
        seriesUid: series.dicomCtSeriesUid,
        allowDetect: isChestBodyPart(series.dicomCtBody)
      })
    })
  }
  return items
}

function injectOverlayStyles() {
  if (stylesInjected) return
  stylesInjected = true
  const style = document.createElement('style')
  style.textContent = `
    .lesion-ai-tooltip {
      position: fixed;
      z-index: 4000;
      max-width: 280px;
      padding: 10px 12px;
      border-radius: 6px;
      background: rgba(18, 22, 28, 0.96);
      border: 1px solid rgba(0, 255, 0, 0.55);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45);
      color: #e8eaed;
      font-size: 12px;
      line-height: 1.5;
      pointer-events: none;
      display: none;
    }
    .lesion-ai-tooltip__title {
      font-weight: 600;
      color: #7dff7d;
      margin-bottom: 6px;
    }
    .lesion-ai-tooltip__body {
      color: #c5cad3;
    }
    .lesion-ai-tooltip__slice {
      margin-top: 6px;
      color: #9aa0a8;
      font-size: 11px;
    }
    .lesion-heatmap-canvas {
      position: absolute;
      top: 0;
      left: 0;
      pointer-events: none;
      z-index: 100;
    }
  `
  document.head.appendChild(style)
}

function getTooltipEl() {
  injectOverlayStyles()
  if (!tooltipEl) {
    tooltipEl = document.createElement('div')
    tooltipEl.className = 'lesion-ai-tooltip'
    document.body.appendChild(tooltipEl)
  }
  return tooltipEl
}

function hideTooltip() {
  if (tooltipEl) tooltipEl.style.display = 'none'
}

function showTooltip(clientX, clientY, lesion) {
  const el = getTooltipEl()
  const detConf = lesion.detectionConfidence != null
    ? lesion.detectionConfidence
    : lesion.confidence
  const conf = detConf != null ? `${(detConf * 100).toFixed(1)}%` : ''
  const title = `${formatLesionDisplayLabel(lesion)}${conf ? ` · ${conf}` : ''}`
  const metrics = formatLesionMetrics(lesion)
  const hints = formatMorphologyHints(lesion)
  const hintText = hints.map((h) => h.text).join(' · ')
  const slice = lesion.sliceIndex != null ? `层位 ${lesion.sliceIndex + 1}` : ''
  el.innerHTML = `
    <div class="lesion-ai-tooltip__title">${title}</div>
    <div class="lesion-ai-tooltip__body">${metrics || '暂无测量数据'}${hintText ? `<br>${hintText}` : ''}</div>
    ${slice ? `<div class="lesion-ai-tooltip__slice">${slice}</div>` : ''}
  `
  el.style.display = 'block'
  el.style.left = `${clientX + 14}px`
  el.style.top = `${clientY + 14}px`
}

function toPixelBox(lesion, image) {
  const bbox = lesion.bbox || {}
  const cols = image.columns || 512
  const rows = image.rows || 512
  if (bbox.x != null && bbox.y != null && bbox.width != null && bbox.height != null) {
    if (bbox.x <= 1 && bbox.y <= 1 && bbox.width <= 1 && bbox.height <= 1) {
      return {
        x: bbox.x * cols,
        y: bbox.y * rows,
        width: Math.max(bbox.width * cols, 8),
        height: Math.max(bbox.height * rows, 8)
      }
    }
    return {
      x: bbox.x,
      y: bbox.y,
      width: Math.max(bbox.width, 8),
      height: Math.max(bbox.height, 8)
    }
  }
  return { x: cols * 0.42, y: rows * 0.38, width: cols * 0.12, height: rows * 0.1 }
}

function getMousePixelCoords(canvas, event) {
  const rect = canvas.getBoundingClientRect()
  const canvasPt = {
    x: event.clientX - rect.left,
    y: event.clientY - rect.top
  }
  return cornerstone.canvasToPixel(canvas, canvasPt)
}

function toPixelPoint(point, image) {
  const cols = image.columns || 512
  const rows = image.rows || 512
  return {
    x: point.x <= 1 ? point.x * cols : point.x,
    y: point.y <= 1 ? point.y * rows : point.y
  }
}

function getLesionContourPixels(lesion, image) {
  if (Array.isArray(lesion.contour) && lesion.contour.length >= 3) {
    return lesion.contour.map((p) => toPixelPoint(p, image))
  }
  return []
}

function pointInPolygon(px, py, polygon) {
  let inside = false
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const xi = polygon[i].x
    const yi = polygon[i].y
    const xj = polygon[j].x
    const yj = polygon[j].y
    if ((yi > py) !== (yj > py) && px < ((xj - xi) * (py - yi)) / (yj - yi) + xi) {
      inside = !inside
    }
  }
  return inside
}

export function formatLesionMetrics(lesion) {
  return formatLesionMetricsLines(lesion)
    .map(({ label, value }) => `${label} ${value}`)
    .join(' · ')
}

/** 病灶测量明细（侧边栏逐行展示） */
export function formatLesionMetricsLines(lesion) {
  if (!lesion) return []
  const lines = []
  if (lesion.longAxisMm != null) {
    lines.push({ label: '长径', value: `${lesion.longAxisMm} mm` })
  }
  if (lesion.shortAxisMm != null) {
    lines.push({ label: '短径', value: `${lesion.shortAxisMm} mm` })
  }
  if (lesion.diameterMm != null && lesion.longAxisMm == null) {
    lines.push({ label: '直径', value: `${lesion.diameterMm} mm` })
  }
  if (lesion.areaMm2 != null) {
    lines.push({ label: '面积', value: `${lesion.areaMm2.toFixed(1)} mm²` })
  }
  if (lesion.volumeMm3 != null) {
    lines.push({ label: '体积', value: `${lesion.volumeMm3.toFixed(1)} mm³` })
  }
  const huMean = lesion.huMean != null ? lesion.huMean : lesion.hu
  if (huMean != null) {
    lines.push({ label: '平均 HU', value: `${Number(huMean).toFixed(0)}` })
  }
  if (lesion.huMin != null) {
    lines.push({ label: '最小 HU', value: `${Number(lesion.huMin).toFixed(0)}` })
  }
  if (lesion.huMax != null) {
    lines.push({ label: '最大 HU', value: `${Number(lesion.huMax).toFixed(0)}` })
  }
  if (lesion.subType) {
    const subLabels = {
      pureGGO: '纯磨玻璃',
      mixedGGO: '混合磨玻璃',
      solid: '实性',
      calcified: '钙化',
      other: '其他'
    }
    lines.push({
      label: '亚型',
      value: subLabels[lesion.subType] || lesion.subType
    })
  }
  if (lesion.detectionClass && DETECTION_CLASS_LABELS[lesion.detectionClass]) {
    lines.push({ label: '智能分类', value: DETECTION_CLASS_LABELS[lesion.detectionClass] })
  } else if (lesion.detectionClassLabel && !/^[\s?？]+$/.test(String(lesion.detectionClassLabel))) {
    lines.push({ label: '智能分类', value: lesion.detectionClassLabel })
  }
  const detConf = lesion.detectionConfidence != null
    ? lesion.detectionConfidence
    : lesion.confidence
  if (detConf != null) {
    lines.push({ label: '检测置信度', value: `${(detConf * 100).toFixed(1)}%` })
  }
  if (lesion.classificationConfidence != null) {
    lines.push({
      label: '分类置信度',
      value: `${(lesion.classificationConfidence * 100).toFixed(1)}%`
    })
  }
  if (lesion.pleuralDistanceMm != null) {
    lines.push({ label: '胸膜距离', value: `${lesion.pleuralDistanceMm} mm` })
  }
  const pleuralHint = formatPleuralHint(lesion)
  if (pleuralHint) {
    lines.push({ label: '胸膜提示', value: pleuralHint })
  }
  const lobeLabel = formatLobeLabel(lesion)
  if (lobeLabel) {
    lines.push({ label: '肺叶位置', value: lobeLabel })
  }
  if (lesion.lobulationHint && !isGarbledText(lesion.lobulationHint)) {
    lines.push({ label: '边缘形态', value: lesion.lobulationHint })
  }
  if (lesion.spiculationHint && lesion.spiculationHint !== '未见明显' && !isGarbledText(lesion.spiculationHint)) {
    lines.push({ label: '毛刺倾向', value: lesion.spiculationHint })
  }
  if (lesion.cavitationHint && !isGarbledText(lesion.cavitationHint)) {
    lines.push({ label: '空泡征', value: lesion.cavitationHint })
  }
  if (lesion.enhancementHint && !isGarbledText(lesion.enhancementHint)) {
    lines.push({ label: '强化特征', value: lesion.enhancementHint })
  }
  if (lesion.deltaHu != null) {
    lines.push({ label: 'ΔHU', value: `${Number(lesion.deltaHu).toFixed(1)}` })
  }
  if (lesion.positionHint && !isGarbledText(lesion.positionHint)) {
    lines.push({ label: '位置提示', value: lesion.positionHint })
  }
  return lines
}

function filterVisibleLesions(lesions) {
  if (!lesions || !lesions.length) return []
  return lesions.filter((l) => l.markerVisible !== false)
}

function filterVisibleGgoRegions(regions) {
  if (!regions || !regions.length) return []
  return regions.filter((r) => r.markerVisible !== false)
}

const MARKER_STYLES = {
  solid: {
    fill: 'rgba(255, 80, 60, 0.30)',
    stroke: 'rgba(255, 100, 70, 0.95)',
    label: 'rgba(255, 200, 180, 0.98)',
    labelBg: 'rgba(48, 16, 8, 0.85)'
  },
  ggo: {
    fill: 'rgba(60, 180, 255, 0.25)',
    stroke: 'rgba(80, 200, 255, 0.92)',
    label: 'rgba(180, 230, 255, 0.98)',
    labelBg: 'rgba(8, 32, 56, 0.85)'
  },
  mixed: {
    fill: 'rgba(200, 80, 255, 0.28)',
    stroke: 'rgba(220, 120, 255, 0.94)',
    label: 'rgba(230, 190, 255, 0.98)',
    labelBg: 'rgba(40, 12, 56, 0.85)'
  },
  calcified: {
    fill: 'rgba(255, 220, 60, 0.40)',
    stroke: 'rgba(255, 235, 100, 0.95)',
    label: 'rgba(255, 245, 200, 0.98)',
    labelBg: 'rgba(48, 40, 8, 0.85)'
  },
  unknown: {
    fill: 'rgba(0, 200, 100, 0.22)',
    stroke: 'rgba(0, 230, 130, 0.92)',
    label: 'rgba(140, 255, 180, 0.98)',
    labelBg: 'rgba(0, 48, 28, 0.82)'
  }
}

function resolveMarkerStyle(lesion) {
  const key = lesion.colorKey || 'unknown'
  return MARKER_STYLES[key] || MARKER_STYLES.unknown
}

function drawTypeLabel(ctx, style, text, x, y) {
  ctx.font = '12px "Microsoft YaHei", "PingFang SC", sans-serif'
  const metrics = ctx.measureText(text)
  const pad = 4
  const tw = metrics.width + pad * 2
  const th = 16
  const lx = Math.max(2, x)
  const ly = Math.max(th + 2, y)
  ctx.fillStyle = style.labelBg
  ctx.fillRect(lx, ly - th, tw, th)
  ctx.fillStyle = style.label
  ctx.fillText(text, lx + pad, ly - 4)
}

function drawLesionMarker(ctx, lesion, contour, box, style) {
  const markerType = lesion.markerType || 'contour'
  const label = formatLesionDisplayLabel(lesion)
  const detConf = lesion.detectionConfidence != null
    ? lesion.detectionConfidence
    : lesion.confidence
  const conf = detConf != null ? ` ${(detConf * 100).toFixed(0)}%` : ''
  const labelText = `${label}${conf}`

  if (markerType === 'circle' && box.width > 0 && box.height > 0) {
    const cx = box.x + box.width / 2
    const cy = box.y + box.height / 2
    const rx = Math.max(box.width / 2, 4)
    const ry = Math.max(box.height / 2, 4)
    ctx.beginPath()
    ctx.ellipse(cx, cy, rx, ry, 0, 0, Math.PI * 2)
    ctx.fillStyle = style.fill
    ctx.fill()
    ctx.strokeStyle = style.stroke
    ctx.lineWidth = 2
    ctx.stroke()
    drawTypeLabel(ctx, style, labelText, cx - rx + 2, cy - ry - 4)
    return
  }

  if (markerType === 'diamond' && box.width > 0 && box.height > 0) {
    const cx = box.x + box.width / 2
    const cy = box.y + box.height / 2
    const hw = Math.max(box.width / 2, 4)
    const hh = Math.max(box.height / 2, 4)
    ctx.beginPath()
    ctx.moveTo(cx, cy - hh)
    ctx.lineTo(cx + hw, cy)
    ctx.lineTo(cx, cy + hh)
    ctx.lineTo(cx - hw, cy)
    ctx.closePath()
    ctx.fillStyle = style.fill
    ctx.fill()
    ctx.strokeStyle = style.stroke
    ctx.lineWidth = 2
    ctx.stroke()
    drawTypeLabel(ctx, style, labelText, cx - hw + 2, cy - hh - 4)
    return
  }

  if (contour.length >= 3) {
    ctx.beginPath()
    ctx.moveTo(contour[0].x, contour[0].y)
    for (let i = 1; i < contour.length; i++) {
      ctx.lineTo(contour[i].x, contour[i].y)
    }
    ctx.closePath()
    ctx.fillStyle = style.fill
    ctx.fill()
    ctx.strokeStyle = style.stroke
    ctx.lineWidth = 2
    ctx.setLineDash([])
    ctx.stroke()

    if (markerType === 'contour+circle' && box.width > 0) {
      const cx = box.x + box.width / 2
      const cy = box.y + box.height / 2
      const r = Math.max(Math.min(box.width, box.height) * 0.15, 3)
      ctx.beginPath()
      ctx.arc(cx, cy, r, 0, Math.PI * 2)
      ctx.fillStyle = 'rgba(255, 120, 80, 0.75)'
      ctx.fill()
    }

    let lx = contour[0].x
    let ly = contour[0].y
    for (const p of contour) {
      if (p.y < ly || (p.y === ly && p.x < lx)) {
        lx = p.x
        ly = p.y
      }
    }
    drawTypeLabel(ctx, style, labelText, lx + 2, ly - 4)
    return
  }

  ctx.strokeStyle = style.stroke
  ctx.lineWidth = 2
  ctx.setLineDash([])
  ctx.strokeRect(box.x, box.y, box.width, box.height)
  drawTypeLabel(ctx, style, labelText, box.x + 2, box.y - 4)
}

// ---------------------------------------------------------------------------
// 核心渲染入口（按 overlayType 分支）
// ---------------------------------------------------------------------------

/**
 * renderLesionOverlays — 主入口。
 * 根据 meta.overlayType 分发到不同渲染器。
 *
 * @param {HTMLElement} element - Cornerstone enabled element
 * @param {Array} lesions - 病灶列表
 * @param {Object} meta - { overlayType, heatmap, ggoRegions, sliceIndex, ... }
 */
export function renderLesionOverlays(element, lesions, meta) {
  const overlayType = (meta && meta.overlayType) || 'bbox'

  if (overlayType === 'heatmap') {
    clearBboxOverlays(element)
    clearGgoOverlay(element)
    return renderHeatmapOverlay(element, meta)
  }

  renderBboxOverlays(element, lesions, meta)
  const visibleLesions = filterVisibleLesions(lesions)
  const sliceIdx = meta && meta.sliceIndex
  const hasLesionOnSlice = visibleLesions.some(
    (l) => l.sliceIndex == null || l.sliceIndex === sliceIdx
  )
  if (
    !hasLesionOnSlice
    && meta
    && meta.overlayType === 'ggo'
    && meta.ggoRegions
    && meta.ggoRegions.length
  ) {
    renderGgoOverlay(element, meta)
  } else {
    clearGgoOverlay(element)
  }
}

export function clearLesionOverlays(element) {
  clearBboxOverlays(element)
  clearHeatmapOverlay(element)
  clearGgoOverlay(element)
}

// ---------------------------------------------------------------------------
// bbox + contour 叠加（方案 A/B）— 独立 canvas，避免擦除 DICOM 底图
// ---------------------------------------------------------------------------

function getStackSliceIndex(element, meta) {
  if (meta && meta.sliceIndex != null) return meta.sliceIndex
  try {
    const state = cornerstoneTools.getToolState(element, 'stack')
    if (state && state.data && state.data.length) {
      return state.data[0].currentImageIdIndex
    }
  } catch (e) { /* ignore */ }
  return null
}

function ensureBboxOverlayCanvas(element) {
  const vp = getViewportInfo(element)
  if (!vp) return null
  const { host, drawCanvas } = vp
  const canvas = appendOverlayCanvas(host, bboxCanvasRegistry, 'lesion-bbox-canvas')
  sizeOverlayCanvas(canvas, drawCanvas, host)
  return canvas
}

function mapPixelPointToCanvas(element, point) {
  return cornerstone.pixelToCanvas(element, { x: point.x, y: point.y })
}

function mapPixelBoxToCanvas(element, box) {
  const tl = mapPixelPointToCanvas(element, { x: box.x, y: box.y })
  const br = mapPixelPointToCanvas(element, { x: box.x + box.width, y: box.y + box.height })
  return {
    x: tl.x,
    y: tl.y,
    width: br.x - tl.x,
    height: br.y - tl.y
  }
}

export function renderBboxOverlays(element, lesions, meta = {}) {
  clearBboxOverlays(element)
  lesions = filterVisibleLesions(lesions)
  if (!lesions || !lesions.length) return

  const enabledElement = cornerstone.getEnabledElement(element)
  if (!enabledElement || !enabledElement.image) return

  const image = enabledElement.image
  let lesionsRef = lesions
  let metaRef = meta

  const draw = () => {
    const sliceIndex = getStackSliceIndex(element, metaRef)
    const overlayCanvas = ensureBboxOverlayCanvas(element)
    if (!overlayCanvas) return
    const ctx = overlayCanvas.getContext('2d')
    if (!ctx) return

    ctx.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height)
    const currentLesions = lesionsRef.filter(
      (l) => l.sliceIndex == null || l.sliceIndex === sliceIndex
    )
    if (!currentLesions.length) {
      overlayCanvas.style.display = 'none'
      hideTooltip()
      return
    }
    overlayCanvas.style.display = 'block'

    for (const lesion of currentLesions) {
      const contour = getLesionContourPixels(lesion, image).map((p) =>
        mapPixelPointToCanvas(element, p)
      )
      const box = mapPixelBoxToCanvas(element, toPixelBox(lesion, image))
      const style = resolveMarkerStyle(lesion)
      drawLesionMarker(ctx, lesion, contour, box, style)
    }
  }

  const onMouseMove = (event) => {
    const sliceIndex = getStackSliceIndex(element, metaRef)
    const currentLesions = lesionsRef.filter(
      (l) => l.sliceIndex == null || l.sliceIndex === sliceIndex
    )
    const px = getMousePixelCoords(element, event)
    for (const lesion of currentLesions) {
      const contour = getLesionContourPixels(lesion, image)
      if (pointInPolygon(px.x, px.y, contour)) {
        showTooltip(event.clientX, event.clientY, lesion)
        return
      }
    }
    hideTooltip()
  }

  const onMouseOut = () => hideTooltip()
  const onImageRendered = () => draw()

  element.addEventListener('mousemove', onMouseMove)
  element.addEventListener('mouseout', onMouseOut)
  element.addEventListener('cornerstoneimagerendered', onImageRendered)

  overlayRegistry.set(element, [{
    cleanups: [
      () => element.removeEventListener('mousemove', onMouseMove),
      () => element.removeEventListener('mouseout', onMouseOut),
      () => element.removeEventListener('cornerstoneimagerendered', onImageRendered)
    ]
  }])

  draw()
}

function clearBboxOverlays(element) {
  const entries = overlayRegistry.get(element)
  if (entries) {
    for (const entry of entries) {
      if (entry.cleanups) {
        entry.cleanups.forEach((fn) => { try { fn() } catch (e) { /* ignore */ } })
      }
    }
    overlayRegistry.delete(element)
  }
  hideTooltip()
  const canvas = bboxCanvasRegistry.get(element)
  if (canvas && canvas.parentElement) {
    canvas.parentElement.removeChild(canvas)
  }
  bboxCanvasRegistry.delete(element)
}

// ---------------------------------------------------------------------------
// heatmap 叠加（方案 C）
// ---------------------------------------------------------------------------

function renderHeatmapOverlay(element, meta) {
  clearHeatmapOverlay(element)
  if (!meta || !meta.heatmap) return

  const heatmap = meta.heatmap
  const sliceIndex = getStackSliceIndex(element, meta)
  if (sliceIndex == null) return
  if (meta.heatmapSliceIndex != null && meta.heatmapSliceIndex !== sliceIndex) {
    clearHeatmapOverlay(element)
    return
  }

  const enabledElement = cornerstone.getEnabledElement(element)
  if (!enabledElement || !enabledElement.image) return
  const vp = getViewportInfo(element)
  if (!vp) return
  const { host, drawCanvas } = vp
  const canvas = appendOverlayCanvas(host, heatmapRegistry, 'lesion-heatmap-canvas')
  sizeOverlayCanvas(canvas, drawCanvas, host)

  const ctx = canvas.getContext('2d')
  ctx.clearRect(0, 0, canvas.width, canvas.height)

  const image = enabledElement.image
  const imgCols = image.columns || 512
  const imgRows = image.rows || 512
  const gridW = heatmap.width || 64
  const gridH = heatmap.height || 64
  const values = heatmap.values || []

  if (!values.length) return

  // 热力图每个格子映射到图像像素区域，再通过 cornerstone pixelToCanvas 定位
  const cellImgW = imgCols / gridW
  const cellImgH = imgRows / gridH

  for (let gy = 0; gy < gridH; gy++) {
    for (let gx = 0; gx < gridW; gx++) {
      const idx = gy * gridW + gx
      const v = idx < values.length ? Math.max(0, Math.min(1, values[idx])) : 0
      if (v < 0.08) continue  // 跳过正常/低异常像素

      // 图像像素坐标 → canvas 坐标
      const imgX1 = gx * cellImgW
      const imgY1 = gy * cellImgH
      const imgX2 = (gx + 1) * cellImgW
      const imgY2 = (gy + 1) * cellImgH

      const c1 = cornerstone.pixelToCanvas(element, { x: imgX1, y: imgY1 })
      const c2 = cornerstone.pixelToCanvas(element, { x: imgX2, y: imgY2 })

      const cx = Math.min(c1.x, c2.x)
      const cy = Math.min(c1.y, c2.y)
      const cw = Math.max(Math.abs(c2.x - c1.x), 2)
      const ch = Math.max(Math.abs(c2.y - c1.y), 2)

      // 裁剪到 canvas 范围
      if (cx + cw < 0 || cy + ch < 0 || cx > canvas.width || cy > canvas.height) continue

      // 蓝→红 颜色映射
      const r = Math.floor(v * 255)
      const b = Math.floor((1 - v) * 255)
      const g = Math.floor(50 * (1 - Math.abs(v - 0.5) * 2))
      const alpha = Math.floor(v * 110)

      ctx.fillStyle = `rgba(${r},${g},${b},${alpha / 255})`
      ctx.fillRect(cx, cy, cw, ch)
    }
  }
}

function clearHeatmapOverlay(element) {
  const host = element
  const canvas = heatmapRegistry.get(host)
  if (canvas && canvas.parentElement) {
    canvas.parentElement.removeChild(canvas)
  }
  heatmapRegistry.delete(host)
}

// ---------------------------------------------------------------------------
// GGO 叠加（方案 B）
// ---------------------------------------------------------------------------

function renderGgoOverlay(element, meta) {
  clearGgoOverlay(element)
  if (!meta || !meta.ggoRegions || !meta.ggoRegions.length) return

  const sliceIndex = getStackSliceIndex(element, meta)
  if (sliceIndex == null) return

  const regions = filterVisibleGgoRegions(meta.ggoRegions).filter(
    (r) => r.sliceIndex == null || r.sliceIndex === sliceIndex
  )
  if (!regions.length) return

  const enabledElement = cornerstone.getEnabledElement(element)
  const image = enabledElement && enabledElement.image
  const vp = getViewportInfo(element)
  if (!vp) return
  const { host, drawCanvas } = vp
  const canvas = appendOverlayCanvas(
    host,
    ggoRegistry,
    'lesion-ggo-canvas',
    'pointer-events:none;'
  )
  sizeOverlayCanvas(canvas, drawCanvas, host)

  const ctx = canvas.getContext('2d')
  ctx.clearRect(0, 0, canvas.width, canvas.height)

  regions.forEach((region, idx) => {
    const points = region.points || region.contour || []
    if (points.length < 3) return
    const pixelPts = points.map((pt) => {
      if (!image) {
        const w = canvas.width
        const h = canvas.height
        return {
          x: (Array.isArray(pt) ? pt[0] : pt.x) * w,
          y: (Array.isArray(pt) ? pt[1] : pt.y) * h
        }
      }
      return mapPixelPointToCanvas(element, toPixelPoint(
        Array.isArray(pt) ? { x: pt[0], y: pt[1] } : pt,
        image
      ))
    })
    ctx.beginPath()
    pixelPts.forEach((p, i) => {
      if (i === 0) ctx.moveTo(p.x, p.y)
      else ctx.lineTo(p.x, p.y)
    })
    ctx.closePath()
    ctx.fillStyle = MARKER_STYLES.ggo.fill
    ctx.strokeStyle = MARKER_STYLES.ggo.stroke
    ctx.lineWidth = 2
    ctx.fill()
    ctx.stroke()

    let lx = pixelPts[0].x
    let ly = pixelPts[0].y
    for (const p of pixelPts) {
      if (p.y < ly || (p.y === ly && p.x < lx)) {
        lx = p.x
        ly = p.y
      }
    }
    const label = region.label || '疑似磨玻璃区域'
    const area = region.areaMm2 != null ? ` ${region.areaMm2.toFixed(1)}mm²` : ''
    drawTypeLabel(ctx, MARKER_STYLES.ggo, `${label}${area}`, lx + 2, ly - 4)
  })
}

function clearGgoOverlay(element) {
  const host = element
  const canvas = ggoRegistry.get(host)
  if (canvas && canvas.parentElement) {
    canvas.parentElement.removeChild(canvas)
  }
  ggoRegistry.delete(host)
}

export default {
  isChestBodyPart,
  findSeriesMeta,
  flattenStudySeries,
  getSyncedStackIndex,
  syncCornerstoneStackState,
  renderLesionOverlays,
  clearLesionOverlays,
  renderBboxOverlays,
  renderHeatmapOverlay,
  renderGgoOverlay,
  getImageInstanceUid,
  truncateUid
}
