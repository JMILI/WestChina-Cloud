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
  const conf = lesion.confidence != null
    ? `${(lesion.confidence * 100).toFixed(1)}%`
    : ''
  const title = `${lesion.label || lesion.type || '疑似病灶'}${conf ? ` · ${conf}` : ''}`
  const metrics = formatLesionMetrics(lesion)
  const slice = lesion.sliceIndex != null ? `层位 ${lesion.sliceIndex + 1}` : ''
  el.innerHTML = `
    <div class="lesion-ai-tooltip__title">${title}</div>
    <div class="lesion-ai-tooltip__body">${metrics || '暂无测量数据'}</div>
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
  const parts = []
  if (lesion.diameterMm != null) parts.push(`${lesion.diameterMm} mm`)
  if (lesion.areaMm2 != null) parts.push(`${lesion.areaMm2.toFixed(1)} mm²`)
  if (lesion.volumeMm3 != null) parts.push(`${lesion.volumeMm3.toFixed(1)} mm³`)
  if (lesion.hu != null) parts.push(`${lesion.hu.toFixed(0)} HU`)
  return parts.join(' · ')
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
  if (meta && meta.ggoRegions && meta.ggoRegions.length) {
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

      if (contour.length >= 3) {
        ctx.beginPath()
        ctx.moveTo(contour[0].x, contour[0].y)
        for (let i = 1; i < contour.length; i++) {
          ctx.lineTo(contour[i].x, contour[i].y)
        }
        ctx.closePath()
        ctx.fillStyle = 'rgba(255, 50, 50, 0.15)'
        ctx.fill()
        ctx.strokeStyle = 'rgba(255, 50, 50, 0.9)'
        ctx.lineWidth = 2.5
        ctx.setLineDash([])
        ctx.stroke()

        let lx = contour[0].x
        let ly = contour[0].y
        for (const p of contour) {
          if (p.y < ly || (p.y === ly && p.x < lx)) {
            lx = p.x
            ly = p.y
          }
        }
        const label = lesion.label || lesion.type || '疑似病灶'
        const conf = lesion.confidence != null
          ? ` ${(lesion.confidence * 100).toFixed(0)}%`
          : ''
        ctx.font = '12px sans-serif'
        ctx.fillStyle = 'rgba(255, 50, 50, 0.95)'
        ctx.fillText(`${label}${conf}`, lx + 2, Math.max(12, ly - 4))
      } else {
        ctx.strokeStyle = 'rgba(255, 50, 50, 0.9)'
        ctx.lineWidth = 2.5
        ctx.setLineDash([6, 3])
        ctx.strokeRect(box.x, box.y, box.width, box.height)
        ctx.setLineDash([])

        const label = lesion.label || lesion.type || '疑似病灶'
        const conf = lesion.confidence != null
          ? ` ${(lesion.confidence * 100).toFixed(0)}%`
          : ''
        ctx.font = '12px sans-serif'
        ctx.fillStyle = 'rgba(255, 50, 50, 0.95)'
        ctx.fillText(`${label}${conf}`, box.x + 2, Math.max(12, box.y - 4))
      }
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

  const regions = meta.ggoRegions.filter(
    (r) => r.sliceIndex == null || r.sliceIndex === sliceIndex
  )
  if (!regions.length) return

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
  const w = canvas.width
  const h = canvas.height

  regions.forEach((region) => {
    const points = region.points || region.contour || []
    if (points.length < 3) return
    ctx.beginPath()
    points.forEach((pt, i) => {
      const x = (Array.isArray(pt) ? pt[0] : pt.x) * w
      const y = (Array.isArray(pt) ? pt[1] : pt.y) * h
      if (i === 0) ctx.moveTo(x, y)
      else ctx.lineTo(x, y)
    })
    ctx.closePath()
    ctx.fillStyle = 'rgba(0, 200, 100, 0.25)'
    ctx.strokeStyle = 'rgba(0, 220, 120, 0.7)'
    ctx.lineWidth = 1.5
    ctx.fill()
    ctx.stroke()
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
