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

      <div class="ai-lesion-panel__meta">
        <p v-if="engine" class="ai-lesion-panel__engine">引擎：{{ engine }}</p>
        <p v-if="detectMode" class="ai-lesion-panel__meta-line">
          识别模式：{{ detectModeLabel }}
        </p>
        <p v-if="sliceIndex != null" class="ai-lesion-panel__meta-line">
          标记层位 Instance {{ sliceIndex + 1 }}
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
        <p v-if="displayDisclaimer" class="ai-lesion-panel__tip">{{ displayDisclaimer }}</p>
        <div v-if="lesions.length" class="ai-lesion-legend">
          <span class="ai-lesion-legend__item"><i class="dot dot--solid"></i>实性</span>
          <span class="ai-lesion-legend__item"><i class="dot dot--ggo"></i>磨玻璃</span>
          <span class="ai-lesion-legend__item"><i class="dot dot--mixed"></i>混合</span>
          <span class="ai-lesion-legend__item"><i class="dot dot--calc"></i>钙化</span>
        </div>
      </div>

      <div class="ai-lesion-panel__body">
        <ul v-if="lesions.length" class="ai-lesion-list">
          <li
            v-for="item in lesions"
            :key="item.id || item.sliceIndex + '-' + item.label"
            class="ai-lesion-item"
          >
            <div class="ai-lesion-item__head" @click="$emit('select', item)">
              <div class="ai-lesion-item__title">
                <span>{{ displayLesionTitle(item) }}</span>
                <span v-if="displayDetectionConf(item) != null" class="ai-lesion-item__conf">
                  检测 {{ (displayDetectionConf(item) * 100).toFixed(1) }}%
                </span>
              </div>
              <div
                v-if="item.classificationConfidence != null"
                class="ai-lesion-item__cls-conf"
              >
                分类 {{ (item.classificationConfidence * 100).toFixed(1) }}%
              </div>
              <div v-if="item.sliceIndex != null" class="ai-lesion-item__slice">
                层位(Instance): {{ item.instanceNumber != null ? item.instanceNumber : (item.sliceIndex + 1) }}
              </div>
              <div v-if="morphologyHints(item).length" class="ai-lesion-item__hints">
                <span
                  v-for="(hint, hi) in morphologyHints(item)"
                  :key="hi"
                  class="ai-lesion-hint"
                  :class="'ai-lesion-hint--' + hint.type"
                >{{ hint.text }}</span>
              </div>
            </div>
            <dl class="ai-lesion-item__metrics">
              <template v-for="(row, idx) in metricsLines(item)">
                <dt :key="'k-' + idx">{{ row.label }}</dt>
                <dd :key="'v-' + idx">{{ row.value }}</dd>
              </template>
            </dl>
            <div class="ai-lesion-item__actions">
              <el-button
                size="mini"
                :type="item.markerVisible !== false ? 'success' : 'info'"
                plain
                @click.stop="$emit('toggle-marker', item)"
              >
                {{ item.markerVisible !== false ? '隐藏标记' : '显示标记' }}
              </el-button>
              <el-button size="mini" type="primary" plain @click.stop="$emit('select', item)">
                定位到该层
              </el-button>
            </div>
          </li>
        </ul>
        <div v-else-if="screening" class="ai-lesion-empty">无结节框；请查看图像上的热力图</div>
        <div v-else class="ai-lesion-empty">暂无病灶数据</div>
      </div>
    </aside>
  </transition>
</template>

<script>
import { formatLesionMetricsLines, truncateUid, formatLesionDisplayLabel, formatDisclaimer, formatMorphologyHints } from '@/utils/lesionDetect'
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
    displayDisclaimer() {
      return formatDisclaimer(this.disclaimer)
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
    metricsLines(lesion) {
      return formatLesionMetricsLines(lesion)
    },
    displayDetectionConf(item) {
      if (item.detectionConfidence != null) return item.detectionConfidence
      return item.confidence
    },
    displayLesionTitle(item) {
      return formatLesionDisplayLabel(item)
    },
    morphologyHints(item) {
      return formatMorphologyHints(item)
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
  width: 320px;
  max-height: calc(100vh - 80px);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: rgba(28, 32, 40, 0.96);
  border: 1px solid rgba(103, 194, 58, 0.35);
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
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  font-weight: 600;
  color: #7dff7d;
  cursor: grab;
  background: rgba(28, 32, 40, 0.98);

  &:active {
    cursor: grabbing;
  }
}

.ai-lesion-panel__body {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
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

.ai-lesion-panel__meta {
  flex-shrink: 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
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
  color: #7dff7d;
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

.ai-lesion-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 12px;
  padding: 6px 12px 8px;
  font-size: 11px;
  color: #b0b6be;
}

.ai-lesion-legend__item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;

  &.dot--solid { background: rgba(255, 80, 60, 0.85); }
  &.dot--ggo { background: rgba(60, 180, 255, 0.85); }
  &.dot--mixed { background: rgba(200, 80, 255, 0.85); }
  &.dot--calc {
    background: rgba(255, 220, 60, 0.85);
    border-radius: 2px;
    transform: rotate(45deg);
  }
}

.ai-lesion-item__cls-conf {
  font-size: 11px;
  color: #7eb8ff;
  margin-bottom: 4px;
}

.ai-lesion-list {
  list-style: none;
  margin: 0;
  padding: 6px 0 12px;
}

.ai-lesion-item {
  padding: 10px 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.ai-lesion-item__head {
  cursor: pointer;

  &:hover .ai-lesion-item__title span:first-child {
    color: #7dff7d;
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

.ai-lesion-item__slice {
  font-size: 12px;
  color: #b8bcc6;
  margin-bottom: 6px;
}

.ai-lesion-item__hints {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 6px;
}

.ai-lesion-hint {
  display: inline-block;
  padding: 1px 6px;
  border-radius: 3px;
  font-size: 10px;
  line-height: 1.4;
  border: 1px solid transparent;

  &--pleural {
    color: #a8d4ff;
    background: rgba(64, 158, 255, 0.12);
    border-color: rgba(64, 158, 255, 0.25);
  }
  &--spiculation {
    color: #ffb8a8;
    background: rgba(245, 108, 108, 0.12);
    border-color: rgba(245, 108, 108, 0.25);
  }
  &--cavitation {
    color: #ffd080;
    background: rgba(230, 162, 60, 0.12);
    border-color: rgba(230, 162, 60, 0.25);
  }
  &--enhance {
    color: #c8a8ff;
    background: rgba(200, 80, 255, 0.12);
    border-color: rgba(200, 80, 255, 0.25);
  }
  &--lobulation {
    color: #b0b6be;
    background: rgba(255, 255, 255, 0.06);
    border-color: rgba(255, 255, 255, 0.1);
  }
}

.ai-lesion-item__metrics {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 2px 10px;
  margin: 0 0 8px;
  font-size: 12px;
  line-height: 1.45;

  dt {
    margin: 0;
    color: #8b93a7;
    white-space: nowrap;
  }

  dd {
    margin: 0;
    color: #dce1e8;
  }
}

.ai-lesion-item__actions {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.ai-lesion-empty {
  padding: 16px 12px;
  color: #8b93a7;
  text-align: center;
}
</style>
