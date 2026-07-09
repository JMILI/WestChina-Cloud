<template>
  <div class="ct-container">
    <aside v-if="openStudySeries" class="study-aside">
      <div class="maker-side-panel">
        <el-collapse v-model="activeNames" class="left-collapse">
          <el-collapse-item v-if="makerFlag" title="新增标记管理" name="1" class="left-label">
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
              <div class="left-label-item" @click="viewImage(item)">
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
                <el-button class="uploader-btn" size="small" @click="submitUpload">保存</el-button>
              </el-tooltip>
            </div>
          </el-collapse-item>

          <el-collapse-item title="标记列表" class="left-study" name="2">
            <el-card
              v-for="item in makerImageList"
              :key="item.dicomMakerId"
              :body-style="{ padding: '0px' }"
              class="series-card"
              :class="{ 'is-active': activeMakerId === item.dicomMakerId }"
            >
              <div
                :ref="'thumb_' + item.dicomMakerId"
                class="ct-image1"
              ></div>
              <div
                class="left-study-collapse-item series-info"
                @click="changeCurrentImagesIds(item)"
              >
                <div>id：{{ item.dicomMakerId }}</div>
                <div>实例id：{{ item.instanceUid }}</div>
                <div>研究id：{{ item.studyUid }}</div>
                <div>序列id：{{ item.seriesUid }}</div>
                <div>标记医生:{{ item.makerDoctor }}</div>
                <div class="bottom clearfix">
                  <span class="time">标记日期:{{ item.makerTime }}</span>
                </div>
              </div>
            </el-card>
          </el-collapse-item>
        </el-collapse>
      </div>
    </aside>

    <div class="viewports-wrap">
      <div class="ct-father-Open">
        <div id="dicomImage" ref="canvas" class="ct-image"></div>
      </div>
    </div>
  </div>
</template>

<script>
//region 包引入
import {mapActions} from "vuex"
import * as cornerstone from 'cornerstone-core'

import * as cornerstoneWebImageLoader from 'cornerstone-web-image-loader'
import Hammer from 'hammerjs'
import * as cornerstoneMath from 'cornerstone-math'
import * as cornerstoneTools from '@cornerstoneTools'
import {ctFile} from "../../api/ct/ctFileUpload";
import {addMaker, getDicomMakerByPatCardId} from "../../api/ct/maker";
import {getMinioUrl} from '@/utils/minioBase'
cornerstoneTools.external.cornerstone = cornerstone
cornerstoneTools.external.cornerstoneMath = cornerstoneMath
cornerstoneTools.external.Hammer = Hammer
cornerstoneWebImageLoader.external.cornerstone = cornerstone
//endregion
export default {
  name: 'makerImage',
  data() {
    return {
      activeNames: ['1', '2'],
      activeMakerId: null,
      routePatient: this.$route.params.patient,
      canvasStack: {
        currentImageIdIndex: 0,
        imageIds: []
      },
      makerImageList: this.$store.getters.makerImageList,
      makerInfoList: {},
      makerFlag: true,
      isDisplaySave: false,
      loadedThumbs: {}
    }
  },
  computed: {
    makerItems() {
      return Object.values(this.makerInfoList || {})
    },
    getInvert() {
      return this.$store.getters.invert
    },
    getHflip() {
      return this.$store.getters.hflip
    },
    getVflip() {
      return this.$store.getters.vflip
    },
    getPixelReplication() {
      return this.$store.getters.pixelReplication
    },
    openStudySeries() {
      return this.$store.getters.openStudy
    },
    isOpen() {
      return this.$store.getters.sidebar.opened
    }
  },
  watch: {
    getInvert() {
      this.displayOneCanvasImage()
    },
    getHflip() {
      this.displayOneCanvasImage()
    },
    getVflip() {
      this.displayOneCanvasImage()
    },
    getPixelReplication() {
      this.displayOneCanvasImage()
    },
    openStudySeries() {
      this.changeWidth()
    },
    isOpen() {
      this.changeWidth()
    },
    makerImageList: {
      deep: true,
      handler() {
        this.scheduleLoadThumbnails()
      }
    },
    makerInfoList: {
      deep: true,
      handler() {
        // previewUrl uses img tag; no extra load needed
      }
    }
  },
  mounted() {
    const that = this
    const canvas = this.$refs.canvas
    canvas.addEventListener(cornerstoneTools.EVENTS.MEASUREMENT_COMPLETED, function () {
      const imageSave = cornerstone.getImage(canvas)
      that.makerImageDeal(imageSave, canvas)
    })
    canvas.addEventListener(cornerstoneTools.EVENTS.MEASUREMENT_REMOVED, function () {
      const imageSave = cornerstone.getImage(canvas)
      that.makerImageDeal(imageSave, canvas)
    })

    that.initCanvas()
    that.scheduleLoadThumbnails()
  },
  activated() {
    this.getList()
  },
  methods: {
    ...mapActions(['makerImageInitInfo', 'updatePatientsStudySeries', 'updateMakerNeed', 'updateMakerImageList']),

    makerImageDeal(imageSave, canvas) {
      let that = this
      let tempInfo = that.$store.getters.makerImageInitInfo
      let instanceUid = tempInfo.instanceUid
      let makerInfo = {}
      makerInfo.instanceUid = tempInfo.instanceUid
      makerInfo.studyUid = tempInfo.studyUid
      makerInfo.seriesUid = tempInfo.seriesUid
      makerInfo.studyDate = tempInfo.studyDate
      makerInfo.patCardId = tempInfo.patCardId
      makerInfo.patientName = tempInfo.patientName
      makerInfo.makerDoctor = that.$store.getters.name
      makerInfo.makerEnterpriseName = that.$store.getters.enterpriseName
      makerInfo.makerColumns = that.$store.getters.makerNeed.columnsOfMe
      makerInfo.makerRows = that.$store.getters.makerNeed.rowsOfMe
      makerInfo.makerColumnPixelSpacing = that.$store.getters.makerNeed.columnPixelSpacingOfMe
      makerInfo.makerRowPixelSpacing = that.$store.getters.makerNeed.rowPixelSpacingOfMe
      makerInfo.makerSlope = that.$store.getters.makerNeed.slopeOfMe
      makerInfo.makerIntercept = that.$store.getters.makerNeed.interceptOfMe
      makerInfo.makerWindowCenter = that.$store.getters.makerNeed.windowCenterOfMe
      makerInfo.makerWindowWidth = that.$store.getters.makerNeed.windowWidthOfMe
      makerInfo.makerScale = that.$store.getters.makerNeed.scaleOfMe
      makerInfo.makerIsDicom = 0
      makerInfo.makerTime = new Date().toLocaleString()
      makerInfo.makerImageAddress = ""
      makerInfo.makerDescription = ''

      const viewport = cornerstone.getViewport(canvas)
      const zoom = viewport.scale.toFixed(3)
      const cols = imageSave.columns * zoom
      const rows = imageSave.rows * zoom
      let canvasTemp = canvas.firstElementChild
      let myCanvas = that.cropCanvas(
        canvasTemp,
        Math.round(canvasTemp.width / 2 - cols / 2),
        Math.round(canvasTemp.height / 2 - rows / 2),
        cols, rows)
      let base64Image = myCanvas.toDataURL("image/png")
      let datetime = new Date().getTime()
      let fileName = "/" + makerInfo.instanceUid + "_" + datetime + ".png"
      let fileOfImage = that.dataURLtoFile(base64Image, fileName)

      let makerImage = {}
      makerImage.fileOfImage = fileOfImage
      makerImage.imageSave = imageSave
      makerImage.previewUrl = base64Image
      makerInfo.makerImage = makerImage

      that.$set(that.makerInfoList, instanceUid, makerInfo)
      that.makerFlag = false
      that.$nextTick(() => {
        that.makerFlag = true
        that.isDisplaySave = true
      })
    },
    submitUpload() {
      let that = this
      that.$modal.loading("正在上传数据中");
      const upload = new Promise((resolve) => {
        for (let makerInfoListKey in that.makerInfoList) {
          let tempDicomMaker = that.makerInfoList[makerInfoListKey]
          const uploadImage = new Promise((resolve) => {
            let formDateOfMakerImage = new FormData()
            formDateOfMakerImage.append('file', tempDicomMaker.makerImage.fileOfImage, tempDicomMaker.makerImage.fileOfImage.name)
            resolve(formDateOfMakerImage)
          })
          uploadImage.then(formDateOfMakerImage => {
            return new Promise((resolve, reject) => {
              ctFile(formDateOfMakerImage).then(res => {
                if (res.url !== '') {
                  let dicomMaker = tempDicomMaker
                  dicomMaker.makerImage = ""
                  dicomMaker.makerImageAddress = res.url
                  resolve(dicomMaker)
                } else {
                  reject("上传失败，请检查网络")
                }
              })
            })
          }).then((dicomMaker) => {
            addMaker(dicomMaker).then(() => {
              that.getList()
            })
            resolve()
          })
        }
      })

      upload.then(() => {
        that.$nextTick(() => {
          that.makerInfoList = {}
          that.makerFlag = true
          that.isDisplaySave = false
          setTimeout(() => {
            that.$modal.closeLoading()
            that.scheduleLoadThumbnails()
          }, 500)
        })
      })
    },
    getList() {
      let that = this
      let patCardId = this.$store.getters.makerOfPatCardId
      getDicomMakerByPatCardId({patCardId: patCardId}).then(response => {
        that.makerImageList = response.data.items
        that.updateMakerImageList(that.makerImageList)
        that.scheduleLoadThumbnails()
      })
    },
    displayOneCanvasImage() {
      let that = this
      const canvas = that.$refs.canvas
      let makerImage = that.$store.getters.makerImageInitInfo
      let bucketNameOfMe = that.$store.getters.bucketName
      let newPath = getMinioUrl() + bucketNameOfMe + '/' + makerImage.makerImageAddress
      cornerstone.loadImage(newPath).then(function (image) {
        let viewport = {}
        viewport.invert = that.getInvert
        viewport.hflip = that.getHflip
        viewport.vflip = that.getVflip
        cornerstone.displayImage(canvas, image, viewport)
        let makerNeed = {
          columnPixelSpacingOfMe: makerImage.makerColumnPixelSpacing,
          interceptOfMe: makerImage.makerIntercept,
          rowPixelSpacingOfMe: makerImage.makerRowPixelSpacing,
          slopeOfMe: makerImage.makerSlope,
          scaleOfMe: makerImage.makerScale,
          isDicomOfMe: makerImage.makerIsDicom,
          columnsOfMe: makerImage.makerColumns,
          rowsOfMe: makerImage.makerRows,
          windowCenterOfMe: makerImage.makerWindowCenter,
          windowWidthOfMe: makerImage.makerWindowWidth,
        }
        that.updateMakerNeed(makerNeed)
      })
    },
    dataURLtoFile(base64Image, fileName) {
      const dataArr = base64Image.split(",")
      let opType = base64Image.split(";base64")[0].slice(5)
      const byteString = atob(dataArr[1])
      const options = {
        type: opType,
        endings: "native"
      }
      const u8Arr = new Uint8Array(byteString.length)
      for (let i = 0; i < byteString.length; i++) {
        u8Arr[i] = byteString.charCodeAt(i)
      }
      return new File([u8Arr], fileName, options)
    },
    viewImage(row) {
      let canvas = this.$refs.canvas
      cornerstone.displayImage(canvas, row.makerImage.imageSave)
    },
    cropCanvas(canvas, x, y, width, height) {
      const newCanvas = document.createElement('canvas')
      newCanvas.width = width
      newCanvas.height = height
      newCanvas.getContext('2d').drawImage(canvas, x, y, width, height, 0, 0, width, height)
      return newCanvas
    },
    initTools(canvas) {
      const StackScrollMouseWheelTool = cornerstoneTools.StackScrollMouseWheelTool
      cornerstoneTools.addTool(StackScrollMouseWheelTool)
      cornerstoneTools.setToolActive('StackScrollMouseWheel', {})
      cornerstoneTools.addStackStateManager(canvas, ['stack'])
      cornerstoneTools.addToolState(canvas, 'stack', this.canvasStack)
      this.styleOfCanvas()
    },
    styleOfCanvas() {
      cornerstoneTools.toolColors.setActiveColor('rgb(255, 255, 0)')
      cornerstoneTools.toolColors.setToolColor('rgb(0, 255, 0)')
      cornerstoneTools.toolStyle.setToolWidth(2)
      const fontFamily =
        'Work Sans, Roboto, OpenSans, HelveticaNeue-Light, Helvetica Neue Light, Helvetica Neue, Helvetica, Arial, Lucida Grande, sans-serif'
      cornerstoneTools.textStyle.setFont(`16px ${fontFamily}`)
    },
    getThumbnailEl(dicomMakerId) {
      const ref = this.$refs['thumb_' + dicomMakerId]
      return Array.isArray(ref) ? ref[0] : ref
    },
    scheduleLoadThumbnails() {
      this.$nextTick(() => {
        setTimeout(() => this.initListCanvas(), 300)
      })
    },
    initListCanvas() {
      let that = this
      let bucketNameOfMe = that.$store.getters.bucketName
      that.makerImageList.forEach(item => {
        const dicomMakerId = item.dicomMakerId
        const el = that.getThumbnailEl(dicomMakerId)
        if (!el || el.clientWidth === 0) return

        let address = getMinioUrl() + bucketNameOfMe + '/' + item.makerImageAddress
        if (that.loadedThumbs[dicomMakerId] === address) return

        try {
          cornerstone.enable(el)
        } catch (e) {
          // already enabled
        }

        cornerstone.loadImage(address).then(function (image) {
          cornerstone.displayImage(el, image)
          that.$set(that.loadedThumbs, dicomMakerId, address)
        }).catch(() => {})
      })
    },
    changeCurrentImagesIds(row) {
      this.activeMakerId = row.dicomMakerId
      this.makerImageInitInfo(row)
      this.displayOneCanvasImage()
    },
    changeWidth() {
      this.$nextTick(() => {
        const canvas = this.$refs.canvas
        if (canvas) {
          cornerstone.resize(canvas)
        }
        if (this.openStudySeries) {
          this.scheduleLoadThumbnails()
        }
        this.displayOneCanvasImage()
      })
    },
    initCanvas() {
      cornerstoneTools.init()
      const canvas = this.$refs.canvas
      cornerstone.enable(canvas)
      this.initTools(canvas)
      this.displayOneCanvasImage()
    }
  },
  beforeRouteLeave(to, from, next) {
    if ((to.name === null) || (to.name === undefined)) {
      this.$router.replace({name: 'maker'})
    } else {
      next()
    }
  }
}
</script>

<style lang="scss" scoped>
@import "~@assets/styles/mixin.scss";
@import "~@assets/styles/variables.scss";

.ct-container {
  box-sizing: border-box;
  width: 100%;
  height: calc(100vh - 84px);
  background-color: #282c34;
  display: flex;
  flex-direction: row;
  overflow: hidden;

  .study-aside {
    flex-shrink: 0;
    width: 18vw;
    min-width: 210px;
    max-width: 280px;
    height: 100%;
    overflow: hidden;
    background: #282c34;
    padding: 0 2px;
    box-sizing: border-box;
  }

  .viewports-wrap {
    flex: 1;
    min-width: 0;
    height: 100%;
    display: flex;
    background: #000;
  }

  .ct-father-Open {
    flex: 1;
    min-width: 0;
    height: 100%;
    position: relative;
    background-color: #000 !important;
    color: white;

    .ct-image {
      width: 100%;
      height: 100%;
      background-color: #000 !important;
    }
  }
}

.maker-side-panel {
  width: 100%;
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
  background-color: #282c34;
  color: #fff;
  padding: 2px 0 0;

  &::-webkit-scrollbar {
    width: 8px;
  }

  &::-webkit-scrollbar-track {
    background: #2b2f37;
    border-radius: 8px;
  }

  &::-webkit-scrollbar-thumb {
    background: #7a7f87;
    border-radius: 8px;
    border: 2px solid #2b2f37;
  }

  &::-webkit-scrollbar-thumb:hover {
    background: #90959d;
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

    div {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
  }

  .maker-thumb-img {
    width: 100%;
    height: 128px;
    display: block;
    object-fit: contain;
    background-color: #000;
  }

  .maker-thumb {
    width: 100%;
    height: 128px;
    display: block;
    pointer-events: none;
    background-color: #000 !important;
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

.left-study {
  .series-card {
    margin: 2px 1px 4px;
    border-radius: 6px;
    border: 1px solid rgba(255, 255, 255, 0.04);
    overflow: hidden;
    background: #2b3038;

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
    padding: 6px 2px 7px !important;
    font-size: 10px;
    color: #ccc;
    cursor: pointer;
    line-height: 1.5;

    div {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
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
