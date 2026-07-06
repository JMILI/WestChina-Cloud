import { minioUrl } from '@/settings'

export function buildSeriesImageIds(series, bucketName, dicomPrefix = 'wadouri:') {
  if (!series || !series.dicomCtPath || !series.dicomCtCount || !bucketName) return []
  const path = series.dicomCtPath.substring(0, series.dicomCtPath.lastIndexOf('/'))
  const ids = []
  for (let i = 1; i <= series.dicomCtCount; i++) {
    ids.push(`${dicomPrefix}${minioUrl}${bucketName}/${path}/${i}.dcm`)
  }
  return ids
}

export function stripImageIdsFromStudySeriesList(studySeriesList) {
  if (!studySeriesList || typeof studySeriesList !== 'object') return {}
  const out = {}
  for (const studyUid of Object.keys(studySeriesList)) {
    out[studyUid] = {}
    const study = studySeriesList[studyUid] || {}
    for (const seriesUid of Object.keys(study)) {
      const series = study[seriesUid]
      if (!series) continue
      const { imageIds, ...meta } = series
      out[studyUid][seriesUid] = meta
    }
  }
  return out
}

export function hydrateStudySeriesList(studySeriesList, bucketName, dicomPrefix = 'wadouri:') {
  if (!studySeriesList || typeof studySeriesList !== 'object') return {}
  const out = {}
  for (const studyUid of Object.keys(studySeriesList)) {
    out[studyUid] = {}
    const study = studySeriesList[studyUid] || {}
    for (const seriesUid of Object.keys(study)) {
      const series = { ...study[seriesUid] }
      if (!series.imageIds || !series.imageIds.length) {
        series.imageIds = buildSeriesImageIds(series, bucketName, dicomPrefix)
      }
      out[studyUid][seriesUid] = series
    }
  }
  return out
}

export function studySeriesNeedsImageIds(studySeriesList) {
  if (!studySeriesList || typeof studySeriesList !== 'object') return false
  for (const studyUid of Object.keys(studySeriesList)) {
    const study = studySeriesList[studyUid] || {}
    for (const seriesUid of Object.keys(study)) {
      const series = study[seriesUid]
      if (series && (!series.imageIds || !series.imageIds.length) && series.dicomCtPath) {
        return true
      }
    }
  }
  return false
}
