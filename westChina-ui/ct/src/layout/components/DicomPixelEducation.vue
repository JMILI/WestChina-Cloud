<template>
  <div class="pixel-education">
    <div class="section-head">
      <i class="el-icon-picture-outline"></i>
      <span>像素 · HU · 窗宽窗位 · AI 识别（通俗图解）</span>
    </div>
    <p class="section-intro">
      下面用示意图说明：DICOM 里存的到底是什么、如何变成 HU、医生调窗与 AI 分析有何不同。
      资料已按 DICOM 标准与本系统实现校对。
    </p>

    <div class="flow-steps">
      <div v-for="(step, i) in flowSteps" :key="i" class="flow-step">
        <div class="flow-step__title">{{ step.title }}</div>
        <div class="flow-step__text">{{ step.text }}</div>
      </div>
    </div>

    <div class="canvas-grid">
      <div class="canvas-card">
        <div class="canvas-card__title">DICOM = 标签 + 像素</div>
        <canvas ref="fileCanvas" class="edu-canvas"></canvas>
      </div>
      <div class="canvas-card">
        <div class="canvas-card__title">存储值 → HU 换算</div>
        <canvas ref="huConvertCanvas" class="edu-canvas"></canvas>
      </div>
      <div class="canvas-card canvas-card--wide">
        <div class="canvas-card__title">HU 常见组织对照尺（约值，因人而异）</div>
        <canvas ref="huScaleCanvas" class="edu-canvas edu-canvas--wide"></canvas>
      </div>
      <div class="canvas-card canvas-card--wide">
        <div class="canvas-card__title">窗宽窗位：同一张 CT，不同「观察滤镜」</div>
        <canvas ref="windowCanvas" class="edu-canvas edu-canvas--wide"></canvas>
      </div>
      <div class="canvas-card canvas-card--full">
        <div class="canvas-card__title">数据流向：AI 看 HU，人眼看灰度</div>
        <canvas ref="pathCanvas" class="edu-canvas edu-canvas--path"></canvas>
      </div>
    </div>

    <div class="accuracy-box">
      <div class="accuracy-box__title">📌 阅读提示（相对网络科普的校正）</div>
      <ul>
        <li v-for="(note, i) in accuracyNotes" :key="i">{{ note }}</li>
      </ul>
    </div>
  </div>
</template>

<script>
import {
  DICOM_PIXEL_ACCURACY_NOTES,
  DICOM_PIXEL_FLOW_STEPS,
  HU_REFERENCE_BANDS,
  WINDOW_PRESETS
} from '@/constants/dicomPixelEducation'

const FILE_W = 340
const FILE_H = 220
const CONV_W = 480
const CONV_H = 190
const SCALE_W = 720
const SCALE_H = 130
const WIN_W = 720
const WIN_H = 200
const PATH_W = 720
const PATH_H = 250

export default {
  name: 'DicomPixelEducation',
  data() {
    return {
      accuracyNotes: DICOM_PIXEL_ACCURACY_NOTES,
      flowSteps: DICOM_PIXEL_FLOW_STEPS
    }
  },
  mounted() {
    this.$nextTick(() => this.drawAll())
  },
  methods: {
    drawAll() {
      this.setupCanvas(this.$refs.fileCanvas, FILE_W, FILE_H, this.drawFileStructure)
      this.setupCanvas(this.$refs.huConvertCanvas, CONV_W, CONV_H, this.drawHuConvert)
      this.setupCanvas(this.$refs.huScaleCanvas, SCALE_W, SCALE_H, this.drawHuScale)
      this.setupCanvas(this.$refs.windowCanvas, WIN_W, WIN_H, this.drawWindowLevel)
      this.setupCanvas(this.$refs.pathCanvas, PATH_W, PATH_H, this.drawDataPaths)
    },
    setupCanvas(canvas, w, h, drawFn) {
      if (!canvas) return
      const dpr = Math.min(window.devicePixelRatio || 2, 3)
      canvas.width = w * dpr
      canvas.height = h * dpr
      canvas.style.width = w + 'px'
      canvas.style.height = h + 'px'
      const ctx = canvas.getContext('2d')
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
      ctx.imageSmoothingEnabled = true
      ctx.imageSmoothingQuality = 'high'
      drawFn(ctx, w, h)
    },
    roundRect(ctx, x, y, w, h, r) {
      ctx.beginPath()
      ctx.moveTo(x + r, y)
      ctx.lineTo(x + w - r, y)
      ctx.quadraticCurveTo(x + w, y, x + w, y + r)
      ctx.lineTo(x + w, y + h - r)
      ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h)
      ctx.lineTo(x + r, y + h)
      ctx.quadraticCurveTo(x, y + h, x, y + h - r)
      ctx.lineTo(x, y + r)
      ctx.quadraticCurveTo(x, y, x + r, y)
      ctx.closePath()
    },
    drawArrow(ctx, x1, y1, x2, y2, color) {
      ctx.strokeStyle = color
      ctx.fillStyle = color
      ctx.lineWidth = 2
      ctx.beginPath()
      ctx.moveTo(x1, y1)
      ctx.lineTo(x2, y2)
      ctx.stroke()
      const a = Math.atan2(y2 - y1, x2 - x1)
      const len = 8
      ctx.beginPath()
      ctx.moveTo(x2, y2)
      ctx.lineTo(x2 - len * Math.cos(a - 0.45), y2 - len * Math.sin(a - 0.45))
      ctx.lineTo(x2 - len * Math.cos(a + 0.45), y2 - len * Math.sin(a + 0.45))
      ctx.closePath()
      ctx.fill()
    },
    drawFileStructure(ctx, w, h) {
      ctx.fillStyle = '#1e2229'
      ctx.fillRect(0, 0, w, h)

      const leftW = 128
      ctx.fillStyle = 'rgba(91,156,245,0.15)'
      ctx.strokeStyle = '#5b9cf5'
      ctx.lineWidth = 2
      this.roundRect(ctx, 12, 24, leftW, h - 48, 8)
      ctx.fill()
      ctx.stroke()
      ctx.fillStyle = '#e8eaed'
      ctx.font = 'bold 12px sans-serif'
      ctx.fillText('标签 Meta', 22, 48)
      ctx.fillStyle = '#9aa3b2'
      ctx.font = '10px sans-serif'
      ;['患者姓名', '检查日期', '层厚', 'Slope', 'Intercept'].forEach((t, i) => {
        ctx.fillText('• ' + t, 20, 68 + i * 16)
      })

      const rightX = 160
      const gridSize = 56
      ctx.fillStyle = 'rgba(230,162,60,0.12)'
      ctx.strokeStyle = '#e6a23c'
      this.roundRect(ctx, rightX, 24, w - rightX - 12, h - 48, 8)
      ctx.fill()
      ctx.stroke()
      ctx.fillStyle = '#e8eaed'
      ctx.font = 'bold 12px sans-serif'
      ctx.fillText('像素 Pixel Data', rightX + 12, 48)
      ctx.font = '10px sans-serif'
      ctx.fillStyle = '#9aa3b2'
      ctx.fillText('整数矩阵，如 512×512', rightX + 12, 64)

      const gx = rightX + 24
      const gy = 78
      for (let r = 0; r < 6; r++) {
        for (let c = 0; c < 6; c++) {
          const v = 120 + (r + c) * 15
          const gray = Math.min(220, v)
          ctx.fillStyle = `rgb(${gray},${gray},${gray})`
          ctx.fillRect(gx + c * 9, gy + r * 9, 8, 8)
        }
      }
      ctx.fillStyle = '#8b93a7'
      ctx.fillText('每个格子 = 一个存储整数', rightX + 12, h - 36)

      this.drawArrow(ctx, 12 + leftW + 4, h / 2, rightX - 4, h / 2, '#67c23a')
      ctx.fillStyle = '#67c23a'
      ctx.font = '10px sans-serif'
      ctx.textAlign = 'center'
      ctx.fillText('不是灰度屏', (12 + leftW + rightX) / 2, h / 2 - 8)
      ctx.textAlign = 'left'
    },
    drawHuConvert(ctx, w, h) {
      ctx.fillStyle = '#1e2229'
      ctx.fillRect(0, 0, w, h)

      const box = (x, y, title, value, color, bw = 88) => {
        ctx.fillStyle = color + '22'
        ctx.strokeStyle = color
        ctx.lineWidth = 2
        this.roundRect(ctx, x, y, bw, 58, 6)
        ctx.fill()
        ctx.stroke()
        ctx.fillStyle = '#e8eaed'
        ctx.font = '11px sans-serif'
        ctx.textAlign = 'center'
        ctx.fillText(title, x + bw / 2, y + 22)
        ctx.font = 'bold 15px monospace'
        ctx.fillText(value, x + bw / 2, y + 44)
        ctx.textAlign = 'left'
      }

      ctx.fillStyle = '#7eb8ff'
      ctx.font = 'bold 12px sans-serif'
      ctx.textAlign = 'center'
      ctx.fillText('HU = 存储值 × Slope + Intercept', w / 2, 24)
      ctx.fillStyle = '#8b93a7'
      ctx.font = '10px sans-serif'
      ctx.fillText('例：200 × 1 + (-1024) = -824 HU（偏肺组织密度）', w / 2, 42)

      const y = 72
      box(16, y, '存储值', '200', '#e6a23c')
      box(120, y, '× Slope', '1', '#909399')
      box(224, y, '+ Intercept', '-1024', '#909399', 100)
      box(348, y, '= HU', '-824', '#67c23a')

      this.drawArrow(ctx, 104, y + 29, 120, y + 29, '#c5cad3')
      this.drawArrow(ctx, 208, y + 29, 224, y + 29, '#c5cad3')
      this.drawArrow(ctx, 324, y + 29, 348, y + 29, '#67c23a')

      ctx.fillStyle = '#8b93a7'
      ctx.font = '10px sans-serif'
      ctx.textAlign = 'center'
      ctx.fillText('水 = 0 HU　空气 ≈ -1000 HU　骨 > +300 HU', w / 2, h - 16)
      ctx.textAlign = 'left'
    },
    drawHuScale(ctx, w, h) {
      const minHu = -1000
      const maxHu = 1000
      const barY = 28
      const barH = 28
      const barX = 12
      const barW = w - 24

      ctx.fillStyle = '#1e2229'
      ctx.fillRect(0, 0, w, h)

      const grad = ctx.createLinearGradient(barX, 0, barX + barW, 0)
      grad.addColorStop(0, '#0a0a12')
      grad.addColorStop(0.15, '#2a4a6a')
      grad.addColorStop(0.35, '#5a6a5a')
      grad.addColorStop(0.5, '#6a8a9a')
      grad.addColorStop(0.65, '#8a7a6a')
      grad.addColorStop(0.85, '#d0c8b8')
      grad.addColorStop(1, '#f0ece4')
      ctx.fillStyle = grad
      this.roundRect(ctx, barX, barY, barW, barH, 4)
      ctx.fill()

      HU_REFERENCE_BANDS.forEach((band, i) => {
        const t = (band.hu - minHu) / (maxHu - minHu)
        const x = barX + t * barW
        ctx.strokeStyle = '#fff'
        ctx.lineWidth = 2
        ctx.beginPath()
        ctx.moveTo(x, barY - 4)
        ctx.lineTo(x, barY + barH + 4)
        ctx.stroke()
        const labelY = barY + barH + 18 + (i % 2) * 14
        ctx.fillStyle = '#e8eaed'
        ctx.font = '10px sans-serif'
        ctx.textAlign = 'center'
        ctx.fillText(band.label, x, labelY)
        ctx.fillStyle = '#8b93a7'
        ctx.font = '9px sans-serif'
        ctx.fillText(String(band.hu), x, labelY + 12)
      })

      ctx.fillStyle = '#7eb8ff'
      ctx.font = '10px sans-serif'
      ctx.textAlign = 'left'
      ctx.fillText('-1000 HU', barX, barY - 8)
      ctx.textAlign = 'right'
      ctx.fillText('+1000 HU', barX + barW, barY - 8)
    },
    huToGray(hu, wl, ww) {
      const low = wl - ww / 2
      const high = wl + ww / 2
      if (hu <= low) return 0
      if (hu >= high) return 255
      return Math.round(((hu - low) / ww) * 255)
    },
    drawWindowLevel(ctx, w, h) {
      ctx.fillStyle = '#1e2229'
      ctx.fillRect(0, 0, w, h)

      const drawStrip = (x, y, preset, sampleHus) => {
        const stripW = 200
        const stripH = 44
        const cardW = stripW + 24
        const cardH = stripH + 58
        ctx.fillStyle = '#23272f'
        this.roundRect(ctx, x, y, cardW, cardH, 6)
        ctx.fill()
        ctx.fillStyle = '#e8eaed'
        ctx.font = 'bold 11px sans-serif'
        ctx.fillText(preset.name, x + 10, y + 18)
        ctx.fillStyle = '#9aa3b2'
        ctx.font = '9px sans-serif'
        ctx.fillText(`窗位 ${preset.level}  窗宽 ${preset.width}`, x + 10, y + 32)

        for (let i = 0; i < stripW; i++) {
          const hu = sampleHus[Math.floor((i / stripW) * sampleHus.length)]
          const g = this.huToGray(hu, preset.level, preset.width)
          ctx.fillStyle = `rgb(${g},${g},${g})`
          ctx.fillRect(x + 10 + i, y + 40, 1, stripH)
        }
        ctx.fillStyle = '#b0b8c4'
        ctx.font = '9px sans-serif'
        const desc = preset.desc.length > 22 ? preset.desc.slice(0, 22) + '…' : preset.desc
        ctx.fillText(desc, x + 10, y + stripH + 52)
      }

      const sample = []
      for (let i = 0; i < 200; i++) {
        const t = i / 200
        if (t < 0.3) sample.push(-900 + t * 400)
        else if (t < 0.55) sample.push(-750 + (t - 0.3) * 200)
        else if (t < 0.75) sample.push(20 + (t - 0.55) * 150)
        else sample.push(200 + (t - 0.75) * 800)
      }

      drawStrip(12, 20, WINDOW_PRESETS[0], sample)
      drawStrip(248, 20, WINDOW_PRESETS[1], sample)
      drawStrip(484, 20, WINDOW_PRESETS[2], sample)

      ctx.fillStyle = '#e6a23c'
      ctx.font = '10px sans-serif'
      ctx.fillText('同一组 HU 数据，换窗后屏幕灰度不同（文件内 HU 不变）', 12, h - 12)
    },
    drawDataPaths(ctx, w, h) {
      ctx.fillStyle = '#1e2229'
      ctx.fillRect(0, 0, w, h)

      const topY = 36
      const cx = w / 2
      ctx.fillStyle = 'rgba(103,194,58,0.2)'
      ctx.strokeStyle = '#67c23a'
      ctx.lineWidth = 2
      this.roundRect(ctx, cx - 70, topY, 140, 48, 8)
      ctx.fill()
      ctx.stroke()
      ctx.fillStyle = '#e8eaed'
      ctx.font = 'bold 12px sans-serif'
      ctx.textAlign = 'center'
      ctx.fillText('HU 体数据 (3D)', cx, topY + 20)
      ctx.font = '10px sans-serif'
      ctx.fillText('DICOM 像素 + Rescale', cx, topY + 36)

      const branchY = 110
      const boxW = 280
      const boxH = 76
      const aiX = w / 2 - boxW - 24
      const eyeX = w / 2 + 24

      this.drawArrow(ctx, cx, topY + 48, cx, branchY - 8, '#67c23a')
      this.drawArrow(ctx, cx, branchY - 8, aiX + boxW / 2, branchY + 12, '#5b9cf5')
      this.drawArrow(ctx, cx, branchY - 8, eyeX + boxW / 2, branchY + 12, '#e6a23c')

      ctx.fillStyle = 'rgba(91,156,245,0.2)'
      ctx.strokeStyle = '#5b9cf5'
      this.roundRect(ctx, aiX, branchY + 12, boxW, boxH, 8)
      ctx.fill()
      ctx.stroke()
      ctx.fillStyle = '#7eb8ff'
      ctx.font = 'bold 12px sans-serif'
      ctx.fillText('AI 识别路径', aiX + boxW / 2, branchY + 32)
      ctx.fillStyle = '#c5cad3'
      ctx.font = '10px sans-serif'
      ctx.fillText('读 HU → 肺区分割 → 找可疑区域', aiX + boxW / 2, branchY + 50)
      ctx.fillText('输出：病灶框 / 轮廓', aiX + boxW / 2, branchY + 66)

      ctx.fillStyle = 'rgba(230,162,60,0.2)'
      ctx.strokeStyle = '#e6a23c'
      this.roundRect(ctx, eyeX, branchY + 12, boxW, boxH, 8)
      ctx.fill()
      ctx.stroke()
      ctx.fillStyle = '#f0c090'
      ctx.font = 'bold 12px sans-serif'
      ctx.fillText('医生阅片路径', eyeX + boxW / 2, branchY + 32)
      ctx.fillStyle = '#c5cad3'
      ctx.font = '10px sans-serif'
      ctx.fillText('HU → 窗宽窗位 → 0~255 灰度', eyeX + boxW / 2, branchY + 50)
      ctx.fillText('调窗 = 换观察滤镜', eyeX + boxW / 2, branchY + 66)

      ctx.fillStyle = '#8b93a7'
      ctx.font = '10px sans-serif'
      ctx.textAlign = 'center'
      ctx.fillText('AI 结果叠加到当前阅片图像（不改变原始 HU）', cx, h - 16)
      ctx.textAlign = 'left'
    }
  }
}
</script>

<style lang="scss" scoped>
.pixel-education {
  margin-bottom: 18px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.section-head {
  font-size: 14px;
  font-weight: 600;
  color: #e8eaed;
  margin-bottom: 8px;

  i {
    color: #67c23a;
    margin-right: 6px;
  }
}

.section-intro {
  font-size: 12px;
  color: #8b93a7;
  line-height: 1.6;
  margin: 0 0 12px;
}

.flow-steps {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  margin-bottom: 14px;
}

.flow-step {
  background: #23272f;
  border-radius: 8px;
  padding: 10px 12px;
  border-left: 3px solid #67c23a;

  &__title {
    font-size: 12px;
    font-weight: 600;
    color: #7eb8ff;
    margin-bottom: 4px;
  }

  &__text {
    font-size: 11px;
    color: #b8bcc6;
    line-height: 1.55;
  }
}

.canvas-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin-bottom: 12px;
}

.canvas-card {
  background: #14171c;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  padding: 8px 10px 10px;

  &--wide {
    grid-column: span 2;
  }

  &--full {
    grid-column: span 2;
  }

  &__title {
    font-size: 11px;
    color: #9aa3b2;
    margin-bottom: 6px;
  }
}

.edu-canvas {
  display: block;
  width: 100%;
  max-width: 100%;

  &--wide {
    min-height: 130px;
  }

  &--path {
    min-height: 250px;
  }
}

.accuracy-box {
  background: rgba(103, 194, 58, 0.08);
  border: 1px solid rgba(103, 194, 58, 0.2);
  border-radius: 8px;
  padding: 10px 14px;

  &__title {
    font-size: 12px;
    font-weight: 600;
    color: #95d475;
    margin-bottom: 8px;
  }

  ul {
    margin: 0;
    padding-left: 18px;
    font-size: 11px;
    color: #b8c5b0;
    line-height: 1.65;
  }
}
</style>
