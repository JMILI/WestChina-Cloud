<template>

  <el-dialog

    title="选择序列进行病灶识别"

    :visible.sync="dialogVisible"

    width="860px"

    append-to-body

    custom-class="lesion-series-dialog"

    @close="handleClose"
  >

    <div class="dialog-toolbar">

      <p class="dialog-tip">

        请选择需要识别的 CT 序列。当前仅支持<strong>胸部</strong>相关检查部位；识别结果请在左侧「<strong>AI识别病灶结果</strong>」中点击查看标记或热力图。

      </p>

      <div class="engine-select-wrap">
        <lesion-engine-select :show-label="true" :compact="false" />
        <el-button type="text" size="small" class="algo-help-btn" @click="showAlgoExplain = true">
          <i class="el-icon-question"></i> 算法说明
        </el-button>
      </div>

    </div>

    <p v-if="selectedEngineDesc" class="engine-desc">{{ selectedEngineDesc }}</p>

    <el-table

      :data="seriesRows"

      size="small"

      max-height="420"

      stripe

      empty-text="暂无序列数据"

    >

      <el-table-column label="序号" prop="index" width="56" align="center" />

      <el-table-column label="序列 ID" min-width="140">

        <template slot-scope="{ row }">

          <span class="mono">{{ truncateUid(row.seriesUid) }}</span>

        </template>

      </el-table-column>

      <el-table-column label="检查部位" prop="bodyPart" width="100" />

      <el-table-column label="层数" prop="imageCount" width="64" align="center" />

      <el-table-column label="可识别" width="88" align="center">

        <template slot-scope="{ row }">

          <el-tag :type="row.allowDetect ? 'success' : 'info'" size="mini">

            {{ row.allowDetect ? '支持' : '不支持' }}

          </el-tag>

        </template>

      </el-table-column>

      <el-table-column label="识别状态" min-width="120">

        <template slot-scope="{ row }">

          <span v-if="statusOf(row) === 'detecting'" class="status detecting">

            <i class="el-icon-loading"></i> 识别中…

          </span>

          <span v-else-if="statusOf(row) === 'done'" class="status done">

            已识别 {{ lesionCount(row) }} 处

          </span>

          <span v-else-if="statusOf(row) === 'empty'" class="status empty">已识别（未发现病灶）</span>

          <span v-else-if="statusOf(row) === 'error'" class="status error">识别失败</span>

          <span v-else class="status pending">未识别</span>

        </template>

      </el-table-column>

      <el-table-column label="操作" width="120" align="center" fixed="right">

        <template slot-scope="{ row }">

          <el-button

            v-if="canDetect(row)"

            type="warning"

            size="mini"

            plain

            :loading="statusOf(row) === 'detecting'"

            @click="handleDetect(row)"

          >

            开始识别

          </el-button>

          <el-tooltip v-else content="仅支持胸部 CT 序列" placement="top">

            <el-button size="mini" disabled>不可识别</el-button>

          </el-tooltip>

        </template>

      </el-table-column>

    </el-table>

    <algorithm-explain-dialog
      :visible.sync="showAlgoExplain"
      :scheme="detectEngine"
    />

  </el-dialog>

</template>



<script>

import { mapGetters } from 'vuex'

import { getEngineDescription } from '@/utils/lesionEngines'

import { flattenStudySeries } from '@/utils/lesionDetect'

import LesionEngineSelect from './LesionEngineSelect'
import AlgorithmExplainDialog from './AlgorithmExplainDialog'

export default {

  name: 'LesionSeriesDialog',

  components: { LesionEngineSelect, AlgorithmExplainDialog },

  props: {

    visible: { type: Boolean, default: false },

    studySeriesList: { type: Object, default: () => ({}) },

    lesionResultsByDicomId: { type: Object, default: () => ({}) }

  },

  data() {

    return {
      showAlgoExplain: false
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

        detectEngine: this.detectEngine

      })

    },

    truncateUid(uid) {

      if (!uid) return '-'

      const str = String(uid)

      if (str.length <= 18) return str

      return str.slice(0, 8) + '…' + str.slice(-6)

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

    hasResult(row) {

      const s = this.statusOf(row)

      return s === 'done' || s === 'empty'

    },

    canDetect(row) {

      if (!row.allowDetect) return false

      const s = this.statusOf(row)

      return s === 'pending' || s === 'error' || s === 'done' || s === 'empty' || s === 'detecting'

    },

    handleClose() {

      this.$emit('update:visible', false)

    }

  }

}

</script>



<style lang="scss">

.lesion-series-dialog {

  .el-dialog__body {

    padding-top: 8px;

  }

}



.dialog-toolbar {

  display: flex;

  align-items: flex-start;

  justify-content: space-between;

  gap: 16px;

  margin-bottom: 8px;

}



.dialog-tip {

  margin: 0;

  flex: 1;

  font-size: 13px;

  color: #606266;

  line-height: 1.5;



  strong {

    color: #e6a23c;

  }

}



.engine-select-wrap {

  display: flex;

  align-items: center;

  flex-shrink: 0;

  gap: 8px;

}

.algo-help-btn {
  color: #409eff;
  padding: 0 4px;
  white-space: nowrap;
}



.engine-label {

  font-size: 13px;

  color: #606266;

  white-space: nowrap;

}



.engine-select {

  width: 240px;

}



.engine-desc {

  margin: 0 0 10px;

  font-size: 12px;

  color: #909399;

  line-height: 1.4;

}



.engine-option-disabled {

  margin-left: 6px;

  color: #c0c4cc;

  font-size: 12px;

}



.mono {

  font-family: monospace;

  font-size: 12px;

}



.status {

  font-size: 12px;



  &.detecting { color: #e6a23c; }

  &.done { color: #67c23a; }

  &.empty { color: #909399; }

  &.error { color: #f56c6c; }

  &.pending { color: #c0c4cc; }

}

</style>


