import { delAiLesion } from '@/api/ct/aiLesion'
import { delFolderFiles } from '@/api/ct/ctFileUpload'
import { aiSeriesFolderFromPath } from '@/utils/aiLesionSeries'

export function delAiLesionAndImages(ids, aiSeriesPaths) {
  const folders = (aiSeriesPaths || [])
    .map((path) => aiSeriesFolderFromPath(path))
    .filter(Boolean)

  const deleteFiles = folders.length
    ? delFolderFiles(folders)
    : Promise.resolve()

  return deleteFiles.then(() => delAiLesion(ids))
}
