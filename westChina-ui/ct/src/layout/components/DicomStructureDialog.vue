<template>
  <el-dialog
    title="DICOM 医学影像数据结构"
    :visible.sync="dialogVisible"
    width="1000px"
    top="4vh"
    custom-class="dicom-structure-dialog"
    append-to-body
    @opened="onDialogOpened"
  >
    <div class="dicom-dialog-body">
      <div class="diagram-section">
        <div class="diagram-title">
          <i class="el-icon-share"></i>
          层级结构图 · 含临床场景示例
        </div>
        <div class="diagram-wrap">
          <canvas ref="diagramCanvas" class="diagram-canvas"></canvas>
        </div>
        <div class="diagram-legend">
          <span v-for="item in legendItems" :key="item.label" class="legend-item">
            <i class="legend-dot" :style="{ background: item.color }"></i>{{ item.label }}
          </span>
        </div>
      </div>

      <div class="related-ie-row">
        <div
          v-for="ie in relatedIE"
          :key="ie.title"
          class="related-ie-card"
          :style="{ borderColor: ie.color }"
        >
          <span class="related-title" :style="{ color: ie.color }">{{ ie.title }}</span>
          <span class="related-desc">{{ ie.desc }}</span>
        </div>
      </div>

      <div class="hierarchy-cards">
        <div
          v-for="level in hierarchy"
          :key="level.id"
          class="level-card"
          :style="{ borderLeftColor: level.color }"
        >
          <div class="level-head">
            <span class="level-icon">{{ level.icon }}</span>
            <div>
              <div class="level-title" :style="{ color: level.color }">{{ level.title }}</div>
              <div class="level-sub">{{ level.subtitle }}</div>
            </div>
          </div>
          <ul class="level-rules">
            <li v-for="(rule, idx) in level.rules" :key="idx">{{ rule }}</li>
          </ul>
          <p v-if="level.uid" class="level-uid">{{ level.uid }}</p>
          <p class="level-scenario"><strong>场景：</strong>{{ level.scenario }}</p>
        </div>
      </div>

      <dicom-pixel-education ref="pixelEducation" />

      <el-collapse v-model="activePanels" class="field-collapse">
        <el-collapse-item
          v-for="section in sections"
          :key="section.key"
          :title="section.label"
          :name="section.key"
        >
          <p class="section-summary">{{ section.summary }}</p>
          <div class="field-table">
            <div v-for="field in section.fields" :key="field.tag" class="field-row">
              <div class="field-name">{{ field.name }}</div>
              <div class="field-tag">{{ field.tag }}</div>
              <div class="field-meaning">{{ field.meaning }}</div>
            </div>
          </div>
        </el-collapse-item>
      </el-collapse>

      <div class="relation-note">
        <strong>标准说明（DICOM PS3.3 / PS3.4）：</strong>
        {{ relationSummary }}
        点击顶部菜单项可在影像四角叠加显示对应字段；鼠标悬停菜单可查看各字段释义。
      </div>
    </div>
  </el-dialog>
</template>

<script>
import {
  DICOM_HIERARCHY,
  DICOM_INFO_SECTIONS,
  DICOM_RELATED_IE,
  DICOM_CLINICAL_SCENARIO,
  DICOM_RELATION_SUMMARY
} from '@/constants/dicomStructure'
import DicomPixelEducation from './DicomPixelEducation'

const LOGICAL_W = 1040
const LOGICAL_H = 430

export default {
  name: 'DicomStructureDialog',
  components: { DicomPixelEducation },
  props: {
    visible: { type: Boolean, default: false }
  },
  data() {
    return {
      hierarchy: DICOM_HIERARCHY,
      sections: DICOM_INFO_SECTIONS,
      relatedIE: DICOM_RELATED_IE,
      scenario: DICOM_CLINICAL_SCENARIO,
      relationSummary: DICOM_RELATION_SUMMARY,
      activePanels: [],
      legendItems: [
        { label: 'Patient 病人', color: '#5b9cf5' },
        { label: 'Study 检查', color: '#67c23a' },
        { label: 'Series 序列', color: '#e6a23c' },
        { label: 'Instance 实例', color: '#f56c6c' },
        { label: 'Equipment 设备', color: '#b37feb' },
        { label: 'Frame of Reference', color: '#36cfc9' }
      ]
    }
  },
  computed: {
    dialogVisible: {
      get() { return this.visible },
      set(val) { this.$emit('update:visible', val) }
    }
  },
  methods: {
    onDialogOpened() {
      this.$nextTick(() => {
        this.setupCanvas()
        this.drawDiagram()
        if (this.$refs.pixelEducation) {
          this.$refs.pixelEducation.drawAll()
        }
      })
    },
    setupCanvas() {
      const canvas = this.$refs.diagramCanvas
      if (!canvas) return
      const dpr = Math.min(window.devicePixelRatio || 2, 3)
      canvas.width = LOGICAL_W * dpr
      canvas.height = LOGICAL_H * dpr
      canvas.style.width = LOGICAL_W + 'px'
      canvas.style.height = LOGICAL_H + 'px'
      const ctx = canvas.getContext('2d')
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
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
    drawArrow(ctx, x1, y1, x2, y2, color, width = 2) {
      ctx.strokeStyle = color
      ctx.fillStyle = color
      ctx.lineWidth = width
      ctx.beginPath()
      ctx.moveTo(x1, y1)
      ctx.lineTo(x2, y2)
      ctx.stroke()
      const angle = Math.atan2(y2 - y1, x2 - x1)
      const len = 9
      ctx.beginPath()
      ctx.moveTo(x2, y2)
      ctx.lineTo(x2 - len * Math.cos(angle - 0.45), y2 - len * Math.sin(angle - 0.45))
      ctx.lineTo(x2 - len * Math.cos(angle + 0.45), y2 - len * Math.sin(angle + 0.45))
      ctx.closePath()
      ctx.fill()
    },
    drawBox(ctx, x, y, w, h, color, title, lines, opts = {}) {
      const r = 10
      ctx.fillStyle = color + (opts.fillAlpha || '28')
      ctx.strokeStyle = color
      ctx.lineWidth = opts.lineWidth || 2
      this.roundRect(ctx, x, y, w, h, r)
      ctx.fill()
      ctx.stroke()

      ctx.fillStyle = '#f0f2f5'
      ctx.font = `bold ${opts.titleSize || 13}px "Microsoft YaHei", sans-serif`
      ctx.textAlign = 'left'
      ctx.textBaseline = 'top'
      ctx.fillText(title, x + 12, y + 10)

      ctx.fillStyle = '#b8bcc6'
      ctx.font = `${opts.fontSize || 11}px "Microsoft YaHei", sans-serif`
      lines.forEach((line, i) => {
        ctx.fillText(line, x + 12, y + 30 + i * 16)
      })
    },
    drawDiagram() {
      const canvas = this.$refs.diagramCanvas
      if (!canvas) return
      const ctx = canvas.getContext('2d')
      const w = LOGICAL_W
      const h = LOGICAL_H

      // background
      const bg = ctx.createLinearGradient(0, 0, 0, h)
      bg.addColorStop(0, '#1a1e26')
      bg.addColorStop(1, '#222830')
      ctx.fillStyle = bg
      ctx.fillRect(0, 0, w, h)

      // divider
      ctx.strokeStyle = 'rgba(255,255,255,0.06)'
      ctx.lineWidth = 1
      ctx.beginPath()
      ctx.moveTo(520, 12)
      ctx.lineTo(520, h - 12)
      ctx.stroke()

      // left label
      ctx.fillStyle = '#7eb8ff'
      ctx.font = 'bold 13px "Microsoft YaHei", sans-serif'
      ctx.textAlign = 'left'
      ctx.fillText('临床场景示例', 24, 16)
      ctx.fillStyle = '#6b7280'
      ctx.font = '11px "Microsoft YaHei", sans-serif'
      ctx.fillText(this.scenario.title, 24, 34)

      const s = this.scenario
      // Patient box
      this.drawBox(ctx, 24, 52, 460, 58, '#5b9cf5', '👤 病人 Patient', [
        `姓名 ${s.patient.name}  ·  ID ${s.patient.id}  ·  ${s.patient.sex}  ·  ${s.patient.age}`
      ])
      this.drawArrow(ctx, 254, 110, 254, 128, '#5b9cf5')

      // Study box
      this.drawBox(ctx, 24, 128, 460, 58, '#67c23a', '📋 检查 Study', [
        `${s.study.desc}  ·  日期 ${s.study.date}  ·  申请号 ${s.study.accession}`,
        'Study Instance UID 标识本次完整检查'
      ])
      this.drawArrow(ctx, 254, 186, 254, 204, '#67c23a')

      // Series row
      const seriesY = 204
      const seriesW = 145
      const gap = 12
      s.seriesList.forEach((ser, i) => {
        const x = 24 + i * (seriesW + gap)
        this.drawBox(ctx, x, seriesY, seriesW, 72, '#e6a23c', `序列 ${ser.num}`, [
          ser.desc,
          `${ser.modality} · ${ser.instances} 张 Instance`
        ], { fontSize: 10, titleSize: 12 })
        this.drawArrow(ctx, 254, 186, x + seriesW / 2, seriesY, 'rgba(230,162,60,0.5)', 1.5)
      })

      // Instance strip under series 2
      const instY = 296
      this.drawBox(ctx, 181, instY, 145, 88, '#f56c6c', '🖼 Instance 实例', [
        'Axial 序列中的单张断层',
        'Inst #1  #2  …  #280',
        '每张 = 一个 .dcm 文件',
        '含 Pixel Data 像素矩阵'
      ], { fontSize: 10, titleSize: 12 })

      // Equipment
      this.drawBox(ctx, 24, instY, 145, 56, '#b37feb', '⚙ 设备 Equipment', [
        'Siemens CT  ·  同 Series 共享'
      ], { fontSize: 10, titleSize: 12 })
      this.drawArrow(ctx, 94, 276, 94, instY, '#b37feb', 1.5)

      // Frame of Reference
      this.drawBox(ctx, 339, instY, 145, 56, '#36cfc9', '◎ 参考坐标 FoR', [
        '同坐标系可 MPR / 3D 重建'
      ], { fontSize: 10, titleSize: 12 })

      // ===== Right: formal model =====
      ctx.fillStyle = '#7eb8ff'
      ctx.font = 'bold 13px "Microsoft YaHei", sans-serif'
      ctx.fillText('DICOM 标准层级（Patient-Root）', 544, 16)

      const levels = [
        { y: 48, color: '#5b9cf5', title: 'Patient 病人', sub: '1 人 → 多次检查', w: 460 },
        { y: 118, color: '#67c23a', title: 'Study 检查', sub: '1 次检查 → 多个序列', w: 420 },
        { y: 188, color: '#e6a23c', title: 'Series 序列', sub: '1 个序列 → 多张图像', w: 380 },
        { y: 258, color: '#f56c6c', title: 'Instance 实例', sub: '1 个文件 → 像素数据', w: 340 }
      ]

      levels.forEach((lv, i) => {
        const x = 544 + i * 18
        this.drawBox(ctx, x, lv.y, lv.w, 56, lv.color, lv.title, [lv.sub], { titleSize: 14 })
        if (i < levels.length - 1) {
          const nx = levels[i + 1]
          this.drawArrow(
            ctx,
            x + lv.w / 2, lv.y + 56,
            nx.x + nx.w / 2, nx.y,
            lv.color, 2
          )
          ctx.fillStyle = '#8b93a7'
          ctx.font = 'bold 10px sans-serif'
          ctx.textAlign = 'center'
          ctx.fillText('1 : N', x + lv.w / 2 + 9, lv.y + 70)
        }
      })

      // Pixel data note
      ctx.fillStyle = 'rgba(144,147,153,0.25)'
      ctx.strokeStyle = '#909399'
      ctx.lineWidth = 1.5
      this.roundRect(ctx, 562, 328, 320, 56, 8)
      ctx.fill()
      ctx.stroke()
      ctx.fillStyle = '#c5cad3'
      ctx.font = '12px "Microsoft YaHei", sans-serif'
      ctx.textAlign = 'center'
      ctx.fillText('Pixel Data（Instance 内部，非独立 Q/R 层级）', 722, 348)
      ctx.font = '10px "Microsoft YaHei", sans-serif'
      ctx.fillStyle = '#8b93a7'
      ctx.fillText('存储整数 → Rescale → HU → 窗宽窗位 → 屏幕灰度', 722, 368)

      // PACS note
      ctx.fillStyle = '#90959d'
      ctx.font = '10px "Microsoft YaHei", sans-serif'
      ctx.textAlign = 'left'
      ctx.fillText('PACS 归档路径：Patient ID → Study UID → Series UID → Instance UID / Instance Number', 544, 408)
    }
  }
}
</script>

<style lang="scss">
.dicom-structure-dialog {
  .el-dialog {
    background: #1a1d23;
    border-radius: 10px;
  }

  .el-dialog__header {
    background: #23272f;
    padding: 14px 20px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);

    .el-dialog__title {
      color: #e8eaed;
      font-size: 16px;
      font-weight: 600;
    }

    .el-dialog__headerbtn .el-dialog__close {
      color: #aaa;
    }
  }

  .el-dialog__body {
    padding: 16px 20px 20px;
    background: #1a1d23;
    color: #d0d4da;
    max-height: 78vh;
    overflow-y: auto;
  }
}
</style>

<style lang="scss" scoped>
.dicom-dialog-body {
  .diagram-section {
    margin-bottom: 14px;
  }

  .diagram-title {
    font-size: 13px;
    color: #8b93a7;
    margin-bottom: 8px;

    i {
      color: #5b9cf5;
      margin-right: 4px;
    }
  }

  .diagram-wrap {
    border-radius: 10px;
    overflow: auto;
    border: 1px solid rgba(255, 255, 255, 0.08);
    background: #14171c;
  }

  .diagram-canvas {
    display: block;
    max-width: 100%;
  }

  .diagram-legend {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-top: 8px;
    padding: 0 4px;

    .legend-item {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      font-size: 11px;
      color: #8b93a7;
    }

    .legend-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      display: inline-block;
    }
  }

  .related-ie-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    margin-bottom: 14px;
  }

  .related-ie-card {
    background: #23272f;
    border-radius: 8px;
    padding: 10px 12px;
    border-left: 3px solid;

    .related-title {
      display: block;
      font-size: 12px;
      font-weight: 600;
      margin-bottom: 4px;
    }

    .related-desc {
      font-size: 11px;
      color: #8b93a7;
      line-height: 1.45;
    }
  }

  .hierarchy-cards {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
    margin-bottom: 16px;
  }

  .level-card {
    background: #23272f;
    border-radius: 8px;
    padding: 12px 14px;
    border-left: 3px solid;

    .level-head {
      display: flex;
      align-items: flex-start;
      gap: 8px;
      margin-bottom: 8px;
    }

    .level-icon {
      font-size: 20px;
      line-height: 1;
    }

    .level-title {
      font-size: 14px;
      font-weight: 600;
    }

    .level-sub {
      font-size: 11px;
      color: #8b93a7;
      margin-top: 2px;
    }

    .level-rules {
      margin: 0 0 8px;
      padding-left: 18px;
      font-size: 11px;
      color: #c5cad3;
      line-height: 1.55;

      li {
        margin-bottom: 3px;
      }
    }

    .level-uid {
      font-size: 11px;
      color: #7eb8ff;
      margin: 0 0 6px;
      font-family: monospace;
    }

    .level-scenario {
      font-size: 11px;
      color: #90959d;
      margin: 0;
      line-height: 1.5;

      strong {
        color: #e6a23c;
      }
    }
  }

  .field-collapse {
    border: none;
    background: transparent;

    ::v-deep .el-collapse-item__header {
      background: #23272f;
      color: #e3a5a5;
      border: none;
      padding: 0 12px;
      height: 38px;
      line-height: 38px;
      font-size: 13px;
      border-radius: 6px;
      margin-bottom: 4px;
    }

    ::v-deep .el-collapse-item__wrap {
      background: transparent;
      border: none;
    }

    ::v-deep .el-collapse-item__content {
      padding: 8px 4px 12px;
    }
  }

  .section-summary {
    font-size: 12px;
    color: #8b93a7;
    margin: 0 0 8px;
    line-height: 1.5;
  }

  .field-table {
    .field-row {
      display: grid;
      grid-template-columns: 150px 118px 1fr;
      gap: 8px;
      padding: 6px 8px;
      font-size: 12px;
      border-radius: 4px;

      &:nth-child(odd) {
        background: rgba(255, 255, 255, 0.03);
      }
    }

    .field-name {
      color: #7eb8ff;
      font-weight: 500;
    }

    .field-tag {
      color: #6b7280;
      font-family: monospace;
      font-size: 11px;
    }

    .field-meaning {
      color: #c5cad3;
      line-height: 1.5;
    }
  }

  .relation-note {
    margin-top: 14px;
    padding: 12px 14px;
    background: rgba(91, 156, 245, 0.08);
    border-radius: 8px;
    border: 1px solid rgba(91, 156, 245, 0.15);
    font-size: 12px;
    line-height: 1.65;
    color: #b8c5d6;

    strong {
      color: #7eb8ff;
    }
  }
}
</style>
