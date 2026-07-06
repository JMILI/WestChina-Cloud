<template>
  <transition name="el-fade-in">
    <aside v-if="visible" class="lesion-log-panel">
      <header class="lesion-log-panel__head">
        <span><i class="el-icon-loading" v-if="loading"></i> AI 识别过程</span>
        <button type="button" class="lesion-log-panel__close" @click="$emit('close')">关闭</button>
      </header>

      <div class="lesion-log-panel__progress">
        <el-progress
          :percentage="progress"
          :status="progressStatus"
          :stroke-width="10"
        />
        <div v-if="stageText" class="stage-text">{{ stageText }}</div>
      </div>

      <div v-if="statsSummary" class="lesion-log-panel__stats">
        {{ statsSummary }}
      </div>

      <div ref="logBody" class="lesion-log-panel__body">
        <div
          v-for="(item, idx) in logs"
          :key="idx"
          class="log-line"
          :class="'log-line--' + (item.level || 'info')"
        >
          <span class="log-time">{{ item.time }}</span>
          <span class="log-msg">{{ item.message }}</span>
        </div>
        <div v-if="!logs.length" class="log-empty">等待后端日志…</div>
      </div>
    </aside>
  </transition>
</template>

<script>
export default {
  name: 'LesionDetectLogPanel',
  props: {
    visible: { type: Boolean, default: false },
    loading: { type: Boolean, default: false },
    progress: { type: Number, default: 0 },
    stage: { type: String, default: '' },
    logs: { type: Array, default: () => [] },
    stats: { type: Object, default: null }
  },
  computed: {
    progressStatus() {
      if (this.loading) return undefined
      if (this.progress >= 100) return 'success'
      return undefined
    },
    stageText() {
      if (this.stage === 'download') return '阶段：MinIO 下载 DICOM'
      if (this.stage === 'volume') return '阶段：构建 3D 体数据'
      if (this.stage === 'segment') return '阶段：肺野分割'
      if (this.stage === 'detect') return '阶段：结节检测 / 融合分析'
      if (this.stage === 'infer') return '阶段：模型推理 + 热力图生成'
      if (this.stage === 'done') return '阶段：完成'
      return this.loading ? '阶段：准备中…' : ''
    },
    statsSummary() {
      if (!this.stats) return ''
      const n = this.stats.lesionCount != null ? this.stats.lesionCount : 0
      const c = this.stats.candidates != null ? this.stats.candidates : 0
      return `统计：候选区域 ${c} 个，最终病灶 ${n} 处`
    }
  },
  watch: {
    logs() {
      this.$nextTick(() => this.scrollToBottom())
    }
  },
  methods: {
    scrollToBottom() {
      const el = this.$refs.logBody
      if (el) el.scrollTop = el.scrollHeight
    }
  }
}
</script>

<style lang="scss" scoped>
.lesion-log-panel {
  flex-shrink: 0;
  width: 340px;
  height: 100%;
  background: rgba(22, 26, 32, 0.97);
  border-left: 1px solid rgba(240, 169, 110, 0.35);
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.35);
  display: flex;
  flex-direction: column;
  color: #e8eaed;
  font-size: 12px;
  overflow: hidden;
}

.lesion-log-panel__head {
  padding: 10px 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  font-weight: 600;
  color: #f0a96e;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.lesion-log-panel__close {
  border: none;
  background: transparent;
  color: #9aa0a8;
  cursor: pointer;
  font-size: 12px;
  padding: 2px 6px;

  &:hover {
    color: #f0a96e;
  }
}

.lesion-log-panel__progress {
  padding: 10px 12px 6px;
  flex-shrink: 0;

  .stage-text {
    margin-top: 6px;
    font-size: 11px;
    color: #9aa0a8;
  }
}

.lesion-log-panel__stats {
  padding: 0 12px 8px;
  font-size: 12px;
  color: #67c23a;
  flex-shrink: 0;
}

.lesion-log-panel__body {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 6px 10px 12px;
  font-family: 'Consolas', 'Monaco', monospace;
}

.log-line {
  display: flex;
  gap: 8px;
  padding: 3px 0;
  line-height: 1.45;
  word-break: break-all;

  &--info .log-msg { color: #c5cad3; }
  &--success .log-msg { color: #67c23a; }
  &--warn .log-msg { color: #e6a23c; }
  &--error .log-msg { color: #f56c6c; }
}

.log-time {
  flex-shrink: 0;
  color: #6b7280;
  font-size: 10px;
}

.log-empty {
  color: #6b7280;
  text-align: center;
  padding: 20px 0;
}
</style>
