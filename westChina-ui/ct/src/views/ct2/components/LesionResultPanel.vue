<template>
  <transition name="el-fade-in">
    <aside
      v-if="visible"
      ref="panel"
      class="ai-lesion-panel"
      :class="{ 'is-dragging': dragging }"
      :style="panelStyle"
    >
      <header
        class="ai-lesion-panel__head"
        @mousedown="onHeadMouseDown"
      >
        <span class="ai-lesion-panel__title">
          <i class="el-icon-rank ai-lesion-panel__drag-icon"></i>
          AI 病灶识别
        </span>
        <button type="button" class="ai-lesion-panel__close" @mousedown.stop @click="$emit('close')">
          <i class="el-icon-close"></i>
        </button>
      </header>
      <p v-if="engine" class="ai-lesion-panel__engine">引擎：{{ engine }}</p>
      <p v-if="detectMode" class="ai-lesion-panel__meta-line">
        识别模式：{{ detectModeLabel }}
      </p>
      <p v-if="sliceIndex != null" class="ai-lesion-panel__meta-line">
        标记层位：第 {{ sliceIndex + 1 }} 层
      </p>
      <p v-if="instanceUid" class="ai-lesion-panel__meta-line ai-lesion-panel__uid" :title="instanceUid">
        Instance UID：{{ shortInstanceUid }}
      </p>
      <div v-if="screening" class="ai-lesion-screening">
        <div class="ai-lesion-screening__title">单层异常倾向</div>
        <div class="ai-lesion-screening__label">{{ screening.label }}</div>
        <div v-if="screening.confidence != null" class="ai-lesion-screening__conf">
          置信度 {{ (screening.confidence * 100).toFixed(1) }}%
        </div>
        <ul v-if="screening.probs" class="ai-lesion-screening__probs">
          <li v-for="(val, key) in screening.probs" :key="key">
            <span>{{ key }}</span>
            <span>{{ (val * 100).toFixed(1) }}%</span>
          </li>
        </ul>
      </div>
      <p v-if="disclaimer" class="ai-lesion-panel__tip">{{ disclaimer }}</p>
      <ul v-if="lesions.length" class="ai-lesion-list">
        <li
          v-for="item in lesions"
          :key="item.id"
          class="ai-lesion-item"
          @click="$emit('select', item)"
        >
          <div class="ai-lesion-item__title">
            <span>{{ item.label || item.type }}</span>
            <span v-if="item.confidence != null" class="ai-lesion-item__conf">
              {{ (item.confidence * 100).toFixed(1) }}%
            </span>
          </div>
          <div class="ai-lesion-item__meta">{{ metricsText(item) }}</div>
          <div v-if="item.sliceIndex != null" class="ai-lesion-item__slice">
            层位：{{ item.sliceIndex + 1 }}
          </div>
          <div v-if="item.instanceUid" class="ai-lesion-item__slice" :title="item.instanceUid">
            UID：{{ shortUid(item.instanceUid) }}
          </div>
        </li>
      </ul>
      <div v-else-if="screening" class="ai-lesion-empty">无结节框；请查看图像上的热力图</div>
      <div v-else class="ai-lesion-empty">暂无病灶数据</div>
    </aside>
  </transition>
</template>

<script>
import { formatLesionMetrics, truncateUid } from '@/utils/lesionDetect'
import { formatDetectModeLabel } from '@/utils/aiLesionSeries'

const PANEL_TOP = 58
const PANEL_MARGIN = 12

export default {
  name: 'LesionResultPanel',
  props: {
    visible: { type: Boolean, default: false },
    lesions: { type: Array, default: () => [] },
    disclaimer: { type: String, default: '' },
    engine: { type: String, default: '' },
    screening: { type: Object, default: null },
    instanceUid: { type: String, default: '' },
    detectMode: { type: String, default: 'series' },
    sliceIndex: { type: Number, default: null },
    offsetRight: { type: Number, default: 0 }
  },
  data() {
    return {
      panelPos: null,
      dragging: false,
      dragOffset: { x: 0, y: 0 }
    }
  },
  computed: {
    detectModeLabel() {
      return formatDetectModeLabel(this.detectMode)
    },
    shortInstanceUid() {
      return truncateUid(this.instanceUid)
    },
    panelStyle() {
      if (this.panelPos) {
        return {
          left: `${this.panelPos.x}px`,
          top: `${this.panelPos.y}px`,
          right: 'auto'
        }
      }
      const right = this.offsetRight > 0 ? this.offsetRight + PANEL_MARGIN : PANEL_MARGIN
      return {
        top: `${PANEL_TOP}px`,
        right: `${right}px`,
        left: 'auto'
      }
    }
  },
  watch: {
    visible(val) {
      if (!val) {
        this.stopDrag()
        this.panelPos = null
      }
    },
    offsetRight() {
      if (!this.dragging && this.panelPos) {
        this.panelPos = null
      }
    }
  },
  beforeDestroy() {
    this.stopDrag()
  },
  methods: {
    metricsText(lesion) {
      return formatLesionMetrics(lesion)
    },
    shortUid(uid) {
      return truncateUid(uid)
    },
    onHeadMouseDown(event) {
      if (event.button !== 0) return
      const panel = this.$refs.panel
      if (!panel) return

      const rect = panel.getBoundingClientRect()
      if (!this.panelPos) {
        this.panelPos = { x: rect.left, y: rect.top }
      }
      this.dragging = true
      this.dragOffset = {
        x: event.clientX - this.panelPos.x,
        y: event.clientY - this.panelPos.y
      }
      document.addEventListener('mousemove', this.onDragMove)
      document.addEventListener('mouseup', this.onDragEnd)
      event.preventDefault()
    },
    onDragMove(event) {
      if (!this.dragging || !this.panelPos) return
      const panel = this.$refs.panel
      const maxW = panel ? panel.offsetWidth : 300
      const maxH = panel ? panel.offsetHeight : 400
      const maxX = window.innerWidth - maxW - PANEL_MARGIN
      const maxY = window.innerHeight - maxH - PANEL_MARGIN
      this.panelPos = {
        x: Math.max(PANEL_MARGIN, Math.min(maxX, event.clientX - this.dragOffset.x)),
        y: Math.max(PANEL_TOP, Math.min(maxY, event.clientY - this.dragOffset.y))
      }
    },
    onDragEnd() {
      this.stopDrag()
    },
    stopDrag() {
      this.dragging = false
      document.removeEventListener('mousemove', this.onDragMove)
      document.removeEventListener('mouseup', this.onDragEnd)
    }
  }
}
</script>

<style lang="scss" scoped>
.ai-lesion-panel {
  position: fixed;
  z-index: 2000;
  width: 300px;
  max-height: calc(100vh - 80px);
  overflow: auto;
  overflow-x: hidden;
  background: rgba(28, 32, 40, 0.96);
  border: 1px solid rgba(240, 169, 110, 0.35);
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45);
  color: #e8eaed;
  font-size: 13px;

  &.is-dragging {
    user-select: none;
    cursor: grabbing;
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.55);
  }
}

.ai-lesion-panel__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  font-weight: 600;
  color: #f0a96e;
  cursor: grab;

  &:active {
    cursor: grabbing;
  }
}

.ai-lesion-panel__title {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.ai-lesion-panel__drag-icon {
  font-size: 14px;
  opacity: 0.75;
}

.ai-lesion-panel__close {
  border: none;
  background: transparent;
  color: #9aa0a8;
  cursor: pointer;
  font-size: 16px;
  padding: 0;

  &:hover {
    color: #fff;
  }
}

.ai-lesion-panel__engine {
  margin: 0;
  padding: 6px 12px 0;
  font-size: 11px;
  color: #7eb8ff;
}

.ai-lesion-panel__meta-line {
  margin: 0;
  padding: 4px 12px 0;
  font-size: 11px;
  color: #b0b6be;
  word-break: break-all;
}

.ai-lesion-panel__uid {
  font-family: monospace;
}

.ai-lesion-screening {
  margin: 8px 12px;
  padding: 10px;
  border-radius: 6px;
  background: rgba(103, 194, 58, 0.08);
  border: 1px solid rgba(103, 194, 58, 0.25);
}

.ai-lesion-screening__title {
  font-size: 11px;
  color: #9aa0a8;
  margin-bottom: 4px;
}

.ai-lesion-screening__label {
  font-size: 14px;
  font-weight: 600;
  color: #f0a96e;
  margin-bottom: 4px;
}

.ai-lesion-screening__conf {
  font-size: 13px;
  color: #67c23a;
  margin-bottom: 6px;
}

.ai-lesion-screening__probs {
  list-style: none;
  margin: 0;
  padding: 0;
  font-size: 12px;
  color: #b8bcc6;

  li {
    display: flex;
    justify-content: space-between;
    padding: 2px 0;
  }
}

.ai-lesion-panel__tip {
  margin: 0;
  padding: 8px 12px;
  font-size: 11px;
  line-height: 1.45;
  color: #9aa0a8;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.ai-lesion-list {
  list-style: none;
  margin: 0;
  padding: 6px 0;
}

.ai-lesion-item {
  padding: 10px 12px;
  cursor: pointer;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  transition: background 0.15s;

  &:hover {
    background: rgba(240, 169, 110, 0.1);
  }
}

.ai-lesion-item__title {
  display: flex;
  justify-content: space-between;
  font-weight: 500;
  margin-bottom: 4px;
}

.ai-lesion-item__conf {
  color: #67c23a;
  font-size: 12px;
}

.ai-lesion-item__meta,
.ai-lesion-item__slice {
  font-size: 12px;
  color: #b8bcc6;
  line-height: 1.4;
}

.ai-lesion-empty {
  padding: 16px 12px;
  color: #8b93a7;
  text-align: center;
}
</style>
