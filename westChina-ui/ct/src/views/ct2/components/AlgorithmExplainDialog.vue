<template>
  <el-dialog
    :title="dialogTitle"
    :visible.sync="innerVisible"
    width="720px"
    append-to-body
    custom-class="algorithm-explain-dialog"
    @opened="drawFlowchart"
  >
    <div class="algorithm-explain__tabs">
      <el-radio-group v-model="activeScheme" size="small" @change="drawFlowchart">
        <el-radio-button label="scheme-a">肺区智能筛查</el-radio-button>
        <el-radio-button label="scheme-b">融合精准分析</el-radio-button>
        <el-radio-button label="scheme-c">单层异常倾向</el-radio-button>
      </el-radio-group>
    </div>
    <p class="algorithm-explain__desc">{{ schemeText.description }}</p>
    <ul class="algorithm-explain__points">
      <li v-for="(p, i) in schemeText.points" :key="i">{{ p }}</li>
    </ul>
    <div class="algorithm-explain__canvas-wrap">
      <canvas ref="flowCanvas" class="algorithm-explain__canvas" width="680" height="320" />
    </div>
    <p class="algorithm-explain__overlay">
      <strong>展示方式：</strong>{{ schemeText.overlay }}
    </p>
  </el-dialog>
</template>

<script>
const SCHEME_COPY = {
  'scheme-a': {
    title: '方案 A · 肺区智能筛查',
    description: '基于 TotalSegmentator 肺区分割 + 3D 形态学候选筛选，在肺野内检出结节样高密度区域，适合全序列或当前层快速筛查。',
    points: [
      '支持：全序列识别、当前层识别',
      '输出：病灶 bbox + 轮廓 + 置信度 + 层位',
      '典型耗时：肺区分割约 30–60s（474 层）'
    ],
    overlay: '红色虚线框 + 半透明轮廓；滚轮切换层位时仅显示当前层的病灶标记',
    nodes: [
      { id: 'a1', text: 'DICOM\n序列', x: 24, y: 130 },
      { id: 'a2', text: 'MinIO\n下载', x: 120, y: 130 },
      { id: 'a3', text: '3D 体数据\nIPP 排序', x: 216, y: 130 },
      { id: 'a4', text: '肺区分割\nTotalSeg', x: 312, y: 130 },
      { id: 'a5', text: '形态学\n候选筛选', x: 408, y: 130 },
      { id: 'a6', text: '病灶列表\nbbox', x: 504, y: 130 },
      { id: 'a7', text: '阅片叠加\noverlay', x: 600, y: 130 }
    ],
    edges: [['a1', 'a2'], ['a2', 'a3'], ['a3', 'a4'], ['a4', 'a5'], ['a5', 'a6'], ['a6', 'a7']]
  },
  'scheme-b': {
    title: '方案 B · 融合精准分析',
    description: '肺叶/血管分割 + nnDetection/MONAI 候选 + 血管过滤 + GGO 启发式，面向全序列精准分析（需 GPU，MONAI 默认关闭）。',
    points: [
      '仅支持：全序列识别',
      '输出：3D 融合病灶 + 可选 GGO 区域',
      '血管/肺叶分割用于减少假阳性'
    ],
    overlay: '红色 bbox 标记结节；若检出 GGO 则叠加绿色半透明区域',
    nodes: [
      { id: 'b1', text: '3D 体', x: 24, y: 80 },
      { id: 'b2', text: '肺叶+\n血管', x: 120, y: 80 },
      { id: 'b3', text: 'nnDet/\nMONAI', x: 216, y: 80 },
      { id: 'b4', text: '血管\n过滤', x: 312, y: 80 },
      { id: 'b5', text: 'GGO\n启发式', x: 408, y: 80 },
      { id: 'b6', text: '融合\n病灶', x: 504, y: 80 },
      { id: 'b7', text: 'bbox+\nGGO', x: 600, y: 80 },
      { id: 'b8', text: '形态学\n轻量候选', x: 216, y: 200 }
    ],
    edges: [['b1', 'b2'], ['b2', 'b3'], ['b3', 'b4'], ['b4', 'b5'], ['b5', 'b6'], ['b6', 'b7']],
    dashedEdges: [['b2', 'b8'], ['b8', 'b4']]
  },
  'scheme-c': {
    title: '方案 C · 单层异常倾向',
    description: '2D CNN 对当前层做异常倾向分类，并生成 Grad-CAM 热力图，用于参考性筛查（非确诊）。',
    points: [
      '仅支持：当前层识别',
      '输出：分类标签 + 置信度 + 64×64 热力图',
      '不输出结节 bbox 列表'
    ],
    overlay: '蓝→红半透明热力图叠加在分析层；无 bbox 框',
    nodes: [
      { id: 'c1', text: '当前层\nHU', x: 40, y: 130 },
      { id: 'c2', text: '预处理\n归一化', x: 150, y: 130 },
      { id: 'c3', text: 'CNN\n分类', x: 260, y: 130 },
      { id: 'c4', text: 'Grad-CAM', x: 370, y: 130 },
      { id: 'c5', text: '热力图\n64×64', x: 480, y: 130 },
      { id: 'c6', text: '倾向标签\n+置信度', x: 590, y: 130 }
    ],
    edges: [['c1', 'c2'], ['c2', 'c3'], ['c3', 'c4'], ['c4', 'c5'], ['c5', 'c6']]
  }
}

export default {
  name: 'AlgorithmExplainDialog',
  props: {
    visible: { type: Boolean, default: false },
    scheme: { type: String, default: 'scheme-a' }
  },
  data() {
    return {
      activeScheme: this.scheme || 'scheme-a'
    }
  },
  computed: {
    innerVisible: {
      get() { return this.visible },
      set(v) { this.$emit('update:visible', v) }
    },
    schemeText() {
      return SCHEME_COPY[this.activeScheme] || SCHEME_COPY['scheme-a']
    },
    dialogTitle() {
      return this.schemeText.title
    }
  },
  watch: {
    scheme(val) {
      if (val) this.activeScheme = val
    },
    visible(val) {
      if (val && this.scheme) this.activeScheme = this.scheme
    }
  },
  methods: {
    drawFlowchart() {
      this.$nextTick(() => {
        const canvas = this.$refs.flowCanvas
        if (!canvas) return
        const ctx = canvas.getContext('2d')
        const spec = SCHEME_COPY[this.activeScheme]
        if (!ctx || !spec) return

        const w = canvas.width
        const h = canvas.height
        ctx.clearRect(0, 0, w, h)

        // 背景
        ctx.fillStyle = '#1a1f28'
        ctx.fillRect(0, 0, w, h)

        const nodeMap = {}
        spec.nodes.forEach((n) => { nodeMap[n.id] = n })

        const drawArrow = (from, to, dashed) => {
          const a = nodeMap[from]
          const b = nodeMap[to]
          if (!a || !b) return
          const x1 = a.x + 72
          const y1 = a.y + 28
          const x2 = b.x
          const y2 = b.y + 28
          ctx.beginPath()
          ctx.strokeStyle = dashed ? 'rgba(144, 147, 153, 0.8)' : '#409eff'
          ctx.lineWidth = dashed ? 1.5 : 2
          if (dashed) ctx.setLineDash([5, 4])
          ctx.moveTo(x1, y1)
          ctx.lineTo(x2, y2)
          ctx.stroke()
          ctx.setLineDash([])
          const ang = Math.atan2(y2 - y1, x2 - x1)
          const ax = x2 - 8 * Math.cos(ang)
          const ay = y2 - 8 * Math.sin(ang)
          ctx.beginPath()
          ctx.fillStyle = dashed ? '#909399' : '#409eff'
          ctx.moveTo(x2, y2)
          ctx.lineTo(ax - 4 * Math.sin(ang), ay + 4 * Math.cos(ang))
          ctx.lineTo(ax + 4 * Math.sin(ang), ay - 4 * Math.cos(ang))
          ctx.closePath()
          ctx.fill()
        }

        ;(spec.edges || []).forEach(([f, t]) => drawArrow(f, t, false))
        ;(spec.dashedEdges || []).forEach(([f, t]) => drawArrow(f, t, true))

        spec.nodes.forEach((n) => {
          const rx = n.x
          const ry = n.y
          const rw = 72
          const rh = 56
          const grd = ctx.createLinearGradient(rx, ry, rx, ry + rh)
          grd.addColorStop(0, '#2c3442')
          grd.addColorStop(1, '#232a36')
          ctx.fillStyle = grd
          ctx.strokeStyle = '#409eff'
          ctx.lineWidth = 1.5
          ctx.fillRect(rx, ry, rw, rh)
          ctx.strokeRect(rx + 0.5, ry + 0.5, rw - 1, rh - 1)
          ctx.fillStyle = '#e8eaed'
          ctx.font = '11px sans-serif'
          ctx.textAlign = 'center'
          const lines = n.text.split('\n')
          lines.forEach((line, i) => {
            ctx.fillText(line, rx + rw / 2, ry + 20 + i * 14)
          })
        })
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.algorithm-explain__tabs {
  margin-bottom: 12px;
}

.algorithm-explain__desc {
  margin: 0 0 8px;
  font-size: 13px;
  color: #606266;
  line-height: 1.55;
}

.algorithm-explain__points {
  margin: 0 0 12px;
  padding-left: 18px;
  font-size: 12px;
  color: #909399;
  line-height: 1.5;
}

.algorithm-explain__canvas-wrap {
  border: 1px solid #ebeef5;
  border-radius: 6px;
  overflow: hidden;
  background: #1a1f28;
}

.algorithm-explain__canvas {
  display: block;
  width: 100%;
  height: auto;
}

.algorithm-explain__overlay {
  margin: 12px 0 0;
  font-size: 12px;
  color: #606266;
  line-height: 1.5;
}
</style>
