<template>

  <el-dialog

    title="选择序列进行病灶识别"

    :visible.sync="dialogVisible"

    width="1320px"

    append-to-body

    custom-class="lesion-series-dialog"

    @close="handleClose"
  >

    <div class="dialog-toolbar">

      <p class="dialog-tip">

        请选择需要识别的 CT 序列。当前仅支持<strong>胸部</strong>相关检查部位；识别结果请在左侧「<strong>AI识别病灶结果</strong>」中点击查看标记或热力图。

      </p>

      <div class="engine-select-wrap">
        <lesion-engine-select :show-label="true" :compact="false" sub-engine-display="radio" />
      </div>

      <div v-if="detectEngine === 'scheme-b'" class="enhanced-ct-bar">
        <el-checkbox v-model="enhancedCtEnabled">配对增强 CT（ΔHU 分析）</el-checkbox>
        <el-select
          v-model="enhancedDicomId"
          size="small"
          clearable
          placeholder="选择增强序列"
          :disabled="!enhancedCtEnabled"
          class="enhanced-ct-bar__select"
        >
          <el-option
            v-for="s in chestSeriesOptions"
            :key="s.dicomId"
            :label="formatSeriesOptionLabel(s)"
            :value="s.dicomId"
          >
            <el-tooltip :content="s.seriesUid || '-'" placement="top" :open-delay="300">
              <span class="enhanced-option-label">
                #{{ s.index }} {{ s.seriesUid || '-' }} ({{ s.imageCount }}层)
              </span>
            </el-tooltip>
          </el-option>
        </el-select>
        <span v-if="enhancedCtEnabled" class="enhanced-ct-bar__tip">
          平扫序列识别时将下载配对增强序列并计算 ΔHU
        </span>
      </div>

    </div>

    <p v-if="selectedEngineDesc" class="engine-desc">{{ selectedEngineDesc }}</p>

    <el-table
      :data="seriesRows"
      size="small"
      max-height="420"
      stripe
      border
      style="width: 100%"
      empty-text="暂无序列数据"
    >

      <el-table-column label="序号" prop="index" width="56" align="center" />

      <el-table-column label="序列 ID" min-width="360" show-overflow-tooltip>
        <template slot-scope="{ row }">
          <span class="mono uid-cell">{{ row.seriesUid || '-' }}</span>
        </template>
      </el-table-column>

      <el-table-column label="检查部位" prop="bodyPart" width="100" show-overflow-tooltip />

      <el-table-column label="层数" prop="imageCount" width="64" align="center" />

      <el-table-column label="可识别" width="88" align="center">

        <template slot-scope="{ row }">

          <el-tag :type="row.allowDetect ? 'success' : 'info'" size="mini">

            {{ row.allowDetect ? '支持' : '不支持' }}

          </el-tag>

        </template>

      </el-table-column>

      <el-table-column label="识别状态" min-width="180" show-overflow-tooltip>

        <template slot-scope="{ row }">

          <div v-if="statusOf(row) === 'detecting'" class="status detecting">

            <el-progress
              :percentage="progressOf(row)"
              :stroke-width="8"
              :show-text="true"
              status="warning"
            />

            <span class="stage-label">{{ stageLabel(row) }}</span>

          </div>

          <span v-else-if="statusOf(row) === 'done'" class="status done">

            已识别 {{ lesionCount(row) }} 处

          </span>

          <span v-else-if="statusOf(row) === 'empty'" class="status empty">已识别（未发现病灶）</span>

          <span v-else-if="statusOf(row) === 'error'" class="status error">
            识别失败
            <el-tooltip v-if="errorMsgOf(row)" :content="errorMsgOf(row, true)" placement="top">
              <span class="error-hint">{{ errorMsgOf(row) }}</span>
            </el-tooltip>
          </span>

          <span v-else-if="statusOf(row) === 'cancelled'" class="status cancelled">已取消</span>

          <span v-else class="status pending">未识别</span>

        </template>

      </el-table-column>

      <el-table-column label="查阅图像" width="88" align="center" fixed="right">
        <template slot-scope="{ row }">
          <el-button
            v-if="isViewing(row)"
            type="text"
            size="mini"
            disabled
            class="viewing-btn"
          >
            正在查阅
          </el-button>
          <el-button
            v-else
            type="primary"
            size="mini"
            plain
            class="view-series-btn"
            @click="handleViewSeries(row)"
          >
            查阅
          </el-button>
        </template>
      </el-table-column>

      <el-table-column label="操作" width="268" align="center" fixed="right">

        <template slot-scope="{ row }">

          <template v-if="row.allowDetect">
            <el-button
              type="text"
              size="mini"
              class="show-log-btn"
              @click="handleShowLogs(row)"
            >
              查看日志
            </el-button>

            <el-button
              type="warning"
              size="mini"
              plain
              :disabled="isDetecting(row)"
              @click="handleDetect(row)"
            >
              开始识别
            </el-button>

            <el-button
              type="text"
              size="mini"
              class="cancel-btn"
              :disabled="!canCancel(row)"
              @click="handleCancel(row)"
            >
              取消任务
            </el-button>
          </template>

          <el-tooltip v-else content="仅支持胸部 CT 序列" placement="top">

            <el-button size="mini" disabled>不可识别</el-button>

          </el-tooltip>

        </template>

      </el-table-column>

    </el-table>

  </el-dialog>

</template>



<script>

import { mapGetters } from 'vuex'

import { getEngineDescription } from '@/utils/lesionEngines'

import { flattenStudySeries } from '@/utils/lesionDetect'

import LesionEngineSelect from './LesionEngineSelect'

export default {

  name: 'LesionSeriesDialog',

  components: { LesionEngineSelect },

  props: {

    visible: { type: Boolean, default: false },

    studySeriesList: { type: Object, default: () => ({}) },

    lesionResultsByDicomId: { type: Object, default: () => ({}) },

    activeSeriesDicomId: { type: [String, Number], default: null }

  },

  data() {

    return {
      enhancedCtEnabled: false,
      enhancedDicomId: null
    }

  },

  computed: {

    ...mapGetters(['lesionDetectEngine', 'lesionEngineCatalog']),

    dialogVisible: {

      get() { return this.visible },

      set(val) { this.$emit('update:visible', val) }

    },

    seriesRows() {

      return flattenStudySeries(this.studySeriesList)

    },

    detectEngine() {

      return this.lesionDetectEngine || 'heuristic'

    },

    engineOptions() {

      return this.lesionEngineCatalog.length
        ? this.lesionEngineCatalog
        : []

    },

    selectedEngineDesc() {

      return getEngineDescription(this.detectEngine, this.engineOptions)

    },

    chestSeriesOptions() {
      return this.seriesRows.filter((r) => r.allowDetect)
    }

  },

  methods: {
    findEngineOption(id) {

      return this.engineOptions.find((o) => o.id === id)

    },

    handleDetect(row) {

      const opt = this.findEngineOption(this.detectEngine)

      if (opt && !opt.available) {

        this.$message.warning(opt.installHint || '请先安装对应识别引擎')

        return

      }

      this.$emit('detect', {

        ...row,

        detectEngine: this.detectEngine,

        ...this.buildEnhancedPayload(row)

      })

    },

    buildEnhancedPayload(row) {
      if (this.detectEngine !== 'scheme-b' || !this.enhancedCtEnabled || !this.enhancedDicomId) {
        return {}
      }
      if (String(this.enhancedDicomId) === String(row.dicomId)) {
        return {}
      }
      const enh = this.seriesRows.find((s) => String(s.dicomId) === String(this.enhancedDicomId))
      if (!enh) return {}
      return {
        enhancedSeriesUid: enh.seriesUid,
        enhancedImageCount: enh.imageCount
      }
    },

    formatSeriesOptionLabel(s) {
      if (!s) return ''
      return `#${s.index} ${s.seriesUid || '-'} (${s.imageCount}层)`
    },

    resultOf(row) {

      const bySeries = this.lesionResultsByDicomId[String(row.dicomId)]

      if (bySeries) return bySeries

      const aiKey = Object.keys(this.lesionResultsByDicomId).find((key) => {

        const r = this.lesionResultsByDicomId[key]

        return r && String(r.sourceDicomId) === String(row.dicomId)

      })

      return aiKey ? this.lesionResultsByDicomId[aiKey] : null

    },

    statusOf(row) {

      const r = this.resultOf(row)

      return r ? r.status : 'pending'

    },

    lesionCount(row) {

      const r = this.resultOf(row)

      if (!r) return 0

      return r.lesionCount != null ? r.lesionCount : (r.lesions || []).length

    },

    errorMsgOf(row, full = false) {
      const r = this.resultOf(row)
      if (!r || !r.errorMsg) return ''
      const msg = String(r.errorMsg)
      if (full) return msg
      return msg.length > 40 ? msg.slice(0, 40) + '…' : msg
    },

    isViewing(row) {
      if (this.activeSeriesDicomId == null || !row) return false
      return String(this.activeSeriesDicomId) === String(row.dicomId)
    },

    handleViewSeries(row) {
      if (!row || !row.series) {
        this.$message.warning('序列数据不完整，无法查阅')
        return
      }
      this.dialogVisible = false
      this.$emit('view-series', row)
    },

    hasResult(row) {

      const s = this.statusOf(row)

      return s === 'done' || s === 'empty'

    },

    isDetecting(row) {
      return this.statusOf(row) === 'detecting'
    },

    hasTaskId(row) {
      const r = this.resultOf(row)
      return !!(r && r.taskId)
    },

    canShowLogs(row) {
      const r = this.resultOf(row)
      return this.isDetecting(row) || (r && (r.status === 'done' || r.status === 'empty' || r.status === 'error' || r.status === 'cancelled'))
    },

    progressOf(row) {

      const r = this.resultOf(row)

      return r && r.progress != null ? Math.min(100, Math.max(0, r.progress)) : 0

    },

    stageLabel(row) {

      const r = this.resultOf(row)

      const stage = r && r.stage

      if (stage === 'queued') {
        const hint = r && r.queueMessage
        if (hint && hint !== '任务已提交，等待执行') return hint
        return '排队等待中…'
      }
      if (stage === 'connect' || stage === 'running') return '连接 AI 服务…'
      if (stage === 'download') return 'MinIO 下载 DICOM'
      if (stage === 'volume') return '构建 3D 体数据'
      if (stage === 'segment') return '肺野分割'
      if (stage === 'detect') return '结节检测 / 融合分析'
      if (stage === 'enhanced') return '增强 CT ΔHU'
      if (stage === 'infer') return '模型推理'
      if (stage === 'done') return '完成'
      return '识别中…'

    },

    canCancel(row) {
      const r = this.resultOf(row)
      return !!(r && r.status === 'detecting' && r.taskId)
    },

    handleCancel(row) {
      const r = this.resultOf(row)
      if (!r || !r.taskId) {
        this.$message.info('当前没有可取消的任务')
        return
      }
      this.$emit('cancel', {
        taskId: r.taskId,
        dicomId: row.dicomId
      })
    },

    handleShowLogs(row) {

      const r = this.resultOf(row)

      this.$emit('show-logs', {

        taskId: r && r.taskId ? r.taskId : null,

        dicomId: row.dicomId

      })

    },

    handleClose() {

      this.$emit('update:visible', false)

    }

  }

}

</script>



<style lang="scss">

.lesion-series-dialog {

  max-width: 99vw;

  .el-dialog__body {

    padding-top: 8px;

  }

  .el-table {

    .el-table__fixed-right {
      box-shadow: -4px 0 8px rgba(0, 0, 0, 0.06);
    }

    .el-table__fixed-right-patch {
      background: #fff;
    }

    th.el-table__cell,
    td.el-table__cell {
      background: inherit;
    }
  }

  .dialog-toolbar {

    display: flex;

    flex-direction: column;

    align-items: stretch;

    gap: 12px;

    margin-bottom: 10px;

  }

  .dialog-tip {

    margin: 0;

    width: 100%;

    font-size: 13px;

    color: #606266;

    line-height: 1.6;

    strong {

      color: #e6a23c;

    }

  }

  .engine-select-wrap {

    display: flex;

    align-items: center;

    flex-wrap: wrap;

    gap: 10px;

    padding: 10px 12px;

    background: #f5f7fa;

    border: 1px solid #ebeef5;

    border-radius: 6px;

    ::v-deep .lesion-engine-select {

      flex-wrap: wrap;

      row-gap: 8px;

    }

    ::v-deep .lesion-engine-select__control {

      width: 200px;

    }

    ::v-deep .lesion-engine-select__sub {

      flex-wrap: wrap;

    }

  }

  .engine-desc {

    margin: 0 0 10px;

    font-size: 12px;

    color: #909399;

    line-height: 1.4;

  }

  .enhanced-ct-bar {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
    padding: 8px 12px;
    background: #fdf6ec;
    border: 1px solid #faecd8;
    border-radius: 6px;
    font-size: 12px;

    &__select {
      width: 420px;
    }

    &__tip {
      color: #909399;
      font-size: 11px;
    }
  }

  .mono {

    font-family: monospace;

    font-size: 12px;

  }

  .uid-cell {
    display: inline-block;
    max-width: 100%;
    word-break: break-all;
    white-space: normal;
    line-height: 1.4;
  }

  .enhanced-option-label {
    display: inline-block;
    max-width: 100%;
  }

  .view-series-btn {
    font-weight: 600;
  }

  .viewing-btn {
    color: #67c23a;
    font-weight: 600;
  }

  .show-log-btn {
    margin-right: 4px;
    color: #409eff;
  }

  .cancel-btn {
    margin-left: 4px;
    color: #f56c6c;
  }

  .status {

    font-size: 12px;

    &.detecting {
      color: #e6a23c;

      .stage-label {
        display: block;
        margin-top: 4px;
        font-size: 11px;
        color: #909399;
      }
    }

    &.done { color: #67c23a; }

    &.empty { color: #909399; }

    &.error {
    color: #f56c6c;

    .error-hint {
      display: block;
      margin-top: 2px;
      font-size: 11px;
      color: #909399;
      cursor: help;
    }
  }

    &.pending { color: #c0c4cc; }

    &.cancelled { color: #909399; }

  }

}

</style>


