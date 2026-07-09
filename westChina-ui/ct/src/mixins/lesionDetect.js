import { streamDetectChestLesion } from '@/utils/lesionDetectStream'
import {
  submitDetectChestLesionTask,
  queryDetectChestLesionTask,
  cancelDetectChestLesionTask
} from '@/api/ct/ai'
import {
  clearLesionOverlays,
  findSeriesMeta,
  formatDisclaimer,
  getImageInstanceUid,
  getSyncedStackIndex,
  isChestBodyPart,
  renderLesionOverlays,
  syncCornerstoneStackState
} from '@/utils/lesionDetect'
import { buildLesionResultPayload } from '@/utils/aiLesionSeries'
import {
  fileIndexToStackIndex,
  stackIndexToFileIndex,
  mapLesionsToStackIndices
} from '@/utils/dicomSeriesOrder'
import { engineSupportsMode, getEngineLabel, DEFAULT_ACTIVE_LESION_ENGINE } from '@/utils/lesionEngines'
import { saveAiLesionResult } from '@/api/ct/aiLesion'
import * as cornerstone from 'cornerstone-core'

function formatLogTime() {
  const d = new Date()
  const pad = (n) => String(n).padStart(2, '0')
  return `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}

function formatUserError(message) {
  if (!message) return '病灶识别失败，请稍后重试'
  if (message.includes('NullPointerException')) {
    return '后端服务内部错误（登录上下文丢失），请联系管理员查看 ct 日志'
  }
  if (message.includes('未收到识别结果')) return message
  return message
}

function inferColorKey(lesion) {
  if (lesion.colorKey) return lesion.colorKey
  const dc = lesion.detectionClass
  if (dc === 'mixed_ggo') return 'mixed'
  if (dc === 'ggo') return 'ggo'
  if (dc === 'calcified') return 'calcified'
  if (dc === 'solid' || dc === 'solid_suspicious') return 'solid'
  if (lesion.subType === 'mixedGGO') return 'mixed'
  if (lesion.subType === 'pureGGO' || lesion.type === '磨玻璃结节') return 'ggo'
  if (lesion.subType === 'calcified' || lesion.type === '高密度结节') return 'calcified'
  if (lesion.subType === 'solid' || lesion.type === '肺结节') return 'solid'
  return 'unknown'
}

function inferMarkerType(lesion) {
  if (lesion.markerType) return lesion.markerType
  const ck = inferColorKey(lesion)
  if (ck === 'solid') return 'circle'
  if (ck === 'calcified') return 'diamond'
  if (ck === 'mixed') return 'contour+circle'
  return 'contour'
}

function enrichLesionsForViewer(lesions) {
  return (lesions || []).map((l, i) => ({
    ...l,
    id: l.id || `L${i + 1}`,
    markerVisible: l.markerVisible !== false,
    colorKey: inferColorKey(l),
    markerType: inferMarkerType(l),
    detectionConfidence: l.detectionConfidence != null ? l.detectionConfidence : l.confidence,
    classificationConfidence: l.classificationConfidence != null ? l.classificationConfidence : undefined,
    detectionClassLabel: l.detectionClassLabel || l.label || l.type || undefined,
    instanceNumber: l.instanceNumber != null
      ? l.instanceNumber
      : (l.sliceIndex != null ? l.sliceIndex + 1 : null)
  }))
}

function enrichGgoForViewer(regions) {
  return (regions || []).map((r, i) => ({
    ...r,
    id: r.id || `GGO${i + 1}`,
    label: r.label || '疑似磨玻璃区域',
    markerVisible: r.markerVisible !== false
  }))
}

export default {
  data() {
    return {
      aiLesionList: [],
      aiLesionPanelVisible: false,
      aiLesionDisclaimer: '',
      aiEngine: '',
      activeLesionDicomId: null,
      lesionOverlayMode: null,
      sliceLesionCache: {},
      aiOverlayType: 'bbox',
      aiHeatmapData: null,
      aiHeatmapSliceIndex: null,
      aiScreeningData: null,
      aiGgoRegions: [],
      aiInstanceUid: null,
      aiDetectMode: 'series',
      aiSliceIndex: null
    }
  },
  computed: {
    lesionDetectTick() {
      return this.$store.getters.lesionDetectTick
    },
    lesionDetectLoading() {
      return this.$store.getters.lesionDetectLoading
    },
    lesionResultsByDicomId() {
      return this.$store.getters.lesionResultsByDicomId
    },
    lesionLogPanelVisible() {
      return this.$store.getters.lesionLogPanelVisible
    },
    lesionDetectLogs() {
      return this.$store.getters.lesionDetectLogs
    },
    lesionDetectProgress() {
      return this.$store.getters.lesionDetectProgress
    },
    lesionDetectStage() {
      return this.$store.getters.lesionDetectStage
    },
    lesionDetectEngine() {
      return this.$store.getters.lesionDetectEngine
    },
    lesionDetectStats() {
      return this.$store.getters.lesionDetectStats
    },
    lesionShowLogsTick() {
      return this.$store.getters.lesionShowLogsTick
    },
    lesionCancelTick() {
      return this.$store.getters.lesionCancelTick
    }
  },
  watch: {
    lesionDetectTick() {
      this.handleLesionAction()
    },
    lesionShowLogsTick() {
      this.handleShowLogsRequest()
    },
    lesionCancelTick() {
      this.handleCancelRequest()
    }
  },
  mounted() {
    this.startLesionTaskPoller()
  },
  beforeDestroy() {
    this.stopLesionTaskPoller()
  },
  methods: {
    getLesionViewerContext() {
      const canvas = this.$refs.canvas
      if (canvas && this.canvasStack) {
        getSyncedStackIndex(canvas, this.canvasStack)
      }
      return {
        canvas,
        stack: this.canvasStack,
        bodyPart: this.seriesInfo && this.seriesInfo.bodyPart,
        studyUid: this.UIDS && this.UIDS.studyUID,
        seriesUid: this.UIDS && this.UIDS.seriesUID,
        activeSeriesDicomId: this.activeSeriesDicomId
      }
    },
    async refreshLesionCanvas() {
      if (typeof this.displayOneCanvasImage === 'function') {
        return this.displayOneCanvasImage()
      }
      if (this.inEffectCanvas === 2 && typeof this.displayCanvas2 === 'function') {
        return this.displayCanvas2()
      }
      if (typeof this.displayCanvas1 === 'function') {
        return this.displayCanvas1()
      }
    },
    async switchToSeriesForLesion(series) {
      if (!series) return
      if (this.inEffectCanvas !== undefined) {
        this.inEffectCanvas = 1
      }
      if (String(this.activeSeriesDicomId) === String(series.dicomId) &&
          this.canvasStack1 && this.canvasStack1.imageIds === series.imageIds) {
        return
      }
      if (typeof this.changeCurrentImagesIds === 'function') {
        this.changeCurrentImagesIds(series, { fromLesion: true })
      }
      await this.$nextTick()
    },
    handleLesionAction() {
      let payloads = [...(this.$store.state.ctTools.lesionDetectQueue || [])]
      if (payloads.length) {
        this.$store.commit('DRAIN_LESION_DETECT_QUEUE')
      } else {
        const single = this.$store.getters.lesionDetectPayload
        if (single && single.action) {
          payloads = [single]
          this.$store.commit('CLEAR_LESION_DETECT_PAYLOAD')
        }
      }

      payloads.forEach((payload) => {
        if (!payload || !payload.action) return
        const action = payload.action
        if (action === 'view-series') {
          this.switchToSeriesForLesion(payload.series)
          return
        }
        if (action === 'view') {
          this.viewLesionResultForSeries(payload)
          return
        }
        if (action === 'detect') {
          this.runLesionDetectForSeries(payload)
          return
        }
        if (action === 'detect-current-slice') {
          this.runLesionDetectForCurrentSlice(payload)
        }
      })
    },
    appendDetectLog(message, level = 'info') {
      this.$store.commit('APPEND_LESION_DETECT_LOG', {
        time: formatLogTime(),
        message,
        level
      })
    },
    startLesionTaskPoller() {
      if (this._lesionTaskPoller) return
      this._lesionTaskPoller = setInterval(() => {
        this.pollAllActiveLesionTasks()
      }, 1000)
    },
    stopLesionTaskPoller() {
      if (this._lesionTaskPoller) {
        clearInterval(this._lesionTaskPoller)
        this._lesionTaskPoller = null
      }
    },
    pollAllActiveLesionTasks() {
      const results = this.$store.getters.lesionResultsByDicomId || {}
      const now = Date.now()
      Object.keys(results).forEach((dicomId) => {
        const row = results[dicomId]
        if (!row || row.status !== 'detecting') return
        if (!row.taskId) {
          const since = row._detectingSince || 0
          if (!since) {
            this.$store.commit('SET_LESION_RESULT', {
              dicomId,
              result: { ...row, _detectingSince: now }
            })
            return
          }
          if (now - since > 90000) {
            this.$store.commit('SET_LESION_RESULT', {
              dicomId,
              result: {
                status: 'error',
                errorMsg: '任务未能启动，请重试'
              }
            })
          }
          return
        }
        queryDetectChestLesionTask(row.taskId)
          .then((res) => {
            if (res && res.code === 200 && res.data) {
              this.syncTaskStatusFromPoll(res.data, dicomId)
            }
          })
          .catch(() => {})
      })
    },
    async submitLesionDetectTask(req, dicomId) {
      const submitRes = await submitDetectChestLesionTask(req)
      if (!submitRes || submitRes.code !== 200 || !submitRes.data) {
        throw new Error((submitRes && submitRes.msg) || '提交识别任务失败')
      }
      const taskId = submitRes.data
      this.$store.commit('SET_LESION_RESULT', {
        dicomId,
        result: {
          status: 'detecting',
          progress: 0,
          stage: 'queued',
          taskId,
          _detectingSince: Date.now()
        }
      })
      return taskId
    },
    async waitLesionDetectTask(taskId, dicomId) {
      const startAt = Date.now()
      const timeoutMs = 7200000
      const intervalMs = 1000
      while (Date.now() - startAt < timeoutMs) {
        // eslint-disable-next-line no-await-in-loop
        const statusRes = await queryDetectChestLesionTask(taskId)
        if (!statusRes || statusRes.code !== 200 || !statusRes.data) {
          throw new Error((statusRes && statusRes.msg) || '查询识别任务状态失败')
        }
        const statusData = statusRes.data
        this.syncTaskStatusFromPoll(statusData, dicomId)
        const status = statusData.status
        if (status === 'DONE') {
          return statusData.result
        }
        if (status === 'FAILED') {
          throw new Error(statusData.message || '任务执行失败')
        }
        if (status === 'CANCELLED') {
          return null
        }
        // eslint-disable-next-line no-await-in-loop
        await new Promise((resolve) => setTimeout(resolve, intervalMs))
      }
      throw new Error('识别任务超时，请稍后查看结果')
    },
    async runDetectByTask(req, options = {}) {
      const dicomId = options.dicomId
      const taskId = await this.submitLesionDetectTask(req, dicomId)
      this.$store.commit('SET_ACTIVE_LESION_TASK', { taskId, dicomId })
      try {
        const result = await this.waitLesionDetectTask(taskId, dicomId)
        this.$store.commit('SET_ACTIVE_LESION_TASK', null)
        return result
      } catch (err) {
        this.$store.commit('SET_ACTIVE_LESION_TASK', null)
        throw err
      }
    },
    syncTaskStatusFromPoll(statusData, dicomId) {
      if (!statusData) return
      const taskId = statusData.taskId
      const activeTaskId = this.$store.getters.activeLesionTaskId
      const activeDicomId = this.$store.getters.activeLesionTaskDicomId
      const panelVisible = this.$store.getters.lesionLogPanelVisible
      const backendLogs = Array.isArray(statusData.logs) ? statusData.logs : []
      const progress = statusData.progress != null ? Number(statusData.progress) : 0
      let stage = statusData.stage || ''
      if (statusData.status === 'PENDING') {
        stage = 'queued'
      } else if (statusData.status === 'RUNNING' && (!stage || stage === 'queued')) {
        stage = 'connect'
      }

      if (dicomId != null && (statusData.status === 'RUNNING' || statusData.status === 'PENDING')) {
        const prev = this.lesionResultsByDicomId[String(dicomId)] || {}
        this.$store.commit('SET_LESION_RESULT', {
          dicomId,
          result: {
            status: 'detecting',
            progress,
            stage,
            taskId: taskId || prev.taskId,
            queueMessage: statusData.message || prev.queueMessage || '',
            detectLogs: backendLogs.length ? backendLogs : (prev.detectLogs || [])
          }
        })
      }

      if (dicomId != null && statusData.status === 'FAILED') {
        this.$store.commit('SET_LESION_RESULT', {
          dicomId,
          result: {
            status: 'error',
            errorMsg: statusData.message || '识别失败',
            taskId
          }
        })
      }

      if (dicomId != null && statusData.status === 'CANCELLED') {
        this.$store.commit('SET_LESION_RESULT', {
          dicomId,
          result: {
            status: 'cancelled',
            taskId,
            errorMsg: statusData.message || '任务已取消'
          }
        })
      }

      const viewingThisTask = panelVisible && (
        (taskId && activeTaskId && taskId === activeTaskId) ||
        (dicomId != null && activeDicomId && String(dicomId) === String(activeDicomId))
      )

      if (viewingThisTask) {
        if (taskId && taskId !== activeTaskId) {
          this.$store.commit('SET_ACTIVE_LESION_TASK', { taskId, dicomId })
        }
        if (backendLogs.length > 0) {
          this.$store.commit('REPLACE_LESION_DETECT_LOGS', backendLogs)
        }
        this.$store.commit('SET_LESION_DETECT_PROGRESS', { percent: progress, stage })
        if (statusData.stats) {
          this.$store.commit('SET_LESION_DETECT_STATS', statusData.stats)
        }
        const running = statusData.status === 'RUNNING' || statusData.status === 'PENDING'
        this.$store.commit('SET_LESION_DETECT_LOADING', running)
        if (statusData.status === 'CANCELLED') {
          this.$store.commit('SET_LESION_DETECT_LOADING', false)
        }
      }
    },
    async openLesionLogPanelForTask({ taskId, dicomId }) {
      this.$store.commit('SET_ACTIVE_LESION_TASK', { taskId: taskId || null, dicomId })
      const row = (this.$store.getters.lesionResultsByDicomId || {})[String(dicomId)]
      if (row && Array.isArray(row.detectLogs) && row.detectLogs.length) {
        this.$store.commit('REPLACE_LESION_DETECT_LOGS', row.detectLogs)
        this.$store.commit('SET_LESION_DETECT_PROGRESS', {
          percent: row.progress != null ? row.progress : 0,
          stage: row.stage || ''
        })
      } else {
        this.$store.commit('RESET_LESION_DETECT_LOGS')
        this.$store.commit('SET_LESION_DETECT_PROGRESS', { percent: 2, stage: 'queued' })
      }
      this.$store.commit('SET_LESION_DETECT_STATS', null)
      if (taskId) {
        try {
          const statusRes = await queryDetectChestLesionTask(taskId)
          if (statusRes && statusRes.code === 200 && statusRes.data) {
            this.syncTaskStatusFromPoll(statusRes.data, dicomId)
          }
        } catch (e) {
          // 打开日志面板时拉取失败不影响展示
        }
      }
      this.$store.commit('SET_LESION_LOG_PANEL', true)
    },
    handleShowLogsRequest() {
      const payload = this.$store.state.ctTools.lesionShowLogsPayload
      if (!payload) return
      this.openLesionLogPanelForTask(payload)
    },
    async handleCancelRequest() {
      const payload = this.$store.state.ctTools.lesionCancelPayload
      if (!payload || !payload.taskId) return
      const { taskId, dicomId } = payload
      try {
        const res = await cancelDetectChestLesionTask(taskId)
        if (res && res.code === 200) {
          this.$message.success(res.msg || '任务已取消')
          const statusRes = await queryDetectChestLesionTask(taskId)
          if (statusRes && statusRes.code === 200 && statusRes.data) {
            this.syncTaskStatusFromPoll(statusRes.data, dicomId)
          }
          if (this.$store.getters.activeLesionTaskId === taskId) {
            this.$store.commit('SET_ACTIVE_LESION_TASK', null)
            this.$store.commit('SET_LESION_DETECT_LOADING', false)
          }
        } else {
          this.$message.warning((res && res.msg) || '取消失败')
        }
      } catch (e) {
        this.$message.error('取消任务失败')
      }
    },
    handleStreamEvent(event, dicomId, detectLogs) {
      if (!event || !event.type) return null
      if (event.type === 'log') {
        this.appendDetectLog(event.message, event.level || 'info')
        if (event.progress != null) {
          this.$store.commit('SET_LESION_DETECT_PROGRESS', {
            percent: event.progress,
            stage: event.stage
          })
        }
      } else if (event.type === 'progress') {
        this.$store.commit('SET_LESION_DETECT_PROGRESS', {
          percent: event.percent,
          stage: event.stage
        })
        if (event.message) {
          this.appendDetectLog(event.message, 'info')
        }
      } else if (event.type === 'stats') {
        const stats = {
          lesionCount: event.lesionCount,
          candidates: event.candidates,
          lungVoxels: event.lungVoxels
        }
        this.$store.commit('SET_LESION_DETECT_STATS', stats)
        this.appendDetectLog(
          `统计：候选 ${event.candidates} 个，检出病灶 ${event.lesionCount} 处`,
          'success'
        )
      } else if (event.type === 'warn') {
        this.appendDetectLog(event.message || event.code || '警告', 'warn')
      } else if (event.type === 'step_start') {
        const label = event.label || event.step_id || '处理中'
        this.appendDetectLog(`▶ ${label}`, 'info')
      } else if (event.type === 'step_end') {
        const ms = event.duration_ms != null ? ` ${(event.duration_ms / 1000).toFixed(1)}s` : ''
        const m = event.metrics || {}
        let detail = ''
        if (m.lesion_count != null) detail = `，病灶 ${m.lesion_count}`
        else if (m.fusion_filtered != null) detail = `，保留 ${m.fusion_filtered}`
        else if (m.candidates != null) detail = `，候选 ${m.candidates}`
        this.appendDetectLog(`✓ ${event.step_id || '步骤'}${ms}${detail}`, 'success')
      } else if (event.type === 'error') {
        const msg = formatUserError(event.message || '识别失败')
        this.appendDetectLog(msg, 'error')
        throw new Error(msg)
      } else if (event.type === 'result') {
        return event.data
      }
      return null
    },
    sliceLesionCacheKey(dicomId, sliceIndex) {
      return `${dicomId}:${sliceIndex}`
    },
    resolveCurrentSeriesMeta() {
      const dicomId = this.activeSeriesDicomId
      if (dicomId == null) return null
      const studyList = this.$store.getters.studySeriesList
      const found = findSeriesMeta(studyList, dicomId)
      if (!found) return null
      return {
        dicomId: String(dicomId),
        studyUid: found.studyUid,
        series: found.series,
        bodyPart: (found.series && found.series.dicomCtBody) || (this.seriesInfo && this.seriesInfo.bodyPart) || '',
        imageCount: (found.series && found.series.imageIds && found.series.imageIds.length) ||
          Number((found.series && found.series.dicomCtCount) || 0),
        seriesUid: found.series && found.series.dicomCtSeriesUid
      }
    },
    async runLesionDetectForCurrentSlice(payload = {}) {
      const meta = this.resolveCurrentSeriesMeta()
      if (!meta) {
        this.$message.warning('请先选择并加载 CT 序列')
        return
      }

      const { dicomId, studyUid, series, bodyPart, imageCount, seriesUid } = meta
      if (!isChestBodyPart(bodyPart)) {
        this.$message.warning(`当前序列检查部位为「${bodyPart || '未知'}」，不支持识别`)
        return
      }

      const ctx = this.getLesionViewerContext()
      if (!ctx.canvas || !ctx.stack || !ctx.stack.imageIds || !ctx.stack.imageIds.length) {
        this.$message.warning('当前层图像未加载，无法识别')
        return
      }

      const stackIndex = ctx.stack.currentImageIdIndex
      const fileIndex = stackIndexToFileIndex(stackIndex, series)
      const total = imageCount || ctx.stack.imageIds.length
      const currentImageId = ctx.stack.imageIds[stackIndex] || ctx.stack.currentImageId || null
      const instanceUid = getImageInstanceUid(ctx.canvas)
      const detectEngine = payload.detectEngine || this.$store.getters.lesionDetectEngine || DEFAULT_ACTIVE_LESION_ENGINE

      // 检查引擎是否支持当前层识别
      const catalog = this.$store.getters.lesionEngineCatalog
      if (!engineSupportsMode(detectEngine, 'single', catalog)) {
        this.$message.warning('当前引擎不支持当前层识别，请切换识别算法')
        return
      }

      // 单层识别：清除全序列叠加，避免与历史结果混显
      this.lesionOverlayMode = 'slice'
      this.activeLesionDicomId = String(dicomId)
      if (ctx.canvas) clearLesionOverlays(ctx.canvas)

      const req = {
        patCardId: this.$store.getters.patCardId,
        dicomId,
        studyUid,
        seriesUid,
        bodyPart,
        currentSliceIndex: stackIndex,
        sliceIndex: fileIndex,
        currentImageId,
        imageCount: total,
        detectMode: 'single',
        detect_mode: 'single',
        singleSlice: true,
        instanceUid,
        detectEngine,
        detectSubEngine: this.$store.getters.lesionDetectSubEngine || 'auto'
      }

      this.$store.commit('RESET_LESION_DETECT_LOGS')
      this.$store.commit('SET_LESION_LOG_PANEL', true)
      this.$store.commit('SET_LESION_DETECT_LOADING', true)
      this.$store.commit('SET_LESION_DETECT_PROGRESS', { percent: 3, stage: 'init' })
      const engineLabel = getEngineLabel(req.detectEngine, catalog)
      this.appendDetectLog(`[前端] 当前层识别：Instance ${stackIndex + 1}/${total}，算法：${engineLabel}`, 'info')
      if (instanceUid) {
        this.appendDetectLog(`[前端] Instance UID：${instanceUid}`, 'info')
      }
      this.appendDetectLog('[Java] 已提交单层识别任务…', 'info')

      let resultData = null
      try {
        resultData = await this.runDetectByTask(req, { dicomId })

        if (!resultData) {
          throw new Error('未收到识别结果')
        }

        const lesions = enrichLesionsForViewer(
          mapLesionsToStackIndices(resultData.lesions || [], series)
        )
        const overlayType = resultData.overlayType || 'bbox'
        this.aiOverlayType = overlayType
        this.aiHeatmapData = resultData.heatmap || null
        this.aiHeatmapSliceIndex = (resultData.meta && resultData.meta.sliceIndex != null)
          ? fileIndexToStackIndex(resultData.meta.sliceIndex, series)
          : stackIndex
        this.aiScreeningData = resultData.screening || null
        this.aiGgoRegions = enrichGgoForViewer(
          mapLesionsToStackIndices(resultData.ggoRegions || [], series)
        )
        this.aiInstanceUid = instanceUid
        this.aiDetectMode = 'single'
        this.aiSliceIndex = stackIndex
        const isHeatmap = overlayType === 'heatmap'
        const cacheKey = this.sliceLesionCacheKey(dicomId, stackIndex)
        const sliceResult = {
          status: lesions.length || isHeatmap ? 'done' : 'empty',
          lesions,
          lesionCount: lesions.length,
          disclaimer: resultData.disclaimer || 'AI 辅助结果仅供临床参考，不能替代医生诊断。',
          engine: resultData.engine || '',
          detectedAt: Date.now(),
          sliceIndex: stackIndex,
          instanceNumber: stackIndex + 1,
          detectMode: 'single',
          instanceUid,
          overlayType,
          heatmap: this.aiHeatmapData,
          heatmapSliceIndex: this.aiHeatmapSliceIndex,
          screening: this.aiScreeningData
        }
        this.$set(this.sliceLesionCache, cacheKey, sliceResult)

        this.lesionOverlayMode = 'slice'
        this.activeLesionDicomId = String(dicomId)
        this.aiLesionList = lesions
        this.aiLesionDisclaimer = sliceResult.disclaimer
        this.aiEngine = sliceResult.engine
        this.aiLesionPanelVisible = true
        this.syncLesionOverlaysForCurrentSlice()

        if (isHeatmap) {
          const conf = this.aiScreeningData && this.aiScreeningData.confidence != null
            ? (this.aiScreeningData.confidence * 100).toFixed(1)
            : null
          this.$message.success(
            conf != null
              ? `Instance ${stackIndex + 1} 筛查完成（${this.aiScreeningData.label || '倾向分析'} ${conf}%）`
              : `Instance ${stackIndex + 1} 筛查完成，已生成热力图`
          )
        } else if (!lesions.length) {
          const msg = (resultData.meta && resultData.meta.stats && resultData.meta.stats.message)
            || `Instance ${stackIndex + 1} 未检测到疑似病灶`
          this.$message.info(msg)
        } else {
          this.$message.success(`Instance ${stackIndex + 1} 识别完成，共 ${lesions.length} 处疑似病灶`)
        }

        await this.persistAiLesionResult(dicomId, resultData, req, {
          ...sliceResult,
          overlayType,
          heatmap: this.aiHeatmapData,
          screening: this.aiScreeningData,
          ggoRegions: this.aiGgoRegions,
          detectMode: 'single',
          sliceIndex: stackIndex,
          instanceUid,
          heatmapSliceIndex: this.aiHeatmapSliceIndex
        })
      } catch (e) {
        const msg = formatUserError((e && e.message) || '当前层识别失败，请稍后重试')
        this.$message.error(msg)
      } finally {
        this.$store.commit('SET_LESION_DETECT_LOADING', false)
      }
    },
    buildSeriesDetectRequest(payload) {
      const { series, studyUid, dicomId, bodyPart, imageCount, detectEngine, detectSubEngine,
        enhancedSeriesUid, enhancedImageCount } = payload
      const count = imageCount ||
        (series && series.imageIds && series.imageIds.length) ||
        Number(series && series.dicomCtCount) || 0
      const req = {
        patCardId: this.$store.getters.patCardId,
        dicomId,
        studyUid,
        seriesUid: series.dicomCtSeriesUid,
        bodyPart,
        currentSliceIndex: 0,
        sliceIndex: 0,
        imageCount: count,
        detectMode: 'series',
        detectEngine: detectEngine || this.$store.getters.lesionDetectEngine || DEFAULT_ACTIVE_LESION_ENGINE,
        detectSubEngine: detectSubEngine || this.$store.getters.lesionDetectSubEngine || 'auto'
      }
      if (enhancedSeriesUid) {
        req.enhancedSeriesUid = enhancedSeriesUid
        req.enhancedImageCount = enhancedImageCount || count
      }
      return req
    },
    async runLesionDetectForSeries(payload) {
      const { series, dicomId, bodyPart } = payload
      if (!isChestBodyPart(bodyPart)) {
        this.$message.warning(`序列检查部位为「${bodyPart || '未知'}」，不支持识别`)
        this.$store.commit('SET_LESION_RESULT', {
          dicomId,
          result: { status: 'error', errorMsg: '检查部位不支持' }
        })
        return
      }

      const catalog = this.$store.getters.lesionEngineCatalog
      const engine = payload.detectEngine || this.$store.getters.lesionDetectEngine || DEFAULT_ACTIVE_LESION_ENGINE
      if (!engineSupportsMode(engine, 'series', catalog)) {
        this.$message.warning('当前引擎不支持全序列识别，请切换识别算法')
        return
      }

      const existing = (this.$store.getters.lesionResultsByDicomId || {})[String(dicomId)]
      if (existing && existing.status === 'detecting') {
        this.$message.info('该序列已在识别队列中，请查看右侧日志面板')
        return
      }

      const req = this.buildSeriesDetectRequest(payload)
      const engineLabel = getEngineLabel(req.detectEngine, catalog)

      this.$store.commit('SET_LESION_RESULT', {
        dicomId,
        result: { status: 'detecting', progress: 0, stage: 'queued', taskId: null, _detectingSince: Date.now() }
      })
      const panelAlreadyOpen = this.$store.getters.lesionLogPanelVisible
      if (!panelAlreadyOpen) {
        this.$store.commit('RESET_LESION_DETECT_LOGS')
        this.$store.commit('SET_LESION_LOG_PANEL', true)
      }
      this.$store.commit('SET_LESION_DETECT_PROGRESS', { percent: 2, stage: 'queued' })
      this.$store.commit('SET_ACTIVE_LESION_TASK', { taskId: null, dicomId: String(dicomId) })
      this.$store.commit('SET_LESION_DETECT_LOADING', true)
      this.appendDetectLog(`[前端] 提交全序列识别：${engineLabel}`, 'info')

      let taskId = null
      try {
        taskId = await this.submitLesionDetectTask(req, dicomId)
        this.$store.commit('SET_ACTIVE_LESION_TASK', { taskId, dicomId: String(dicomId) })
        const statusRes = await queryDetectChestLesionTask(taskId)
        if (statusRes && statusRes.code === 200 && statusRes.data) {
          this.syncTaskStatusFromPoll(statusRes.data, dicomId)
        }
      } catch (submitErr) {
        const msg = formatUserError((submitErr && submitErr.message) || '提交识别任务失败')
        this.$store.commit('SET_LESION_RESULT', {
          dicomId,
          result: { status: 'error', errorMsg: msg }
        })
        this.$message.error(msg)
        this.$store.commit('SET_LESION_DETECT_LOADING', false)
        return
      }

      this.completeLesionDetectSeriesInBackground({
        req,
        dicomId,
        taskId,
        series,
        engineLabel
      })
    },
    async completeLesionDetectSeriesInBackground({ req, dicomId, taskId, series, engineLabel }) {
      let resultData = null
      try {
        resultData = await this.waitLesionDetectTask(taskId, dicomId)

        if (!resultData) {
          return
        }

        await this.switchToSeriesForLesion(series)
        const ctx = this.getLesionViewerContext()
        const seriesInstanceUid = (ctx.canvas && getImageInstanceUid(ctx.canvas)) || series.dicomCtSeriesUid

        const lesions = enrichLesionsForViewer(
          mapLesionsToStackIndices(resultData.lesions || [], series)
        )
        const overlayType = resultData.overlayType || 'bbox'
        this.aiOverlayType = overlayType
        this.aiHeatmapData = resultData.heatmap || null
        this.aiHeatmapSliceIndex = (resultData.meta && resultData.meta.sliceIndex != null)
          ? fileIndexToStackIndex(resultData.meta.sliceIndex, series)
          : 0
        this.aiScreeningData = resultData.screening || null
        this.aiGgoRegions = enrichGgoForViewer(
          mapLesionsToStackIndices(resultData.ggoRegions || [], series)
        )
        this.aiInstanceUid = seriesInstanceUid
        this.aiDetectMode = 'series'
        this.aiSliceIndex = req.sliceIndex
        const stats = (resultData.meta && resultData.meta.stats) || this.lesionDetectStats
        const result = {
          status: lesions.length || overlayType === 'heatmap' ? 'done' : 'empty',
          lesions,
          lesionCount: lesions.length,
          disclaimer: resultData.disclaimer || 'AI 辅助结果仅供临床参考，不能替代医生诊断。',
          engine: resultData.engine || '',
          detectedAt: Date.now(),
          detectLogs: [...this.lesionDetectLogs],
          stats,
          overlayType,
          heatmap: this.aiHeatmapData,
          heatmapSliceIndex: this.aiHeatmapSliceIndex,
          screening: this.aiScreeningData,
          ggoRegions: this.aiGgoRegions,
          detectMode: 'series',
          sliceIndex: req.sliceIndex,
          instanceUid: seriesInstanceUid,
          sourceDicomId: dicomId
        }
        this.$store.commit('SET_LESION_RESULT', { dicomId, result })
        this.lesionOverlayMode = 'series'
        this.applyLesionResultToViewer(dicomId)
        await this.persistAiLesionResult(dicomId, resultData, req, result)

        if (!lesions.length) {
          const msg = (resultData.meta && resultData.meta.stats && resultData.meta.stats.message)
            || (stats && stats.message)
            || '该序列未检测到疑似病灶'
          this.$message.info(msg)
        } else {
          this.$message.success(`识别完成，共 ${lesions.length} 处疑似病灶`)
        }
      } catch (e) {
        const msg = formatUserError((e && e.message) || '病灶识别失败，请稍后重试')
        this.$store.commit('SET_LESION_RESULT', {
          dicomId,
          result: {
            status: 'error',
            errorMsg: msg,
            taskId,
            detectLogs: [...this.lesionDetectLogs]
          }
        })
        this.$message.error(msg)
      } finally {
        const activeId = this.$store.getters.activeLesionTaskId
        const activeDicom = this.$store.getters.activeLesionTaskDicomId
        if (!activeId || String(activeDicom) === String(dicomId)) {
          this.$store.commit('SET_LESION_DETECT_LOADING', false)
        }
      }
    },
    viewLesionResultForSeries(payload) {
      const dicomId = payload.dicomId
      const cached = this.lesionResultsByDicomId[String(dicomId)]
      if (!cached || (cached.status !== 'done' && cached.status !== 'empty')) {
        this.$message.warning('该序列尚无识别结果')
        return
      }
      this.switchToSeriesForLesion(payload.series).then(() => {
        this.applyLesionResultToViewer(dicomId)
      })
    },
    applyLesionResultToViewer(dicomId) {
      const cached = this.lesionResultsByDicomId[String(dicomId)]
      if (!cached) return

      this.applyLesionOverlayState(cached, dicomId)

      const ctx = this.getLesionViewerContext()
      if (!ctx.canvas || !ctx.stack) return

      const meta = this.resolveCurrentSeriesMeta()
      const series = meta && meta.series
      const jumpSlice = this.resolveLesionJumpSlice(cached, series)
      if (jumpSlice != null && jumpSlice !== ctx.stack.currentImageIdIndex) {
        ctx.stack.currentImageIdIndex = Math.max(
          0,
          Math.min(jumpSlice, ctx.stack.imageIds.length - 1)
        )
        syncCornerstoneStackState(ctx.canvas, ctx.stack)
        this.refreshLesionCanvas().then(() => this.syncLesionOverlaysForCurrentSlice())
        return
      }
      this.syncLesionOverlaysForCurrentSlice()
    },
    applyLesionOverlayState(cached, dicomId) {
      this.activeLesionDicomId = String(dicomId)
      this.lesionOverlayMode = cached.detectMode === 'single' ? 'slice' : 'series'
      this.aiLesionList = cached.lesions || []
      this.aiLesionDisclaimer = formatDisclaimer(cached.disclaimer || '')
      this.aiEngine = cached.engine || ''
      this.aiOverlayType = cached.overlayType || 'bbox'
      this.aiHeatmapData = cached.heatmap || null
      this.aiHeatmapSliceIndex = cached.heatmapSliceIndex != null
        ? cached.heatmapSliceIndex
        : cached.sliceIndex
      this.aiScreeningData = cached.screening || null
      this.aiGgoRegions = cached.ggoRegions || []
      this.aiInstanceUid = cached.instanceUid || null
      this.aiDetectMode = cached.detectMode || 'series'
      this.aiSliceIndex = cached.sliceIndex != null
        ? cached.sliceIndex
        : cached.sourceSliceIndex
      this.aiLesionPanelVisible = true
    },
    resolveLesionJumpSlice(cached, series) {
      const mapIdx = (idx) => fileIndexToStackIndex(idx, series)
      if (cached.overlayType === 'heatmap') {
        const raw = cached.heatmapSliceIndex != null
          ? cached.heatmapSliceIndex
          : cached.sliceIndex
        return raw != null ? mapIdx(raw) : null
      }
      if (cached.lesions && cached.lesions.length) {
        const first = cached.lesions.find((l) => l.sliceIndex != null)
        return first ? first.sliceIndex : null
      }
      return cached.sliceIndex != null ? mapIdx(cached.sliceIndex) : null
    },
    onSeriesSwitchedForLesion(series, options = {}) {
      if (!series || options.fromLesion) return
      if (series.isAiLesionSeries) {
        this.applyLesionResultToViewer(String(series.dicomId))
        return
      }
      this.aiLesionPanelVisible = false
      this.aiLesionList = []
      this.activeLesionDicomId = null
      this.lesionOverlayMode = null
      const ctx = this.getLesionViewerContext()
      if (ctx.canvas) clearLesionOverlays(ctx.canvas)
    },
    async persistAiLesionResult(dicomId, resultData, req, result) {
      try {
        const lesionPayload = buildLesionResultPayload({
          ...result,
          detectMode: result.detectMode || req.detectMode || 'series',
          sliceIndex: result.sliceIndex != null ? result.sliceIndex : req.sliceIndex,
          instanceUid: result.instanceUid || req.instanceUid || this.aiInstanceUid
        })
        const detectMode = result.detectMode || req.detectMode || 'series'
        const sliceIndex = result.sliceIndex != null ? result.sliceIndex : req.sliceIndex
        const payload = {
          sourceDicomId: dicomId,
          patCardId: this.$store.getters.patCardId,
          patientName: this.$store.getters.patName,
          studyUid: req.studyUid,
          seriesUid: req.seriesUid,
          studyDate: (this.seriesInfo && this.seriesInfo.seriesDate) || '',
          bodyPart: req.bodyPart,
          imageCount: req.imageCount,
          detectMode,
          sliceIndex,
          sourceSliceIndex: sliceIndex != null ? sliceIndex + 1 : null,
          instanceUid: result.instanceUid || this.aiInstanceUid || null,
          lesions: lesionPayload,
          engine: result.engine || (resultData && resultData.engine) || '',
          disclaimer: result.disclaimer || '',
          lesionCount: result.lesionCount || 0
        }
        const res = await saveAiLesionResult(payload)
        if (res.code === 200) {
          const modeLabel = detectMode === 'single' ? '单层 DICOM' : '完整序列'
          this.appendDetectLog(`AI 识别结果已保存（${modeLabel} + 病灶标记）`, 'success')
          if (typeof this.loadSavedAiLesions === 'function') {
            try {
              await this.loadSavedAiLesions()
            } catch (e) {
              this.appendDetectLog('刷新 AI 列表失败，请手动刷新页面', 'warn')
            }
          }
        } else {
          this.appendDetectLog(res.msg || '保存 AI 识别结果失败', 'error')
        }
      } catch (e) {
        this.appendDetectLog((e && e.message) || '保存 AI 识别结果失败', 'error')
      }
    },
    syncLesionOverlaysForCurrentSlice() {
      const ctx = this.getLesionViewerContext()
      if (!ctx.canvas || !ctx.stack) return
      let image = null
      try {
        image = cornerstone.getImage(ctx.canvas)
      } catch (e) {
        return
      }
      if (!image) return

      try {
        const idx = ctx.stack.currentImageIdIndex
        const dicomId = String(this.activeSeriesDicomId || '')
        const overlayType = this.aiOverlayType || 'bbox'
        let lesions = []

        if (
          this.aiLesionPanelVisible &&
          this.activeLesionDicomId === dicomId &&
          (this.aiLesionList.length || this.aiOverlayType === 'heatmap' ||
            (this.aiGgoRegions && this.aiGgoRegions.length))
        ) {
          if (this.lesionOverlayMode === 'series') {
            lesions = this.aiLesionList.filter(
              (l) => l.sliceIndex == null || l.sliceIndex === idx
            )
          } else if (this.lesionOverlayMode === 'slice') {
            lesions = this.aiLesionList.filter((l) => l.sliceIndex === idx)
          }
        }

        const overlayMeta = {
          overlayType,
          heatmap: this.aiHeatmapData || null,
          heatmapSliceIndex: this.aiHeatmapSliceIndex,
          ggoRegions: this.aiGgoRegions || [],
          sliceIndex: idx
        }

        if (overlayType === 'heatmap' && this.aiHeatmapData) {
          clearLesionOverlays(ctx.canvas)
          renderLesionOverlays(ctx.canvas, [], overlayMeta)
          return
        }

        const hasGgo = this.aiGgoRegions && this.aiGgoRegions.length
        if (!lesions.length && !hasGgo) {
          clearLesionOverlays(ctx.canvas)
          return
        }

        renderLesionOverlays(ctx.canvas, lesions, overlayMeta)
      } catch (e) {
        // 图像或 overlay 未就绪时忽略，避免打断识别流程
      }
    },
    jumpToLesionSlice(lesion) {
      const ctx = this.getLesionViewerContext()
      if (!ctx.canvas || lesion.sliceIndex == null) return
      ctx.stack.currentImageIdIndex = lesion.sliceIndex
      this.refreshLesionCanvas().then(() => {
        this.syncLesionOverlaysForCurrentSlice()
      })
    },
    toggleLesionMarker(lesion) {
      if (!lesion || !lesion.id) return
      const flip = (list) => {
        if (!list || !list.length) return false
        const idx = list.findIndex((l) => l.id === lesion.id)
        if (idx < 0) return false
        const next = list[idx].markerVisible === false
        this.$set(list[idx], 'markerVisible', next)
        return true
      }
      if (!flip(this.aiLesionList) && !flip(this.aiGgoRegions)) return
      this.syncLesionOverlaysForCurrentSlice()
    },
    closeLesionLogPanel() {
      this.$store.commit('SET_LESION_LOG_PANEL', false)
      this.$store.commit('SET_LESION_DETECT_LOADING', false)
    },
    closeLesionPanel() {
      this.aiLesionPanelVisible = false
      this.activeLesionDicomId = null
      const ctx = this.getLesionViewerContext()
      if (ctx.canvas) clearLesionOverlays(ctx.canvas)
    }
  }
}
