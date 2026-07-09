import * as dicomParser from 'dicom-parser'

/** 从 DICOM 数据集提取 Instance Number */
export function instanceNumberFromDataSet(dataSet) {
  const inum = dataSet.string('x00200013')
  if (inum == null || inum === '') return null
  const n = parseInt(String(inum).trim(), 10)
  return Number.isNaN(n) ? null : n
}

function wadouriToHttpUrl(imageId) {
  if (!imageId) return ''
  return imageId.startsWith('wadouri:') ? imageId.slice('wadouri:'.length) : imageId
}

/** 从 MinIO URL 路径解析 1.dcm 中的序号（0-based fileIndex） */
export function fileIndexFromImageId(imageId) {
  const url = wadouriToHttpUrl(imageId)
  const name = url.split('/').pop() || ''
  const n = parseInt(name.replace(/\.dcm$/i, ''), 10)
  return Number.isNaN(n) ? null : n - 1
}

async function fetchSliceMeta(imageId, fileIndex) {
  try {
    const url = wadouriToHttpUrl(imageId)
    const resp = await fetch(url)
    if (!resp.ok) throw new Error(String(resp.status))
    const buf = await resp.arrayBuffer()
    const dataSet = dicomParser.parseDicom(new Uint8Array(buf))
    let instance = instanceNumberFromDataSet(dataSet)
    if (instance == null) {
      const fromName = fileIndexFromImageId(imageId)
      instance = fromName != null ? fromName + 1 : fileIndex + 1
    }
    return { imageId, fileIndex, instance }
  } catch (e) {
    const fromName = fileIndexFromImageId(imageId)
    return {
      imageId,
      fileIndex,
      instance: fromName != null ? fromName + 1 : fileIndex + 1
    }
  }
}

/**
 * 阅片 stack 按 Instance Number 升序（1,2,3…），与 AI 返回的 MinIO 文件序号建立映射。
 * AI 仍按 IPP 做 3D 分析；返回的 sliceIndex 为 fileIndex（0-based，1.dcm→0）。
 */
export async function sortImageIdsForViewer(imageIds, batchSize = 24) {
  if (!imageIds || imageIds.length <= 1) {
    return {
      imageIds: imageIds || [],
      stackIndexByFileIndex: null,
      fileIndexByStackIndex: null,
      instanceAligned: true
    }
  }

  const items = []
  for (let i = 0; i < imageIds.length; i += batchSize) {
    const batch = imageIds.slice(i, i + batchSize)
    const part = await Promise.all(
      batch.map((id, j) => fetchSliceMeta(id, i + j))
    )
    items.push(...part)
  }

  const sorted = [...items].sort((a, b) => {
    if (a.instance !== b.instance) return a.instance - b.instance
    return a.fileIndex - b.fileIndex
  })

  const stackIndexByFileIndex = new Array(items.length)
  const fileIndexByStackIndex = new Array(items.length)
  sorted.forEach((item, stackIdx) => {
    stackIndexByFileIndex[item.fileIndex] = stackIdx
    fileIndexByStackIndex[stackIdx] = item.fileIndex
  })

  const instanceAligned = sorted.every((item, stackIdx) => item.instance === stackIdx + 1)
  const fileAligned = sorted.every((item, stackIdx) => item.fileIndex === stackIdx)

  return {
    imageIds: sorted.map(i => i.imageId),
    stackIndexByFileIndex,
    fileIndexByStackIndex,
    instanceAligned,
    fileAligned
  }
}

/** AI / MinIO 文件序号 → 阅片 stack 序号 */
export function fileIndexToStackIndex(fileIndex, series) {
  if (fileIndex == null) return 0
  const idx = Number(fileIndex)
  if (series && series.stackIndexByFileIndex && series.stackIndexByFileIndex[idx] != null) {
    return series.stackIndexByFileIndex[idx]
  }
  return idx
}

/** 阅片 stack 序号 → AI / MinIO 文件序号 */
export function stackIndexToFileIndex(stackIndex, series) {
  if (stackIndex == null) return 0
  const idx = Number(stackIndex)
  if (series && series.fileIndexByStackIndex && series.fileIndexByStackIndex[idx] != null) {
    return series.fileIndexByStackIndex[idx]
  }
  return idx
}

/** 将 AI 结果中的 sliceIndex（fileIndex）转为阅片 stack 序号 */
export function mapLesionsToStackIndices(items, series) {
  if (!items || !items.length) return items || []
  return items.map((item) => {
    if (!item || item.sliceIndex == null) return item
    const fileIndex = item.fileIndex != null ? item.fileIndex : item.sliceIndex
    const stackIndex = fileIndexToStackIndex(fileIndex, series)
    return {
      ...item,
      fileIndex,
      sliceIndex: stackIndex,
      instanceNumber: stackIndex + 1
    }
  })
}

/** @deprecated 使用 sortImageIdsForViewer */
export async function sortImageIdsByDicomTags(imageIds, batchSize) {
  const r = await sortImageIdsForViewer(imageIds, batchSize)
  return r.imageIds
}
