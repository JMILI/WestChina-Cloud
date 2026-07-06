<template>
  <canvas
    v-if="visible"
    ref="heatmapCanvas"
    class="lesion-heatmap-canvas"
    :style="canvasStyle"
  />
</template>

<script>
import * as cornerstone from 'cornerstone-core'

export default {
  name: 'LesionHeatmapOverlay',
  props: {
    element: { type: HTMLElement, default: null },
    heatmap: { type: Object, default: null },
    sliceIndex: { type: Number, default: null }
  },
  data() {
    return {
      visible: false
    }
  },
  computed: {
    canvasStyle() {
      if (!this.element) return {}
      return {
        position: 'absolute',
        top: '0',
        left: '0',
        width: this.element.offsetWidth + 'px',
        height: this.element.offsetHeight + 'px',
        pointerEvents: 'none',
        zIndex: 100
      }
    }
  },
  watch: {
    heatmap: {
      handler() { this.renderHeatmap() },
      deep: true
    },
    sliceIndex() { this.checkVisibility() }
  },
  mounted() {
    this.checkVisibility()
    this.listenImageRendered()
  },
  beforeDestroy() {
    this.unlistenImageRendered()
  },
  methods: {
    getCurrentSlice() {
      if (!this.element) return null
      try {
        const ee = cornerstone.getEnabledElement(this.element)
        if (ee && ee.stack) return ee.stack.currentImageIdIndex
      } catch (e) { /* ignore */ }
      return null
    },
    checkVisibility() {
      const cur = this.getCurrentSlice()
      this.visible = cur != null && cur === this.sliceIndex && !!this.heatmap
    },
    listenImageRendered() {
      if (!this.element) return
      this._onImageRendered = () => {
        this.checkVisibility()
        if (this.visible) this.renderHeatmap()
      }
      this.element.addEventListener('cornerstoneimagerendered', this._onImageRendered)
    },
    unlistenImageRendered() {
      if (this.element && this._onImageRendered) {
        this.element.removeEventListener('cornerstoneimagerendered', this._onImageRendered)
      }
    },
    renderHeatmap() {
      if (!this.visible || !this.heatmap) return

      const canvas = this.$refs.heatmapCanvas
      if (!canvas) return

      const w = this.heatmap.width || 64
      const h = this.heatmap.height || 64
      const values = this.heatmap.values || []
      if (!values.length) return

      canvas.width = this.element.offsetWidth || 512
      canvas.height = this.element.offsetHeight || 512

      const ctx = canvas.getContext('2d')
      const imgData = ctx.createImageData(canvas.width, canvas.height)

      for (let py = 0; py < canvas.height; py++) {
        const sy = (py + 0.5) / canvas.height * h - 0.5
        for (let px = 0; px < canvas.width; px++) {
          const sx = (px + 0.5) / canvas.width * w - 0.5
          const x0 = Math.floor(sx)
          const y0 = Math.floor(sy)
          const x1 = Math.min(w - 1, x0 + 1)
          const y1 = Math.min(h - 1, y0 + 1)
          const fx = sx - x0
          const fy = sy - y0
          const v00 = values[y0 * w + x0] || 0
          const v10 = values[y0 * w + x1] || 0
          const v01 = values[y1 * w + x0] || 0
          const v11 = values[y1 * w + x1] || 0
          const v = Math.max(0, Math.min(1,
            (1 - fx) * (1 - fy) * v00 + fx * (1 - fy) * v10 +
            (1 - fx) * fy * v01 + fx * fy * v11
          ))
          if (v < 0.08) continue

          const r = Math.floor(v * 255)
          const b = Math.floor((1 - v) * 255)
          const g = Math.floor(50 * (1 - Math.abs(v - 0.5) * 2))

          const pi = (py * canvas.width + px) * 4
          imgData.data[pi] = r
          imgData.data[pi + 1] = g
          imgData.data[pi + 2] = b
          imgData.data[pi + 3] = Math.floor(v * 110)
        }
      }
      ctx.putImageData(imgData, 0, 0)
    }
  }
}
</script>

<style scoped>
.lesion-heatmap-canvas {
  display: block;
}
</style>
