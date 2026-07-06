import { minioUrl } from '@/settings'
import { findSeriesMeta } from '@/utils/lesionDetect'

export function buildAiLesionImageIds(record, bucketName, dicomPrefix = 'wadouri:') {
  if (!record || !record.aiSeriesPath || !record.imageCount || !bucketName) {
    return []
  }
  const folder = record.aiSeriesPath.substring(0, record.aiSeriesPath.lastIndexOf('/'))
  const ids = []
  for (let i = 1; i <= record.imageCount; i++) {
    ids.push(`${dicomPrefix}${minioUrl}${bucketName}/${folder}/${i}.dcm`)
  }
  return ids
}

/** 解析 lesionsJson：兼容纯数组或 v2 结构化对象 */
export function parseLesionResultJson(lesionsJson) {
  if (!lesionsJson) {
    return {
      version: 2,
      lesions: [],
      overlayType: 'bbox',
      heatmap: null,
      screening: null,
      ggoRegions: [],
      detectMode: 'series',
      sliceIndex: null,
      instanceUid: null
    }
  }
  try {
    const parsed = typeof lesionsJson === 'string' ? JSON.parse(lesionsJson) : lesionsJson
    if (Array.isArray(parsed)) {
      return {
        version: 1,
        lesions: parsed,
        overlayType: 'bbox',
        heatmap: null,
        screening: null,
        ggoRegions: [],
        detectMode: 'series',
        sliceIndex: null,
        instanceUid: null
      }
    }
    if (parsed && typeof parsed === 'object') {
      return {
        version: parsed.version || 2,
        lesions: parsed.lesions || [],
        overlayType: parsed.overlayType || 'bbox',
        heatmap: parsed.heatmap || null,
        screening: parsed.screening || null,
        ggoRegions: parsed.ggoRegions || [],
        detectMode: parsed.detectMode || 'series',
        sliceIndex: parsed.sliceIndex != null ? parsed.sliceIndex : null,
        heatmapSliceIndex: parsed.heatmapSliceIndex != null
          ? parsed.heatmapSliceIndex
          : parsed.sliceIndex,
        instanceUid: parsed.instanceUid || null
      }
    }
  } catch (e) {
    // ignore
  }
  return {
    version: 2,
    lesions: [],
    overlayType: 'bbox',
    heatmap: null,
    screening: null,
    ggoRegions: [],
    detectMode: 'series',
    sliceIndex: null,
    instanceUid: null
  }
}

export function parseLesionsJson(lesionsJson) {
  return parseLesionResultJson(lesionsJson).lesions
}

export function buildLesionResultPayload(result) {
  return {
    version: 2,
    lesions: result.lesions || [],
    overlayType: result.overlayType || 'bbox',
    heatmap: result.heatmap || null,
    screening: result.screening || null,
    ggoRegions: result.ggoRegions || [],
    detectMode: result.detectMode || 'series',
    sliceIndex: result.sliceIndex != null ? result.sliceIndex : null,
    heatmapSliceIndex: result.heatmapSliceIndex != null
      ? result.heatmapSliceIndex
      : result.sliceIndex,
    instanceUid: result.instanceUid || null
  }
}

export function lesionResultFromSavedRecord(record) {
  const parsed = parseLesionResultJson(record.lesionsJson)
  return {
    status: (record.lesionCount > 0 || parsed.overlayType === 'heatmap') ? 'done' : 'empty',
    lesions: parsed.lesions,
    lesionCount: record.lesionCount || parsed.lesions.length,
    disclaimer: record.disclaimer || '',
    engine: record.engine || '',
    overlayType: parsed.overlayType,
    heatmap: parsed.heatmap,
    screening: parsed.screening,
    ggoRegions: parsed.ggoRegions,
    detectMode: parsed.detectMode,
    sliceIndex: parsed.sliceIndex,
    heatmapSliceIndex: parsed.heatmapSliceIndex,
    instanceUid: record.instanceUid || parsed.instanceUid || null,
    sourceSliceIndex: record.sourceSliceIndex != null
      ? record.sourceSliceIndex
      : parsed.sliceIndex,
    sourceDicomId: record.sourceDicomId,
    saved: true
  }
}

export function formatDetectModeLabel(mode) {
  if (mode === 'single') return '当前层'
  return '全序列'
}

export function enrichAiLesionRecord(record, bucketName, options = {}) {
  const { studySeriesList = null, dicomPrefix = 'wadouri:' } = options
  const parsed = parseLesionResultJson(record.lesionsJson)
  const lesions = parsed.lesions
  const imageIds = buildAiLesionImageIds(record, bucketName, dicomPrefix)
  let previewImageId = imageIds[0] || null
  const sliceIdx = record.sourceSliceIndex != null
    ? record.sourceSliceIndex
    : parsed.sliceIndex
  if (studySeriesList && record.sourceDicomId != null && sliceIdx != null) {
    const found = findSeriesMeta(studySeriesList, record.sourceDicomId)
    if (found && found.series && found.series.imageIds && found.series.imageIds[sliceIdx]) {
      previewImageId = found.series.imageIds[sliceIdx]
    }
  }
  return {
    ...record,
    dicomId: 'ai-' + record.dicomAiLesionId,
    imageIds,
    previewImageId,
    lesions,
    overlayType: parsed.overlayType,
    heatmap: parsed.heatmap,
    screening: parsed.screening,
    ggoRegions: parsed.ggoRegions,
    detectMode: record.detectMode || parsed.detectMode || 'series',
    sliceIndex: parsed.sliceIndex,
    heatmapSliceIndex: parsed.heatmapSliceIndex,
    instanceUid: record.instanceUid || parsed.instanceUid || null,
    sourceSliceIndex: record.sourceSliceIndex != null
      ? record.sourceSliceIndex
      : parsed.sliceIndex,
    dicomCtStudyUid: record.studyUid,
    dicomCtSeriesUid: record.seriesUid,
    dicomCtBody: record.bodyPart,
    dicomCtTime: record.studyDate,
    isAiLesionSeries: true
  }
}

export function aiSeriesFolderFromPath(aiSeriesPath) {
  if (!aiSeriesPath || !aiSeriesPath.includes('/')) return aiSeriesPath
  return aiSeriesPath.substring(0, aiSeriesPath.lastIndexOf('/'))
}
