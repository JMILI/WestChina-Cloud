<template>
  <div class="study-side-panel">
    <el-collapse v-model="panelActive" class="left-collapse">
      <el-collapse-item v-if="makerFlag" title="标记管理" name="maker" class="left-label">
        <el-card
          v-for="item in makerItems"
          :key="item.instanceUid"
          :body-style="{ padding: '0px' }"
          class="maker-card"
        >
          <img
            v-if="item.makerImage && item.makerImage.previewUrl"
            :src="item.makerImage.previewUrl"
            class="maker-thumb-img"
            alt=""
          />
          <div
            v-else
            :ref="'maker_thumb_' + item.instanceUid"
            class="ct-image1 maker-thumb"
          ></div>
          <div
            class="left-label-item"
            @click="$emit('view-image', item)"
          >
            <div>图像id：{{ item.instanceUid }}</div>
            <div>拍摄CT时间：{{ item.studyDate }}</div>
            <div class="bottom clearfix">
              <span class="time">标记日期:{{ item.makerTime }}</span>
            </div>
          </div>
        </el-card>
        <div v-if="isDisplaySave" class="left-label-item-save">
          <el-tooltip
            content="点击保存按钮，系统将上传标记的图像"
            placement="bottom"
            :open-delay="250"
          >
            <el-button class="uploader-btn" size="small" @click="$emit('submit-upload')">保存</el-button>
          </el-tooltip>
        </div>
      </el-collapse-item>

      <el-collapse-item title="AI识别病灶结果" name="aiLesion" class="left-ai-lesion">
        <el-card
          v-for="item in aiLesionItems"
          :key="item.dicomAiLesionId"
          :body-style="{ padding: '0px' }"
          class="ai-lesion-card"
          :class="{ 'is-active': activeAiLesionId === item.dicomAiLesionId }"
        >
          <div v-if="item.lesionCount > 0" class="ai-lesion-badge">
            病灶 {{ item.lesionCount }} 处
          </div>
          <div v-else-if="item.overlayType === 'heatmap'" class="ai-lesion-badge ai-lesion-badge--heatmap">
            热力图
          </div>
          <div
            :ref="'ai_thumb_' + item.dicomAiLesionId"
            class="ct-image1 ai-lesion-thumb"
          ></div>
          <div class="left-label-item ai-lesion-info" @click="$emit('view-ai-lesion', item)">
            <el-tooltip
              :content="'识别模式：' + formatDetectMode(item.detectMode)"
              placement="right"
              :open-delay="250"
              popper-class="study-info-tooltip"
            >
              <div class="info-line">识别模式：{{ formatDetectMode(item.detectMode) }}</div>
            </el-tooltip>
            <el-tooltip
              v-if="item.instanceUid"
              :content="'Instance UID：' + item.instanceUid"
              placement="right"
              :open-delay="250"
              popper-class="study-info-tooltip"
            >
              <div class="info-line">Instance UID：{{ truncateUid(item.instanceUid) }}</div>
            </el-tooltip>
            <el-tooltip
              v-if="item.sourceSliceIndex != null"
              :content="'标记层位 Instance ' + item.sourceSliceIndex"
              placement="right"
              :open-delay="250"
              popper-class="study-info-tooltip"
            >
              <div class="info-line">标记层位 Instance {{ item.sourceSliceIndex }}</div>
            </el-tooltip>
            <el-tooltip
              :content="'原始序列：' + item.sourceDicomId"
              placement="right"
              :open-delay="250"
              popper-class="study-info-tooltip"
            >
              <div class="info-line">原始序列：{{ item.sourceDicomId }}</div>
            </el-tooltip>
            <el-tooltip
              :content="'切片数：' + item.imageCount"
              placement="right"
              :open-delay="250"
              popper-class="study-info-tooltip"
            >
              <div class="info-line">切片数：{{ item.imageCount }}</div>
            </el-tooltip>
            <el-tooltip
              :content="'检查部位：' + (item.bodyPart || '未知')"
              placement="right"
              :open-delay="250"
              popper-class="study-info-tooltip"
            >
              <div class="info-line">检查部位：{{ item.bodyPart || '未知' }}</div>
            </el-tooltip>
            <el-tooltip
              v-if="item.engine"
              :content="'算法：' + item.engine"
              placement="right"
              :open-delay="250"
              popper-class="study-info-tooltip"
            >
              <div class="info-line">算法：{{ formatEngine(item.engine) }}</div>
            </el-tooltip>
            <el-tooltip
              :content="'识别时间：' + (item.detectTime || '—')"
              placement="right"
              :open-delay="250"
              popper-class="study-info-tooltip"
            >
              <div class="bottom clearfix">
                <span class="time">识别: {{ item.detectTime }}</span>
              </div>
            </el-tooltip>
          </div>
        </el-card>
        <div v-if="!aiLesionItems.length" class="ai-lesion-empty">暂无 AI 识别结果</div>
      </el-collapse-item>

      <el-collapse-item title="病人study列表" name="studies" class="left-study">
        <el-collapse
          v-for="(seriesMap, studyUid) in studySeriesList"
          :key="studyUid"
          v-model="studyActiveNames"
          class="left-study-collapse"
          @change="onStudyCollapseChange"
        >
          <el-collapse-item
            :name="String(studyUid)"
            class="left-study-collapse-item"
          >
            <template slot="title">
              <el-tooltip
                :content="'studyID：' + studyUid"
                placement="right"
                :open-delay="250"
                popper-class="study-info-tooltip"
              >
                <span class="study-title-text">studyID:{{ truncateUid(studyUid) }}</span>
              </el-tooltip>
            </template>
            <el-card
              v-for="series in getSeriesList(seriesMap)"
              :key="series.dicomId"
              :body-style="{ padding: '0px' }"
              class="series-card"
              :class="{ 'is-active': activeSeriesId === series.dicomId }"
            >
              <div
                :ref="'thumb_' + series.dicomId"
                class="ct-image1"
              ></div>
              <div
                class="left-study-collapse-item series-info"
                @click="$emit('change-series', series)"
              >
                <el-tooltip
                  :content="'id：' + series.dicomId"
                  placement="right"
                  :open-delay="250"
                  popper-class="study-info-tooltip"
                >
                  <div class="info-line">id：{{ series.dicomId }}</div>
                </el-tooltip>
                <el-tooltip
                  :content="'研究id：' + series.dicomCtStudyUid"
                  placement="right"
                  :open-delay="250"
                  popper-class="study-info-tooltip"
                >
                  <div class="info-line">研究id：{{ series.dicomCtStudyUid }}</div>
                </el-tooltip>
                <el-tooltip
                  :content="'序列id：' + series.dicomCtSeriesUid"
                  placement="right"
                  :open-delay="250"
                  popper-class="study-info-tooltip"
                >
                  <div class="info-line">序列id：{{ series.dicomCtSeriesUid }}</div>
                </el-tooltip>
                <el-tooltip
                  :content="'切片数：' + seriesSliceCount(series)"
                  placement="right"
                  :open-delay="250"
                  popper-class="study-info-tooltip"
                >
                  <div class="info-line">切片数：{{ seriesSliceCount(series) }}</div>
                </el-tooltip>
                <el-tooltip
                  :content="'检查部位：' + (series.dicomCtBody || '未知')"
                  placement="right"
                  :open-delay="250"
                  popper-class="study-info-tooltip"
                >
                  <div class="info-line">检查部位：{{ series.dicomCtBody }}</div>
                </el-tooltip>
                <el-tooltip
                  :content="'日期：' + (series.dicomCtTime || '—')"
                  placement="right"
                  :open-delay="250"
                  popper-class="study-info-tooltip"
                >
                  <div class="bottom clearfix">
                    <span class="time">日期:{{ series.dicomCtTime }}</span>
                  </div>
                </el-tooltip>
              </div>
            </el-card>
          </el-collapse-item>
        </el-collapse>
      </el-collapse-item>
    </el-collapse>
  </div>
</template>

<script>
import * as cornerstone from 'cornerstone-core'
import { formatDetectModeLabel } from '@/utils/aiLesionSeries'
import {
  installThumbnailRejectionHandler,
  loadCornerstoneThumbnail,
  pickThumbnailCandidates
} from '@/utils/thumbnailLoader'

export default {
  name: 'StudySidePanel',
  props: {
    makerFlag: { type: Boolean, default: false },
    makerInfoList: { type: [Array, Object], default: () => ({}) },
    isDisplaySave: { type: Boolean, default: false },
    studySeriesList: { type: Object, default: () => ({}) },
    aiLesionItems: { type: Array, default: () => [] },
    activeSeriesId: { type: [String, Number], default: null },
    activeAiLesionId: { type: [String, Number], default: null }
  },
  data() {
    return {
      panelActive: ['maker', 'aiLesion', 'studies'],
      studyActiveNames: [],
      loadedThumbs: {},
      loadedAiThumbs: {},
      failedThumbs: {},
      failedAiThumbs: {},
      loadingThumbs: {},
      loadingAiThumbs: {}
    }
  },
  computed: {
    makerItems() {
      if (Array.isArray(this.makerInfoList)) return this.makerInfoList
      return Object.values(this.makerInfoList || {})
    }
  },
  watch: {
    makerFlag(val) {
      if (val) this.scheduleLoadMakerThumbnails()
    },
    makerInfoList: {
      immediate: true,
      deep: true,
      handler() {
        this.scheduleLoadMakerThumbnails()
      }
    },
    studySeriesList: {
      immediate: true,
      deep: true,
      handler(list) {
        const keys = Object.keys(list || {})
        if (keys.length && this.studyActiveNames.length === 0) {
          this.studyActiveNames = keys.map(String)
        }
        this.scheduleLoadThumbnails()
      }
    },
    aiLesionItems: {
      immediate: true,
      deep: true,
      handler() {
        this.scheduleLoadAiThumbnails()
      }
    }
  },
  mounted() {
    installThumbnailRejectionHandler()
    this.scheduleLoadThumbnails()
    this.scheduleLoadMakerThumbnails()
    this.scheduleLoadAiThumbnails()
  },
  methods: {
    truncateUid(uid) {
      if (!uid) return ''
      const str = String(uid)
      if (str.length <= 22) return str
      return str.slice(0, 10) + '…' + str.slice(-8)
    },
    formatEngine(engine) {
      if (!engine) return ''
      if (engine.includes('scheme-c')) return '单层异常倾向'
      if (engine.includes('scheme-b')) return '融合精准分析'
      if (engine.includes('scheme-a')) return '肺区智能筛查'
      return engine
    },
    formatDetectMode(mode) {
      return formatDetectModeLabel(mode)
    },
    seriesSliceCount(series) {
      if (!series) return 0
      if (series.imageIds && series.imageIds.length) {
        return series.imageIds.length
      }
      const count = Number(series.dicomCtCount)
      return Number.isFinite(count) && count > 0 ? count : 0
    },
    getSeriesList(seriesMap) {
      if (!seriesMap) return []
      return Object.values(seriesMap)
    },
    getThumbnailEl(dicomId) {
      const ref = this.$refs['thumb_' + dicomId]
      return Array.isArray(ref) ? ref[0] : ref
    },
    getMakerThumbnailEl(instanceUid) {
      const ref = this.$refs['maker_thumb_' + instanceUid]
      return Array.isArray(ref) ? ref[0] : ref
    },
    onStudyCollapseChange() {
      this.scheduleLoadThumbnails()
    },
    scheduleLoadThumbnails() {
      this.$nextTick(() => {
        setTimeout(() => this.loadThumbnails(), 300)
      })
    },
    scheduleLoadMakerThumbnails() {
      this.$nextTick(() => {
        setTimeout(() => this.loadMakerThumbnails(), 150)
      })
    },
    scheduleLoadAiThumbnails() {
      this.$nextTick(() => {
        setTimeout(() => this.loadAiThumbnails(), 200)
      })
    },
    loadAiThumbnails() {
      (this.aiLesionItems || []).forEach(item => {
        const id = item.dicomAiLesionId
        const imageIds = this.buildAiThumbnailCandidates(item)
        if (!id || !imageIds.length) return

        const el = this.getAiThumbnailEl(id)
        if (!el || el.clientWidth === 0) return
        if (this.failedAiThumbs[id] || this.loadingAiThumbs[id]) return
        if (this.loadedAiThumbs[id]) return

        this.loadOneThumbnail(el, imageIds, {
          loadingMap: 'loadingAiThumbs',
          loadedMap: 'loadedAiThumbs',
          failedMap: 'failedAiThumbs',
          cacheKey: id,
          ordered: true
        })
      })
    },
    buildAiThumbnailCandidates(item) {
      const ids = []
      if (item.previewImageId) ids.push(item.previewImageId)
      pickThumbnailCandidates(item.imageIds || []).forEach(id => {
        if (id && !ids.includes(id)) ids.push(id)
      })
      return ids
    },
    getAiThumbnailEl(dicomAiLesionId) {
      const ref = this.$refs['ai_thumb_' + dicomAiLesionId]
      return Array.isArray(ref) ? ref[0] : ref
    },
    loadThumbnails() {
      for (const studyUid in this.studySeriesList) {
        if (!this.studyActiveNames.includes(String(studyUid))) continue
        const seriesList = this.getSeriesList(this.studySeriesList[studyUid])
        seriesList.forEach(series => {
          const dicomId = series.dicomId
          const imageIds = series.imageIds
          if (!dicomId || !imageIds || !imageIds.length) return

          const el = this.getThumbnailEl(dicomId)
          if (!el || el.clientWidth === 0) return
          if (this.failedThumbs[dicomId] || this.loadingThumbs[dicomId]) return
          if (this.loadedThumbs[dicomId]) return

          this.loadOneThumbnail(el, imageIds, {
            loadingMap: 'loadingThumbs',
            loadedMap: 'loadedThumbs',
            failedMap: 'failedThumbs',
            cacheKey: dicomId
          })
        })
      }
    },
    async loadOneThumbnail(el, imageIds, maps) {
      const { loadingMap, loadedMap, failedMap, cacheKey, ordered } = maps
      this.$set(this[loadingMap], cacheKey, true)
      try {
        cornerstone.enable(el)
      } catch (e) {
        // already enabled
      }
      try {
        const imageId = await loadCornerstoneThumbnail(el, imageIds, { ordered })
        this.$set(this[loadedMap], cacheKey, imageId)
      } catch (err) {
        this.$set(this[failedMap], cacheKey, true)
      } finally {
        this.$delete(this[loadingMap], cacheKey)
      }
    },
    loadMakerThumbnails() {
      const makerList = Array.isArray(this.makerInfoList)
        ? this.makerInfoList
        : Object.values(this.makerInfoList || {})

      makerList.forEach(item => {
        const el = this.getMakerThumbnailEl(item.instanceUid)
        const image = item && item.makerImage && item.makerImage.imageSave
        if (!el || !image) return

        try {
          cornerstone.enable(el)
        } catch (e) {
          // already enabled
        }

        try {
          cornerstone.displayImage(el, image)
        } catch (e) {
          // ignore thumbnail draw failures
        }
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.study-side-panel {
  width: 100%;
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
  background-color: #282c34;
  color: #fff;
  padding: 2px 0 0;

  ::v-deep aside {
    padding: 0;
    margin: 0;
    background: transparent;
  }
}

.left-collapse {
  background-color: #282c34;
  border-top: none;
  border-bottom: none;

  ::v-deep .el-collapse-item__header {
    background-color: #2d313a !important;
    color: #e3a5a5 !important;
    border-bottom: none;
    font-size: 12px;
    height: 36px;
    line-height: 36px;
    padding: 0 2px;
  }

  ::v-deep .el-collapse-item__wrap {
    background-color: #242831 !important;
    border-bottom: none;
  }

  ::v-deep .el-collapse-item__content {
    padding: 4px 0 4px;
  }
}

.left-label {
  .maker-card {
    margin: 3px 2px 5px;
    border-radius: 6px;
    border: 1px solid rgba(255, 255, 255, 0.04);
    overflow: hidden;
    background: #2b3038;

    ::v-deep .el-card__body {
      padding: 0;
    }
  }

  .left-label-item {
    background-color: #2b3038;
    color: #fff;
    font-size: 10px;
    padding: 6px 2px 7px;
    cursor: pointer;
  }

  .ct-image1 {
    width: 100%;
    height: 128px;
    display: block;
    pointer-events: none;
    background-color: #000 !important;
  }

  .maker-thumb {
    height: 128px;
  }

  .maker-thumb-img {
    width: 100%;
    height: 128px;
    display: block;
    object-fit: contain;
    background-color: #000;
  }

  .left-label-item-save {
    padding: 6px 2px 10px;

    ::v-deep .el-tooltip {
      display: block;
      width: 100%;
    }

    .uploader-btn {
      width: 100%;
    }
  }
}

.left-ai-lesion {
  .ai-lesion-card {
    margin: 3px 2px 5px;
    border-radius: 6px;
    border: 1px solid rgba(240, 169, 110, 0.25);
    overflow: hidden;
    background: #2b3038;
    position: relative;

    &.is-active {
      border-color: rgba(240, 169, 110, 0.65);
      background: #353a44;
    }

    ::v-deep .el-card__body {
      padding: 0;
    }
  }

  .ai-lesion-thumb {
    height: 120px;
  }

  .ai-lesion-info {
    background-color: #2b3038;
    color: #fff;
    font-size: 10px;
    padding: 6px 2px 7px;
    cursor: pointer;

    .info-line,
    .bottom {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    ::v-deep .el-tooltip {
      display: block;
      width: 100%;
    }
  }

  .ai-lesion-badge {
    position: absolute;
    top: 6px;
    right: 6px;
    z-index: 2;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 10px;
    color: #fff;
    background: rgba(240, 169, 110, 0.92);
    pointer-events: none;

    &--heatmap {
      background: rgba(103, 194, 58, 0.92);
    }
  }

  .ai-lesion-empty {
    padding: 8px 6px 12px;
    font-size: 10px;
    color: #999;
    text-align: center;
  }
}

.left-study {
  .left-study-collapse {
    background-color: #242831;
    border: none;
    margin: 0;

    ::v-deep .el-collapse-item__header {
      font-size: 10px;
      height: 32px;
      line-height: 32px;
      color: #d4d4d4 !important;
      padding: 0 2px;
      background-color: #242831 !important;
      border-bottom: none;
    }

    ::v-deep .el-collapse-item__content {
      padding: 1px 1px 3px;
    }
  }

  .series-card {
    margin: 2px 1px 4px;
    border-radius: 6px;
    border: 1px solid rgba(255, 255, 255, 0.04);
    overflow: hidden;
    background: #2b3038;
    position: relative;

    &.is-active {
      border-color: rgba(64, 158, 255, 0.45);
      background: #313746;
      box-shadow: none;
    }

    ::v-deep .el-card__body {
      padding: 0;
    }
  }

  .ct-image1 {
    width: 100%;
    height: 120px;
    display: block;
    pointer-events: none;
    background-color: #000 !important;
  }
  .series-info {
    padding: 6px 7px 7px !important;
    font-size: 10px;
    color: #ccc;
    cursor: pointer;
    line-height: 1.5;

    .info-line,
    .bottom {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    ::v-deep .el-tooltip {
      display: block;
      width: 100%;
    }
  }

  .study-title-text {
    display: inline-block;
    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    vertical-align: middle;
  }
}

.time {
  font-size: 10px;
  color: #999;
}

.bottom {
  margin-top: 3px;
}
</style>

<style lang="scss">
/* tooltip 挂载到 body，需非 scoped */
.study-info-tooltip {
  max-width: 480px;
  line-height: 1.5;
  word-break: break-all;
  white-space: normal;
}
</style>
