import * as cornerstone from 'cornerstone-core'

const THUMB_DECODE_ERROR = /frame exceeds size of pixelData/i

export function isThumbnailDecodeError(err) {
  if (!err) return false
  const msg = err.message || String(err)
  return THUMB_DECODE_ERROR.test(msg)
}

/** Prefer middle slice; scouts/localizers at index 0 often fail to decode. */
export function pickThumbnailCandidates(imageIds) {
  if (!imageIds || !imageIds.length) return []
  const len = imageIds.length
  const indices = new Set([
    Math.floor(len / 2),
    0,
    len > 1 ? len - 1 : 0
  ])
  if (len > 8) {
    indices.add(Math.floor(len / 4))
    indices.add(Math.floor((3 * len) / 4))
  }
  return Array.from(indices)
    .filter(i => i >= 0 && i < len)
    .map(i => imageIds[i])
}

export async function loadCornerstoneThumbnail(el, imageIds, options = {}) {
  const candidates = options.ordered
    ? (imageIds || []).filter(Boolean)
    : pickThumbnailCandidates(imageIds)
  let lastErr = null
  for (const imageId of candidates) {
    try {
      const image = await Promise.resolve(cornerstone.loadImage(imageId))
      cornerstone.displayImage(el, image)
      return imageId
    } catch (err) {
      lastErr = err
    }
  }
  throw lastErr || new Error('thumbnail load failed')
}

let rejectionHandlerInstalled = false

/** Suppress benign DICOM decode errors from wado worker promises. */
export function installThumbnailRejectionHandler() {
  if (rejectionHandlerInstalled || typeof window === 'undefined') return
  rejectionHandlerInstalled = true
  window.addEventListener('unhandledrejection', event => {
    if (isThumbnailDecodeError(event.reason)) {
      event.preventDefault()
    }
  })
}
