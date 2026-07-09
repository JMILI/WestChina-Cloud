<template>
  <transition name="el-fade-in">
    <aside v-if="visible" class="lesion-log-panel">
      <header class="lesion-log-panel__head">
        <span><i class="el-icon-loading" v-if="loading"></i> AI 识别过程</span>
        <button type="button" class="lesion-log-panel__close" @click="$emit('close')">关闭</button>
      </header>

      <div class="lesion-log-panel__progress">
        <div class="stage-track">
          <div
            v-for="(item, idx) in stagePipeline"
            :key="item.id"
            class="stage-track__item"
            :class="stageItemClass(idx, item)"
          >
            <div class="stage-track__dot">
              <i v-if="isStageDone(idx)" class="el-icon-check" />
              <span v-else>{{ idx + 1 }}</span>
            </div>
            <div class="stage-track__label">{{ item.label }}</div>
            <div v-if="idx < stagePipeline.length - 1" class="stage-track__line" />
          </div>
        </div>

        <div class="stage-progress-row">
          <el-progress
            :percentage="displayProgress"
            :status="progressStatus"
            :stroke-width="6"
            :show-text="false"
            class="stage-progress"
          />
          <span class="stage-progress__pct">{{ displayProgress }}%</span>
        </div>

        <div v-if="stageDetail" class="stage-text">
          <span class="stage-text__badge">{{ currentStageLabel }}</span>
          {{ stageDetail }}
        </div>
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
import {
  computeStageProgress,
  getStageDetailText,
  getStagePipeline,
  resolveStageIndex
} from '@/utils/lesionDetectStages'

export default {
  name: 'LesionDetectLogPanel',
  props: {
    visible: { type: Boolean, default: false },
    loading: { type: Boolean, default: false },
    progress: { type: Number, default: 0 },
    stage: { type: String, default: '' },
    engine: { type: String, default: '' },
    logs: { type: Array, default: () => [] },
    stats: { type: Object, default: null }
  },
  data() {
    return {
      maxDisplayProgress: 0
    }
  },
  computed: {
    stagePipeline() {
      return getStagePipeline(this.engine)
    },
    activeStageIndex() {
      const idx = resolveStageIndex(this.stagePipeline, this.stage)
      if (idx >= 0) return idx
      return this.loading ? 0 : -1
    },
    mappedProgress() {
      return computeStageProgress(this.stagePipeline, this.stage, this.progress)
    },
    displayProgress() {
      return Math.max(this.maxDisplayProgress, this.mappedProgress)
    },
    progressStatus() {
      if (this.stage === 'done' || this.displayProgress >= 100) return 'success'
      if (this.stage === 'cancelled') return 'exception'
      if (this.loading) return undefined
      return undefined
    },
    currentStageLabel() {
      const idx = this.activeStageIndex
      if (idx >= 0 && this.stagePipeline[idx]) {
        return this.stagePipeline[idx].label
      }
      return '准备'
    },
    stageDetail() {
      return getStageDetailText(this.stage, this.engine)
    },
    statsSummary() {
      if (!this.stats) return ''
      const n = this.stats.lesionCount != null ? this.stats.lesionCount : 0
      const c = this.stats.candidates != null ? this.stats.candidates : 0
      return `统计：候选区域 ${c} 个，最终病灶 ${n} 处`
    }
  },
  watch: {
    visible(val) {
      if (val) this.maxDisplayProgress = 0
    },
    mappedProgress(val) {
      if (val > this.maxDisplayProgress) this.maxDisplayProgress = val
    },
    logs() {
      this.$nextTick(() => this.scrollToBottom())
    }
  },
  methods: {
    isStageDone(idx) {
      if (this.stage === 'done') return idx <= this.stagePipeline.length - 1
      const active = this.activeStageIndex
      return active >= 0 && idx < active
    },
    stageItemClass(idx, item) {
      const active = this.activeStageIndex
      if (this.stage === 'done' || item.id === 'done' && this.stage === 'done') {
        return { 'is-done': true }
      }
      if (this.stage === 'cancelled') {
        return { 'is-cancelled': idx === active }
      }
      return {
        'is-done': this.isStageDone(idx),
        'is-active': idx === active,
        'is-pending': active >= 0 && idx > active
      }
    },
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
  z-index: 1;
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
  padding: 8px 12px 4px;
  flex-shrink: 0;
  text-align: left;

  .stage-progress-row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 2px;
  }

  .stage-progress {
    flex: 1;
    min-width: 0;
    max-width: calc(100% - 36px);

    ::v-deep .el-progress-bar {
      padding-right: 0;
      margin-right: 0;
    }

    ::v-deep .el-progress-bar__outer {
      border-radius: 3px;
    }

    ::v-deep .el-progress-bar__inner {
      border-radius: 3px;
    }
  }

  .stage-progress__pct {
    flex-shrink: 0;
    width: 32px;
    font-size: 11px;
    color: #9aa0a8;
    text-align: right;
    line-height: 1;
  }

  .stage-text {
    margin-top: 6px;
    font-size: 10px;
    color: #9aa0a8;
    line-height: 1.45;

    &__badge {
      display: inline-block;
      margin-right: 4px;
      padding: 0 5px;
      border-radius: 2px;
      background: rgba(240, 169, 110, 0.18);
      color: #f0a96e;
      font-weight: 600;
      font-size: 10px;
    }
  }
}

.stage-track {
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  margin-bottom: 8px;
  overflow: hidden;
  gap: 0;
  width: 100%;

  &__item {
    position: relative;
    flex: 1 1 0;
    min-width: 0;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    text-align: left;
  }

  &__dot {
    width: 18px;
    height: 18px;
    border-radius: 50%;
    border: 1.5px solid rgba(154, 160, 168, 0.45);
    color: #9aa0a8;
    font-size: 9px;
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(255, 255, 255, 0.04);
    z-index: 1;
    flex-shrink: 0;

    .el-icon-check {
      font-size: 10px;
    }
  }

  &__label {
    margin-top: 3px;
    font-size: 9px;
    color: #9aa0a8;
    white-space: nowrap;
    line-height: 1.15;
    transform: scale(0.92);
    transform-origin: left top;
    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  &__line {
    position: absolute;
    top: 9px;
    left: 18px;
    width: calc(100% - 18px);
    height: 1.5px;
    background: rgba(154, 160, 168, 0.25);
    z-index: 0;
  }

  &__item.is-done {
    .stage-track__dot {
      border-color: #67c23a;
      background: rgba(103, 194, 58, 0.15);
      color: #67c23a;
    }
    .stage-track__label {
      color: #67c23a;
    }
    .stage-track__line {
      background: rgba(103, 194, 58, 0.45);
    }
  }

  &__item.is-active {
    .stage-track__dot {
      border-color: #f0a96e;
      background: rgba(240, 169, 110, 0.2);
      color: #f0a96e;
      box-shadow: 0 0 0 2px rgba(240, 169, 110, 0.1);
    }
    .stage-track__label {
      color: #f0a96e;
      font-weight: 600;
    }
  }

  &__item.is-cancelled {
    .stage-track__dot {
      border-color: #f56c6c;
      color: #f56c6c;
    }
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
