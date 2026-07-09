import {
  readStoredEngine,
  readStoredSubEngine,
  writeStoredEngine,
  writeStoredSubEngine,
  normalizeActiveEngine,
  filterVisibleEngines,
  DEFAULT_ACTIVE_LESION_ENGINE
} from '@/utils/lesionEngines'

const ctTools = {
  state: {
    invert: false,
    hflip: false,
    vflip: false,
    pixelReplication: true,
    rotation: 0,

    isShowPatientInfo: true,
    isShowStudyInfo: false,
    isShowSeriesInfo: false,
    isShowInstancesInfo: false,
    isShowImageInfo: false,
    isShowEquipmentInfo: false,
    isShowUIDS: false,

    openStudy: true,

    // ── 病灶检测 ──
    lesionDetectTick: 0,
    lesionDetectLoading: false,
    lesionDetectPayload: null,
    lesionDetectQueue: [],
    lesionSeriesDialogVisible: false,
    lesionResultsByDicomId: {},
    lesionDetectLogs: [],
    lesionDetectProgress: 0,
    lesionDetectStage: '',
    lesionDetectStats: null,
    lesionLogPanelVisible: false,
    activeLesionTaskId: null,
    activeLesionTaskDicomId: null,
    lesionShowLogsTick: 0,
    lesionShowLogsPayload: null,
    lesionCancelTick: 0,
    lesionCancelPayload: null,
    lesionDetectEngine: readStoredEngine(),
    lesionDetectSubEngine: readStoredSubEngine(),
    lesionEngineCatalog: [],
    activeViewerSeriesDicomId: null,
  },

  mutations: {
    SET_INVERT: (state) => {
      state.invert = !state.invert
    },
    SET_HFLIP: (state) => {
      state.hflip = !state.hflip
    },
    SET_VFLIP: (state) => {
      state.vflip = !state.vflip
    },
    SET_PIXEL_REPLICATION: (state) => {
      state.pixelReplication = !state.pixelReplication
    },

    SET_IS_SHOW_PATIENT_INFO: (state) => {
      state.isShowPatientInfo = !state.isShowPatientInfo
      state.isShowStudyInfo = false
      state.isShowSeriesInfo = false
      state.isShowInstancesInfo = false
      state.isShowImageInfo = false
      state.isShowEquipmentInfo = false
      state.isShowUIDS = false
    },
    SET_IS_SHOW_STUDY_INFO: (state) => {
      state.isShowStudyInfo = !state.isShowStudyInfo
      state.isShowPatientInfo = false
      state.isShowSeriesInfo = false
      state.isShowInstancesInfo = false
      state.isShowImageInfo = false
      state.isShowEquipmentInfo = false
      state.isShowUIDS = false
    },
    SET_IS_SHOW_SERIES_INFO: (state) => {
      state.isShowSeriesInfo = !state.isShowSeriesInfo
      state.isShowPatientInfo = false
      state.isShowStudyInfo = false
      state.isShowInstancesInfo = false
      state.isShowImageInfo = false
      state.isShowEquipmentInfo = false
      state.isShowUIDS = false
    },
    SET_IS_SHOW_INSTANCES_INFO: (state) => {
      state.isShowInstancesInfo = !state.isShowInstancesInfo
      state.isShowPatientInfo = false
      state.isShowStudyInfo = false
      state.isShowSeriesInfo = false
      state.isShowImageInfo = false
      state.isShowEquipmentInfo = false
      state.isShowUIDS = false
    },
    SET_IS_SHOW_IMAGE_INFO: (state) => {
      state.isShowImageInfo = !state.isShowImageInfo
      state.isShowPatientInfo = false
      state.isShowStudyInfo = false
      state.isShowSeriesInfo = false
      state.isShowInstancesInfo = false
      state.isShowEquipmentInfo = false
      state.isShowUIDS = false
    },
    SET_IS_SHOW_EQUIPMENT_INFO: (state) => {
      state.isShowEquipmentInfo = !state.isShowEquipmentInfo
      state.isShowPatientInfo = false
      state.isShowStudyInfo = false
      state.isShowSeriesInfo = false
      state.isShowInstancesInfo = false
      state.isShowImageInfo = false
      state.isShowUIDS = false
    },
    SET_IS_SHOW_UIDS_INFO: (state) => {
      state.isShowUIDS = !state.isShowUIDS
      state.isShowPatientInfo = false
      state.isShowStudyInfo = false
      state.isShowSeriesInfo = false
      state.isShowInstancesInfo = false
      state.isShowImageInfo = false
      state.isShowEquipmentInfo = false
    },

    SET_OPEN_STUDY: (state) => {
      state.openStudy = !state.openStudy
    },
    SET_DEFAULT_STUDY: (state) => {
      state.openStudy = true
    },

    // ── 病灶检测 mutations ──
    SET_LESION_DETECT_ENGINE(state, engine) {
      const value = normalizeActiveEngine(engine, state.lesionEngineCatalog)
      state.lesionDetectEngine = value
      writeStoredEngine(value)
    },
    SET_LESION_DETECT_SUB_ENGINE(state, subEngine) {
      const value = subEngine || 'auto'
      state.lesionDetectSubEngine = value
      writeStoredSubEngine(value)
    },
    SET_LESION_ENGINE_CATALOG(state, list) {
      const catalog = filterVisibleEngines(Array.isArray(list) ? list : [])
      state.lesionEngineCatalog = catalog
      state.lesionDetectEngine = normalizeActiveEngine(state.lesionDetectEngine, catalog)
      writeStoredEngine(state.lesionDetectEngine)
    },
    APPEND_LESION_DETECT_LOG(state, log) {
      state.lesionDetectLogs = [...state.lesionDetectLogs, log]
    },
    REPLACE_LESION_DETECT_LOGS(state, logs) {
      state.lesionDetectLogs = Array.isArray(logs) ? [...logs] : []
    },
    SET_ACTIVE_LESION_TASK(state, payload) {
      if (!payload) {
        state.activeLesionTaskId = null
        state.activeLesionTaskDicomId = null
        return
      }
      state.activeLesionTaskId = payload.taskId || null
      state.activeLesionTaskDicomId = payload.dicomId != null ? String(payload.dicomId) : null
    },
    REQUEST_LESION_SHOW_LOGS(state, payload) {
      state.lesionShowLogsPayload = payload || null
      state.lesionShowLogsTick += 1
    },
    REQUEST_LESION_CANCEL(state, payload) {
      state.lesionCancelPayload = payload || null
      state.lesionCancelTick += 1
    },
    SET_LESION_DETECT_PROGRESS(state, payload) {
      if (payload.percent != null) state.lesionDetectProgress = payload.percent
      if (payload.stage != null) state.lesionDetectStage = payload.stage
    },
    SET_LESION_DETECT_STATS(state, stats) {
      state.lesionDetectStats = stats
    },
    RESET_LESION_DETECT_LOGS(state) {
      state.lesionDetectLogs = []
      state.lesionDetectProgress = 0
      state.lesionDetectStage = ''
      state.lesionDetectStats = null
    },
    SET_LESION_LOG_PANEL(state, visible) {
      state.lesionLogPanelVisible = visible
    },
    REQUEST_LESION_DETECT(state, payload) {
      if (!state.lesionDetectQueue) state.lesionDetectQueue = []
      state.lesionDetectQueue.push(payload || null)
      state.lesionDetectPayload = payload || null
      state.lesionDetectTick += 1
    },
    DRAIN_LESION_DETECT_QUEUE(state) {
      state.lesionDetectQueue = []
      state.lesionDetectPayload = null
    },
    CLEAR_LESION_DETECT_QUEUE(state) {
      state.lesionDetectQueue = []
    },
    CLEAR_LESION_DETECT_PAYLOAD(state) {
      state.lesionDetectPayload = null
    },
    SET_LESION_DETECT_LOADING(state, loading) {
      state.lesionDetectLoading = !!loading
    },
    SET_LESION_RESULT(state, { dicomId, result }) {
      if (dicomId == null) return
      state.lesionResultsByDicomId = {
        ...state.lesionResultsByDicomId,
        [String(dicomId)]: result
      }
    },
    SET_LESION_SERIES_DIALOG(state, visible) {
      state.lesionSeriesDialogVisible = !!visible
    },
    SET_ACTIVE_VIEWER_SERIES(state, dicomId) {
      state.activeViewerSeriesDicomId = dicomId != null ? String(dicomId) : null
    },
  },

  actions: {
    changeViewPort({ commit }, name) {
      commit(name.toString())
    },
    changeShowInfo({ commit }, switchInfo) {
      commit(switchInfo.toString())
    },
    openStudy({ commit }) {
      commit('SET_OPEN_STUDY')
    },
    setDefaultStudy({ commit }) {
      commit('SET_DEFAULT_STUDY')
    },

    // ── 病灶检测 actions ──
    setLesionDetectEngine({ commit }, engine) {
      commit('SET_LESION_DETECT_ENGINE', engine)
    },
    setLesionDetectSubEngine({ commit }, subEngine) {
      commit('SET_LESION_DETECT_SUB_ENGINE', subEngine)
    },
    loadLesionEngineCatalog({ commit }, list) {
      commit('SET_LESION_ENGINE_CATALOG', list)
    },
    requestLesionDetect({ commit }) {
      commit('SET_LESION_SERIES_DIALOG', true)
    },
    requestLesionDetectCurrentSlice({ commit, state }) {
      commit('REQUEST_LESION_DETECT', {
        action: 'detect-current-slice',
        detectEngine: state.lesionDetectEngine || DEFAULT_ACTIVE_LESION_ENGINE,
        detectSubEngine: state.lesionDetectSubEngine || 'auto'
      })
    },
    startLesionDetectForSeries({ commit, state }, item) {
      commit('REQUEST_LESION_DETECT', {
        action: 'detect',
        dicomId: item.dicomId,
        studyUid: item.studyUid,
        series: item.series,
        bodyPart: item.bodyPart,
        imageCount: item.imageCount,
        detectEngine: item.detectEngine || state.lesionDetectEngine || DEFAULT_ACTIVE_LESION_ENGINE,
        detectSubEngine: item.detectSubEngine || state.lesionDetectSubEngine || 'auto',
        enhancedSeriesUid: item.enhancedSeriesUid || null,
        enhancedImageCount: item.enhancedImageCount || null
      })
    },
    openLesionDetectLogs({ commit }, payload) {
      commit('REQUEST_LESION_SHOW_LOGS', payload || null)
    },
    cancelLesionDetectTask({ commit }, payload) {
      commit('REQUEST_LESION_CANCEL', payload || null)
    },
    viewSeriesInViewer({ commit }, item) {
      commit('SET_LESION_SERIES_DIALOG', false)
      commit('REQUEST_LESION_DETECT', {
        action: 'view-series',
        dicomId: item.dicomId,
        series: item.series
      })
    },
  }
}

export default ctTools
