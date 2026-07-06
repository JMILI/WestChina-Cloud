import { stripImageIdsFromStudySeriesList } from '@/utils/studyImageIds'
import persistedState from 'vuex-persistedstate'

function createSafeStorage(storage) {
  return {
    getItem(key) {
      return storage.getItem(key)
    },
    setItem(key, value) {
      try {
        storage.setItem(key, value)
      } catch (err) {
        if (err && err.name === 'QuotaExceededError') {
          console.warn('[vuex] storage quota exceeded, skip persist')
          try {
            storage.removeItem(key)
          } catch (e) {
            // ignore
          }
        } else {
          throw err
        }
      }
    },
    removeItem(key) {
      storage.removeItem(key)
    }
  }
}

/** Only persist small session fields; imageIds / heatmaps stay in memory. */
export function persistReducer(state) {
  const ctTools = state.ctTools || {}
  return {
    app: state.app,
    user: state.user,
    tagsView: state.tagsView,
    permission: state.permission,
    settings: state.settings,
    ctPatientInfo: {
      patCardId: state.ctPatientInfo && state.ctPatientInfo.patCardId,
      patName: state.ctPatientInfo && state.ctPatientInfo.patName,
      patPhone: state.ctPatientInfo && state.ctPatientInfo.patPhone,
      studySeriesList: stripImageIdsFromStudySeriesList(
        state.ctPatientInfo && state.ctPatientInfo.studySeriesList
      )
    },
    ctTools: {
      invert: ctTools.invert,
      hflip: ctTools.hflip,
      vflip: ctTools.vflip,
      pixelReplication: ctTools.pixelReplication,
      rotation: ctTools.rotation,
      isShowPatientInfo: ctTools.isShowPatientInfo,
      isShowStudyInfo: ctTools.isShowStudyInfo,
      isShowSeriesInfo: ctTools.isShowSeriesInfo,
      isShowInstancesInfo: ctTools.isShowInstancesInfo,
      isShowImageInfo: ctTools.isShowImageInfo,
      isShowEquipmentInfo: ctTools.isShowEquipmentInfo,
      isShowUIDS: ctTools.isShowUIDS,
      openStudy: ctTools.openStudy,
      lesionDetectEngine: ctTools.lesionDetectEngine,
      lesionDetectSubEngine: ctTools.lesionDetectSubEngine,
      lesionLogPanelVisible: ctTools.lesionLogPanelVisible
    },
    dicom: state.dicom,
    makerImage: {
      makerOfPatCardId: state.makerImage && state.makerImage.makerOfPatCardId,
      makerImageInitInfo: state.makerImage && state.makerImage.makerImageInitInfo
    },
    makerToolsOfMe: state.makerToolsOfMe,
    aiLesion: state.aiLesion
  }
}

export function createPersistPlugin() {
  const storage = createSafeStorage(window.sessionStorage)
  try {
    window.sessionStorage.removeItem('vuex')
    window.localStorage.removeItem('vuex')
  } catch (e) {
    // ignore
  }
  return persistedState({
    key: 'vuex-v2',
    storage,
    reducer: persistReducer
  })
}
