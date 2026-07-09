<template>
  <el-dialog
    :title="dialogTitle"
    :visible.sync="innerVisible"
    width="920px"
    append-to-body
    custom-class="algorithm-explain-dialog"
  >
    <div class="algorithm-explain__tabs">
      <el-radio-group v-model="activeScheme" size="small">
        <el-radio-button
          v-for="tab in visibleSchemeTabs"
          :key="tab.id"
          :label="tab.id"
        >
          {{ tab.label }}
        </el-radio-button>
      </el-radio-group>
    </div>
    <p class="algorithm-explain__desc">{{ schemeText.description }}</p>
    <ul class="algorithm-explain__points">
      <li v-for="(p, i) in schemeText.points" :key="i">{{ p }}</li>
    </ul>
    <ol v-if="schemeText.stepDetails && schemeText.stepDetails.length" class="algorithm-explain__steps">
      <li v-for="(s, i) in schemeText.stepDetails" :key="i" class="algorithm-explain__step">
        <div class="step-title">{{ s.title }}</div>
        <div class="step-body">
          <span class="step-label">作用</span>{{ s.purpose }}
        </div>
        <div class="step-body step-effect">
          <span class="step-label">效果</span>{{ s.effect }}
        </div>
      </li>
    </ol>

    <!-- SVG + CSS 流程图（矢量清晰，不依赖 Canvas 缩放） -->
    <div class="flow-chart">
      <div
        v-for="(phase, pi) in schemeText.flowPhases"
        :key="pi"
        class="flow-phase"
      >
        <div class="flow-phase__badge">{{ phase.label }}</div>
        <div class="flow-phase__body">
          <div class="flow-phase__main">
            <template v-for="(step, si) in phase.steps">
              <div
                :key="step.id || `${pi}-${si}`"
                :class="['flow-node', `flow-node--${step.kind || 'main'}`]"
              >
                <span class="flow-node__title">{{ step.title }}</span>
                <span v-if="step.sub" class="flow-node__sub">{{ step.sub }}</span>
              </div>
              <div
                v-if="si < phase.steps.length - 1"
                :key="`arrow-${pi}-${si}`"
                class="flow-arrow"
                :class="{ 'flow-arrow--dashed': step.arrowDashed }"
                aria-hidden="true"
              >
                <svg viewBox="0 0 32 16" xmlns="http://www.w3.org/2000/svg">
                  <path
                    d="M2 8 H22 M18 4 L26 8 L18 12"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.8"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </svg>
              </div>
            </template>
          </div>
          <div v-if="phase.branches && phase.branches.length" class="flow-phase__branches">
            <div
              v-for="(branch, bi) in phase.branches"
              :key="`branch-${pi}-${bi}`"
              class="flow-branch"
            >
              <span class="flow-branch__tag">{{ branch.tag || '可选' }}</span>
              <div class="flow-branch__nodes">
                <div
                  v-for="(node, ni) in branch.nodes"
                  :key="`bn-${pi}-${bi}-${ni}`"
                  :class="['flow-node', 'flow-node--branch', `flow-node--${node.kind || 'optional'}`]"
                >
                  <span class="flow-node__title">{{ node.title }}</span>
                  <span v-if="node.sub" class="flow-node__sub">{{ node.sub }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="flow-legend">
        <span class="flow-legend__item"><i class="dot dot--main" />主流程</span>
        <span class="flow-legend__item"><i class="dot dot--optional" />可选 / 默认关闭</span>
        <span class="flow-legend__item"><i class="dot dot--key" />关键引擎</span>
        <span class="flow-legend__item"><i class="dot dot--output" />前端展示</span>
      </div>
    </div>

    <p class="algorithm-explain__overlay">
      <strong>前端展示：</strong>{{ schemeText.overlay }}
    </p>
  </el-dialog>
</template>

<script>
import {
  DEFAULT_ACTIVE_LESION_ENGINE,
  isHiddenLesionEngine
} from '@/utils/lesionEngines'

const SCHEME_COPY = {
  'scheme-a': {
    title: '方案 A · 肺区智能筛查',
    description: '基于 TotalSegmentator 肺区分割 + 3D 形态学 HU 候选筛选。支持全序列与当前层；输出病灶轮廓、bbox、置信度及前端 stack 层位。',
    points: [
      '模式：全序列 / 当前层均可',
      '关键：IPP 排序 → 肺野 mask → HU 形态学 → 3D 连通域 → sliceIndex 映射',
      '典型耗时：肺区分割约 30–60s（~474 层，视 CPU/GPU）',
      '实现：scheme_a_detector.py、hu_utils.py、lung_segment_2d.py'
    ],
    overlay: '红色虚线 bbox + 半透明轮廓；滚轮切层仅显示当前层病灶；HU 区分 GGO / 实性 / 高密度',
    flowPhases: [
      {
        label: '① 数据准备',
        steps: [
          { title: '前端发起', sub: 'SSE 请求', kind: 'output' },
          { title: 'CT 代理', sub: ':9800', kind: 'main' },
          { title: 'AI 服务', sub: 'scheme-a', kind: 'main' },
          { title: 'MinIO', sub: '拉取 DICOM', kind: 'main' },
          { title: 'robust_ct', sub: '_loader', kind: 'main' }
        ]
      },
      {
        label: '② 肺野分割',
        steps: [
          { title: 'IPP 排序', sub: '3D 体数据', kind: 'main' },
          { title: 'slice 映射', sub: 'file_slice', kind: 'key' },
          { title: 'TotalSeg', sub: '肺区分割', kind: 'main' }
        ],
        branches: [
          {
            tag: '回退',
            nodes: [
              { title: '2D 肺野', sub: '回退' },
              { title: '当前层', sub: '裁剪' }
            ]
          }
        ]
      },
      {
        label: '③ 候选与过滤',
        steps: [
          { title: 'HU 候选', sub: 'nodule_mask', kind: 'main' },
          { title: '3D 连通域', sub: '体积/实心度', kind: 'main' },
          { title: '跨层连续', sub: '肺门抑制', kind: 'main' },
          { title: 'HU 分类', sub: 'GGO/实性', kind: 'highlight' },
          { title: 'sliceIndex', sub: '→ 前端', kind: 'key' }
        ]
      },
      {
        label: '④ 输出与阅片',
        steps: [
          { title: 'contour', sub: '+ bbox', kind: 'main' },
          { title: 'SSE 推送', sub: '结果 JSON', kind: 'main' },
          { title: '阅片叠加', sub: 'overlay', kind: 'output' }
        ],
        branches: [
          { tag: '可选', nodes: [{ title: '落库', sub: 'dicom_ai_lesion' }] }
        ]
      }
    ]
  },
  'scheme-b': {
    title: '方案 B · 融合精准分析',
    description:
      '全序列深度学习检测 + 解剖约束 + HU 形态标注，输出统一病灶列表。默认跳过血管 TotalSegmentator、关闭 GGO 独立通道与 watershed 轮廓，以缩短耗时并减少空气区/血管假阳性。推荐 GPU。',
    points: [
      '模式：仅全序列（series）；可选配对增强 CT 计算 ΔHU',
      '子引擎：auto → nnDetection 优先，否则 MONAI RetinaNet；可强制 monai / nndet',
      '默认优化：跳过血管 TS · GGO 启发式 off · watershed 轮廓 off · 体数据磁盘缓存',
      '分色：实性红圆 / 磨玻璃蓝轮廓 / 混合紫 / 钙化黄菱形（均写入 lesions，无独立绿层）',
      '实现：scheme_b_fusion.py、lesion_enrichment.py、scheme_b_filter.py、detection_runner.py'
    ],
    stepDetails: [
      {
        title: '1. 发起识别（准备）',
        purpose: '阅片页选择方案 B 后，经 CT 微服务把序列信息转发到 AI 服务，并建立 SSE 长连接推送进度。',
        effect: '左侧日志面板显示「准备→下载→体数据→融合→ΔHU→完成」各阶段，可随时取消任务。'
      },
      {
        title: '2. 下载 DICOM / 命中体数据缓存',
        purpose: '从 MinIO 拉取该序列全部 .dcm；若同 study+series 近期已识别过，直接读取 logs/ai-service/cache 中的体数据缓存。',
        effect: '首次识别需完整下载；二次识别可跳过下载，节省 1–3 分钟网络与解析时间。'
      },
      {
        title: '3. 构建 3D 体数据（IPP 排序）',
        purpose: '按 Image Position Patient 将各层切片排成连续 3D 数组，并换算为 HU 值，得到 spacing 与层厚信息。',
        effect: '得到与真实解剖顺序一致的体数据，后续分割与检测不会在错层上运算。'
      },
      {
        title: '4. 降采样与 HU 质量门（可选）',
        purpose: '层数过多时沿 z 轴轻量降采样以控制 GPU 显存；检查体数据 HU 分布是否像有效胸部 CT。',
        effect: '超厚序列仍可跑通；异常数据（如未正确缩放）会给出警告，避免完全误判。'
      },
      {
        title: '5. 肺野 + 肺叶分割（TotalSegmentator）',
        purpose: '在融合子进程中用 TotalSegmentator 得到左右肺野与五叶 ROI；失败时用肺野 bbox 启发式估算肺叶。',
        effect: '为后续过滤提供「是否在肺内」依据，并为每个病灶标注肺叶位置（如右上叶）。'
      },
      {
        title: '6. 血管分割（默认跳过）',
        purpose: '完整版可再跑 lung_vessels 任务做血管 mask，用于剔除血管样假阳性；当前默认 SCHEME_B_SKIP_VESSEL_SEG=true 以省时。',
        effect: '识别速度明显提升；血管误检主要靠 P1 形态与 HU 规则抑制，而非血管 mask IoU。'
      },
      {
        title: '7. 深度学习 3D 检测',
        purpose: '子引擎 auto 优先 nnDetection（LUNA16 权重），否则 MONAI RetinaNet；在体数据上输出 3D 候选框及置信度。',
        effect: '找到疑似结节的位置与大小，比纯 HU 形态学更擅长小结节与弱对比灶。'
      },
      {
        title: '8. P1 融合过滤',
        purpose: '剔除肺野外、空气占比过高、HU 不合理、形态不像结节（实心度/球形度等）的候选；低置信磨玻璃可进入补充池。',
        effect: '显著减少胸壁、气管、空气区的红框假阳性，列表更干净。'
      },
      {
        title: '9. 病灶 enrich（轮廓 + 分型 + 肺叶）',
        purpose: '在检测框 ROI 内按 HU 阈值提取真实轮廓（watershed 默认关闭）；调用 classify_nodule_hu 区分实性/磨玻璃/混合/钙化，并写入肺叶与形态指标。',
        effect: '每个病灶带有可解释的 HU 均值、亚型、轮廓坐标，供右侧指标面板与分色渲染使用。'
      },
      {
        title: '10. GGO 启发式补充（默认关闭）',
        purpose: '独立 GGO 扫描算法可将肺内磨玻璃区并入 lesions；当前 SCHEME_B_GGO_BACKEND=off，仅保留低置信 DL 候选作轻量补充。',
        effect: '避免大片磨玻璃误标；需要时可手动开启环境变量恢复该通道。'
      },
      {
        title: '11. 多源融合去重与 sliceIndex 映射',
        purpose: '合并 DL 高置信、低置信 GGO 与（可选）启发式结果，按 IoU 去重；把 3D 坐标映射为前端 stack 的 sliceIndex。',
        effect: '同一结节只显示一次；滚轮切层时仅在对应层出现标记。'
      },
      {
        title: '12. 增强 CT ΔHU（可选）',
        purpose: '若同患者存在配对平扫+增强序列，可计算病灶增强前后 HU 差值（ΔHU）。',
        effect: '指标面板展示强化程度，辅助鉴别血管性与部分良性灶（无增强 CT 时跳过）。'
      },
      {
        title: '13. SSE 返回与落库',
        purpose: '通过 SSE 推送最终 lesions JSON；CT 模块可写入租户库 dicom_ai_lesion，供左侧历史记录回看。',
        effect: '刷新页面后仍可加载上次 AI 结果；历史乱码字段由前端映射兜底显示。'
      },
      {
        title: '14. 前端分色叠加',
        purpose: '按 markerType / subType 在 Canvas 上绘制 bbox 与轮廓，右侧展示 HU、形态、肺叶等指标。',
        effect: '实性红、磨玻璃蓝、混合紫、钙化黄菱形一目了然，无红绿双层叠加。'
      }
    ],
    overlay: '按病灶类型分色分形渲染（bbox + 轮廓）；GGO 已合并进 lesions；右侧指标面板展示 HU、形态与肺叶',
    flowPhases: [
      {
        label: '① 体数据',
        steps: [
          { title: 'MinIO 下载', sub: '或体缓存', kind: 'main' },
          { title: 'IPP 排序', sub: '3D 体数据', kind: 'main' },
          { title: '肺野+肺叶', sub: 'TotalSeg', kind: 'main' }
        ],
        branches: [
          {
            tag: '可选',
            nodes: [
              { title: '降采样', sub: 'HU 质量门' },
              { title: '血管 TS', sub: '默认跳过' }
            ]
          }
        ]
      },
      {
        label: '② 深度学习检测',
        steps: [
          { title: '子引擎', sub: 'auto/monai/nndet', kind: 'key' },
          { title: '3D 检测框', sub: '候选', kind: 'main' },
          { title: 'P1 过滤', sub: '肺野/空气/HU', kind: 'main' }
        ],
        branches: [
          {
            tag: '并行引擎',
            nodes: [
              { title: 'nnDetection', sub: 'LUNA16' },
              { title: 'MONAI', sub: 'RetinaNet' }
            ]
          }
        ]
      },
      {
        label: '③ 融合标注',
        steps: [
          { title: 'enrich', sub: '轮廓+分型', kind: 'highlight' },
          { title: '多源融合', sub: '去重', kind: 'main' },
          { title: 'sliceIndex', sub: '映射', kind: 'key' }
        ],
        branches: [
          {
            tag: '默认关闭',
            nodes: [
              { title: 'GGO 启发式', sub: 'off' },
              { title: 'ΔHU 增强', sub: '可选' }
            ]
          }
        ]
      },
      {
        label: '④ 融合与展示',
        steps: [
          { title: '统一 lesions', sub: '分色', kind: 'main' },
          { title: 'SSE 返回', sub: '+ 落库', kind: 'main' },
          { title: '轮廓叠加', sub: '类型分色', kind: 'output' },
          { title: '指标面板', sub: 'HU/形态', kind: 'output' }
        ]
      }
    ]
  },
  'scheme-c': {
    title: '方案 C · 单层异常倾向',
    description: '对当前层 HU 做体内/肺实质分析，生成与原图同分辨率的热力图与异常倾向标签。参考性筛查，不输出结节 bbox 列表。',
    points: [
      '模式：仅当前层（single）',
      '不以 Grad-CAM 皮肤边缘为主，避免背景假阳性',
      '热力图：肺实质 GGO/实性偏离 + 高密度灶 (+80~+280 HU)',
      '实现：scheme_c_screening.py、hu_utils.py'
    ],
    overlay: '蓝→红半透明热力图叠加在当前分析层；无 bbox 框；右侧显示倾向标签与置信度',
    flowPhases: [
      {
        label: '① 单层输入',
        steps: [
          { title: '当前层', sub: 'sliceIndex', kind: 'key' },
          { title: 'MinIO', sub: '取 .dcm', kind: 'main' },
          { title: 'pixel_array', sub: '× Rescale', kind: 'main' },
          { title: 'HU 实际值', sub: '窗宽窗位', kind: 'main' }
        ]
      },
      {
        label: '② 预处理',
        steps: [
          { title: '体内 mask', sub: '去空气/皮', kind: 'main' },
          { title: '肺实质', sub: '区域', kind: 'main' }
        ]
      },
      {
        label: '③ 异常建模',
        steps: [
          { title: 'GGO/实性', sub: 'HU 偏离', kind: 'main' },
          { title: '高密度灶', sub: '+80~+280HU', kind: 'highlight' },
          { title: '权重融合', sub: '热力图', kind: 'main' },
          { title: '归一化', sub: '0~1 矩阵', kind: 'main' }
        ]
      },
      {
        label: '④ 热力图输出',
        steps: [
          { title: 'heatmap', sub: '.values[]', kind: 'main' },
          { title: '倾向标签', sub: '+ 置信度', kind: 'main' },
          { title: 'SSE 推送', sub: '实时', kind: 'main' },
          { title: '前端叠加', sub: '热力图', kind: 'output' }
        ]
      }
    ]
  }
}

const VISIBLE_SCHEME_TABS = [
  { id: 'scheme-b', label: '融合精准分析' },
  { id: 'scheme-c', label: '单层异常倾向' }
]

function resolveExplainScheme(scheme) {
  if (!scheme || isHiddenLesionEngine(scheme)) {
    return DEFAULT_ACTIVE_LESION_ENGINE
  }
  return VISIBLE_SCHEME_TABS.some((tab) => tab.id === scheme)
    ? scheme
    : DEFAULT_ACTIVE_LESION_ENGINE
}

export default {
  name: 'AlgorithmExplainDialog',
  props: {
    visible: { type: Boolean, default: false },
    scheme: { type: String, default: DEFAULT_ACTIVE_LESION_ENGINE }
  },
  data() {
    return {
      activeScheme: resolveExplainScheme(this.scheme)
    }
  },
  computed: {
    visibleSchemeTabs() {
      return VISIBLE_SCHEME_TABS
    },
    innerVisible: {
      get() { return this.visible },
      set(v) { this.$emit('update:visible', v) }
    },
    schemeText() {
      return SCHEME_COPY[this.activeScheme] || SCHEME_COPY[DEFAULT_ACTIVE_LESION_ENGINE]
    },
    dialogTitle() {
      return this.schemeText.title
    }
  },
  watch: {
    scheme(val) {
      this.activeScheme = resolveExplainScheme(val)
    },
    visible(val) {
      if (val) this.activeScheme = resolveExplainScheme(this.scheme)
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
  margin: 0 0 10px;
  padding-left: 18px;
  font-size: 12px;
  color: #909399;
  line-height: 1.55;
}

.algorithm-explain__steps {
  margin: 0 0 14px;
  padding: 10px 12px 10px 28px;
  max-height: 200px;
  overflow-y: auto;
  font-size: 12px;
  line-height: 1.5;
  color: #606266;
  background: #f5f7fa;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.algorithm-explain__step {
  margin-bottom: 10px;

  &:last-child {
    margin-bottom: 0;
  }
}

.step-title {
  font-weight: 600;
  color: #303133;
  margin-bottom: 2px;
}

.step-body {
  margin-top: 2px;
  color: #606266;
}

.step-effect {
  color: #529b2e;
}

.step-label {
  display: inline-block;
  min-width: 2.2em;
  margin-right: 4px;
  font-weight: 600;
  color: #909399;
}

/* ── 流程图（SVG + CSS，高清矢量） ── */
.flow-chart {
  padding: 16px 14px 12px;
  background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
  border: 1px solid #e2e8f0;
  border-radius: 10px;
}

.flow-phase {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 14px;

  &:last-of-type {
    margin-bottom: 10px;
  }
}

.flow-phase__badge {
  flex: 0 0 88px;
  padding: 6px 0;
  font-size: 12px;
  font-weight: 600;
  color: #409eff;
  text-align: right;
  line-height: 1.4;
  white-space: nowrap;
}

.flow-phase__body {
  flex: 1;
  min-width: 0;
}

.flow-phase__main {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px 0;
}

.flow-node {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-width: 88px;
  max-width: 110px;
  min-height: 52px;
  padding: 6px 10px;
  border-radius: 8px;
  border: 1.5px solid #409eff;
  background: #fff;
  box-shadow: 0 1px 3px rgba(64, 158, 255, 0.12);
  text-align: center;
  transition: box-shadow 0.15s;

  &:hover {
    box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
  }
}

.flow-node__title {
  font-size: 12px;
  font-weight: 600;
  color: #303133;
  line-height: 1.35;
  word-break: keep-all;
}

.flow-node__sub {
  margin-top: 2px;
  font-size: 11px;
  color: #909399;
  line-height: 1.3;
}

.flow-node--main {
  border-color: #409eff;
  background: #fff;
}

.flow-node--key {
  border-color: #e6a23c;
  background: #fdf6ec;
  box-shadow: 0 1px 3px rgba(230, 162, 60, 0.15);
}

.flow-node--highlight {
  border-color: #f56c6c;
  background: #fef0f0;
  box-shadow: 0 1px 3px rgba(245, 108, 108, 0.15);
}

.flow-node--output {
  border-color: #67c23a;
  background: #f0f9eb;
  box-shadow: 0 1px 3px rgba(103, 194, 58, 0.15);
}

.flow-node--optional,
.flow-node--branch {
  border-style: dashed;
  border-color: #c0c4cc;
  background: #fafafa;
  box-shadow: none;
}

.flow-arrow {
  flex: 0 0 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #409eff;

  svg {
    width: 28px;
    height: 14px;
  }
}

.flow-arrow--dashed {
  color: #c0c4cc;
}

.flow-phase__branches {
  margin-top: 8px;
  padding-left: 4px;
}

.flow-branch {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.flow-branch__tag {
  flex: 0 0 auto;
  padding: 2px 8px;
  font-size: 10px;
  font-weight: 600;
  color: #909399;
  background: #eef1f6;
  border-radius: 10px;
  letter-spacing: 0.02em;
}

.flow-branch__nodes {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
}

.flow-branch .flow-node {
  min-width: 76px;
  max-width: 96px;
  min-height: 44px;
  padding: 4px 8px;
}

.flow-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 20px;
  padding-top: 10px;
  margin-top: 4px;
  border-top: 1px dashed #dcdfe6;
  font-size: 11px;
  color: #909399;
}

.flow-legend__item {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 3px;
  border: 1.5px solid transparent;
}

.dot--main {
  border-color: #409eff;
  background: #fff;
}

.dot--optional {
  border: 1.5px dashed #c0c4cc;
  background: #fafafa;
}

.dot--key {
  border-color: #e6a23c;
  background: #fdf6ec;
}

.dot--output {
  border-color: #67c23a;
  background: #f0f9eb;
}

.algorithm-explain__overlay {
  margin: 12px 0 0;
  font-size: 12px;
  color: #606266;
  line-height: 1.5;
}
</style>
