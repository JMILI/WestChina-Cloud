<template>
  <div class="ct-container"
       :style="{
         width:divTempWidth,
       }
">
    <!--div 方病人CT序列列 表-->
    <el-scrollbar style="height:100%">
      <div class="left" v-show="openStudySeries">

        <el-collapse v-model="activeNames" class="left-collapse">
          <el-collapse-item v-if="makerFlag" title="新增标记管理" name="1" class="left-label">
            <el-card v-for="item in makerInfoList"
                     :body-style="{ padding: '0px' }">
              <div class="left-label-item" @click="viewImage(item)">
                <div>图像id：{{ item.instanceUid }}</div>
                <div>拍摄CT时间：{{ item.studyDate }}</div>
                <div class="bottom clearfix">
                  <span class="time">标记日期:{{ item.makerTime }}</span>
                </div>
              </div>
            </el-card>
            <div v-if="isDisplaySave" class="left-label-item-save">

              <el-button class="uploader-btn" @click="submitUpload">保存</el-button>
              <br>
              <span class="noteOfMe"> 解释：点击保存按钮，系统将上传标记的图像!!!</span>
            </div>
          </el-collapse-item>

          <el-collapse-item title="标记列表" class="left-study" name="2">
            <el-card v-for="(item) in makerImageList"
                     :body-style="{ padding: '0px' }">
              <div
                :ref="item.dicomMakerId"
                class="ct-image1"
              >
              </div>

              <div style="padding: 14px;" class="left-study-collapse-item"
                   @click="changeCurrentImagesIds(item)">
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
    </el-scrollbar>

    <div
      class="ct-father-Open"
      :style="{
         width:divTempWidth2,
       }">
      <!--      图像-->
      <div id="dicomImage"
           ref="canvas"
           class="ct-image"
      >
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
import {minioUrl} from '../../settings'
cornerstoneTools.external.cornerstone = cornerstone
cornerstoneTools.external.cornerstoneMath = cornerstoneMath
cornerstoneTools.external.Hammer = Hammer
cornerstoneWebImageLoader.external.cornerstone = cornerstone
//endregion
export default {
  name: 'makerImage',
  data() {
    return {
      activeNames: ['1', '2', '3'],
      routePatient: this.$route.params.patient,
      canvasStack: {
        currentImageIdIndex: 0,
        imageIds: []
      },
      divTempWidth: 'calc(100vw - 200px)',
      divTempWidth2: 'calc(80vw - 200px)',
      makerImageList: this.$store.getters.makerImageList,
      makerInfoList: {},
      makerFlag: true,
      isDisplaySave: false,
      dicomPrefix: 'wadouri:'
    }
  },
  created() {
  },
  mounted() {
    const that = this
    const canvas = this.$refs.canvas
    //监听滚动事件
    canvas.addEventListener(cornerstoneTools.EVENTS.MEASUREMENT_COMPLETED, function (params) {
      //得到image
      let imageSave = cornerstone.getImage(canvas)
      that.makerImageDeal(imageSave, canvas)
    });
    canvas.addEventListener(cornerstoneTools.EVENTS.MEASUREMENT_REMOVED, function (params) {
      //得到image
      let imageSave = cornerstone.getImage(canvas)
      that.makerImageDeal(imageSave, canvas)
    });



    //展示选中的那个
    that.initCanvas()
    //下面：initListCanvas的初始化必须进行
    that.initListCanvas()
  },
  activated(){
    this.getList();
  },
  methods: {
    ...mapActions(['makerImageInitInfo']),

    makerImageDeal(imageSave, canvas) {
      let that = this
      //获取图像信息
      let tempInfo = that.$store.getters.makerImageInitInfo
      //获取医生信息和企业信息
      let instanceUid = tempInfo.instanceUid
      let makerInfo = {}
      makerInfo.instanceUid = tempInfo.instanceUid
      makerInfo.studyUid = tempInfo.studyUid
      makerInfo.seriesUid = tempInfo.seriesUid
      makerInfo.studyDate = tempInfo.studyDate
      //获取病人信息
      makerInfo.patCardId = tempInfo.patCardId
      makerInfo.patientName = tempInfo.patientName

      //获取医生信息和企业信息
      makerInfo.makerDoctor = that.$store.getters.name
      makerInfo.makerEnterpriseName = that.$store.getters.enterpriseName
      //图像信息
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

      //设置标记图像时间
      makerInfo.makerTime = new Date().toLocaleString()
      //存储图像在服务器上的地址
      makerInfo.makerImageAddress = ""
      makerInfo.makerDescription = ''
      //生成png照片
      const viewport = cornerstone.getViewport(canvas)
      const zoom = viewport.scale.toFixed(3)
      const cols = imageSave.columns * zoom
      const rows = imageSave.rows * zoom
      let myCanvas = document.createElement('canvas')
      let canvasTemp = canvas.firstElementChild
      // console.log("打印",canvasTemp)
      myCanvas = that.cropCanvas(
        canvasTemp,
        Math.round(canvasTemp.width / 2 - cols / 2),
        Math.round(canvasTemp.height / 2 - rows / 2),
        cols, rows)
      //canvas转base64
      // let image = new Image();
      // canvas.toDataURL 返回的是一串Base64编码的URL，当然,浏览器自己肯定支持
      // 指定格式 PNG
      let base64Image = myCanvas.toDataURL("image/png");
      // image.src = myCanvas.toDataURL("image/png")
      let datetime = new Date().getTime()
      let fileName = "/" + makerInfo.instanceUid + "_" + datetime + ".png"
      let fileOfImage = that.dataURLtoFile(base64Image, fileName)
      //记录信息
      //canvas类型图像信息，方便后面上传，数据库表中没有该字段，临时存储起来,
      // fileOfImage:需要保存的图像，png类型文件
      //imageSave：存放可以直接通过：displayImage(imageSave)展示该图像
      let makerImage = {}
      makerImage.fileOfImage = fileOfImage
      makerImage.imageSave = imageSave
      makerInfo.makerImage = makerImage
      // //将此次标记图像和信息存储到页面中
      that.makerInfoList[instanceUid] = makerInfo
      that.makerFlag = false
      that.$nextTick(() => {
        that.makerFlag = true
        that.isDisplaySave = true
      });
    },
    submitUpload() {
      let that = this
      that.$modal.loading("正在上传数据中");
      const upload = new Promise((resolve, reject) => {
        for (let makerInfoListKey in that.makerInfoList) {
          //上传前处理
          let tempDicomMaker = that.makerInfoList[makerInfoListKey]
          const uploadImage = new Promise((resolve, reject) => {
            let formDateOfMakerImage = new FormData(); //创建form对象
            formDateOfMakerImage.append('file', tempDicomMaker.makerImage.fileOfImage, tempDicomMaker.makerImage.fileOfImage.name);//通过append向form对象添加数据
            resolve(formDateOfMakerImage)
          })
          //  上传
          uploadImage.then(formDateOfMakerImage => {
            return new Promise((resolve, reject) => {
              ctFile(formDateOfMakerImage).then(res => {
                if (res.url !== '') {
                  //  封装对象
                  let dicomMaker = {}
                  dicomMaker = tempDicomMaker
                  dicomMaker.makerImage = ""
                  dicomMaker.makerImageAddress = res.url
                  console.log(res.url)
                  resolve(dicomMaker)
                } else {
                  reject("上传失败，请检查网络")
                }
              })
            })
          })
            .then((dicomMaker) => {
              addMaker(dicomMaker).then(res => {
                that.getList()
              })
              resolve()
            })
        }
      })

      //上传完之后，清空列表
      upload.then((resolve, reject) => {
        that.$nextTick(() => {

          setTimeout(() => {
            that.makerInfoList = {}
            that.makerFlag = true
            that.isDisplaySave = false
            that.$modal.closeLoading();

            that.makerImageList.forEach(item => {
              let tempCanvas = that.$refs[item.dicomMakerId][0]
              // cornerstone.disable(tempCanvas)
              let address = item.makerImageAddress
              console.log(address)
              cornerstone.loadImage(address).then(function (image) {
                cornerstone.enable(tempCanvas)
                cornerstone.displayImage(tempCanvas, image)
              })
            })
          }, 500)
        });
      })
    },
    /** 查询病人标记过的dicom图像列表 */
    getList() {
      let that = this
      let patCardId = this.$store.getters.makerOfPatCardId
      getDicomMakerByPatCardId({patCardId: patCardId}).then(response => {
        that.makerImageList = response.data.items;
        console.log(that.makerImageList)
        that.updateMakerImageList(that.makerImageList)
      });
    },
    displayOneCanvasImage() {
      let that = this
      const canvas = that.$refs.canvas
      let makerImage = that.$store.getters.makerImageInitInfo
      let bucketNameOfMe = that.$store.getters.bucketName
      let newPath = minioUrl + bucketNameOfMe + '/' +makerImage.makerImageAddress
      // let url = makerImage.makerImageAddress
      cornerstone.loadImage(newPath).then(function (image) {
        let viewport = {}
        // viewport.scale=1
        viewport.invert = that.getInvert
        viewport.hflip = that.getHflip
        viewport.vflip = that.getVflip
        cornerstone.displayImage(canvas, image, viewport);
        //  当前图像的一些信息，有利于标记工具的使用
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
    convertCanvasToImage(canvas) {
      //参考 https://blog.csdn.net/yongjian_123/article/details/106857298
      //新Image对象，可以理解为DOM
      let image = new Image();
      // canvas.toDataURL 返回的是一串Base64编码的URL，当然,浏览器自己肯定支持
      // 指定格式 PNG
      let base64Image = canvas.toDataURL("image/png");
      // image.src = canvas.toDataURL("image/png")
      this.dataURLtoFile(base64Image, "myfile.png")
      return image;
    },
    dataURLtoFile(base64Image, fileName) {//将base64转换为文件，dataurl为base64字符串，filename为文件名（必须带后缀名，如.jpg,.png）
      const dataArr = base64Image.split(",");
      let opType = base64Image.split(";base64")[0].slice(5);

      const byteString = atob(dataArr[1]);
      const options = {
        type: opType,
        endings: "native"
      }
      const u8Arr = new Uint8Array(byteString.length);
      for (let i = 0; i < byteString.length; i++) {
        u8Arr[i] = byteString.charCodeAt(i);
      }
      // console.log(u8Arr)
      return new File([u8Arr], fileName, options);
    },
    //点击
    viewImage(row) {
      let canvas = this.$refs.canvas
      cornerstone.displayImage(canvas, row.makerImage.imageSave)
    },


    /**
     * 重新绘制图像并返回
     * @param canvas 原来canvas图像
     * @param x
     * @param y
     * @param width
     * @param height
     * @returns {HTMLCanvasElement}
     */
    cropCanvas(canvas, x, y, width, height) {
      // create a temp canvas创建一个临时的画布
      const newCanvas = document.createElement('canvas')
      // set its dimensions
      newCanvas.width = width
      newCanvas.height = height
      // draw the canvas in the new resized temp canvas
      newCanvas.getContext('2d').drawImage(canvas, x, y, width, height, 0, 0, width, height)
      return newCanvas
    },
    initTools(canvas) {
      //stack滚动工具
      let that = this
      console.log("设置默认工具")
      const StackScrollMouseWheelTool = cornerstoneTools.StackScrollMouseWheelTool
      cornerstoneTools.addTool(StackScrollMouseWheelTool)
      //激活
      cornerstoneTools.setToolActive('StackScrollMouseWheel', {})
      //增加堆栈管理工具
      cornerstoneTools.addStackStateManager(canvas, ['stack'])
      cornerstoneTools.addToolState(canvas, 'stack', that.canvasStack)
      that.styleOfCanvas()
    },
    styleOfCanvas() {
      //可以设置激活工具的颜色，也就是鼠标覆盖在上面的颜色
      cornerstoneTools.toolColors.setActiveColor('rgb(255, 255, 0)');
      //Set color for inactive tools
      cornerstoneTools.toolColors.setToolColor('rgb(0, 255, 0)');
      // Set the tool width
      cornerstoneTools.toolStyle.setToolWidth(2);
      // Set the tool font and font size
      const fontFamily =
        'Work Sans, Roboto, OpenSans, HelveticaNeue-Light, Helvetica Neue Light, Helvetica Neue, Helvetica, Arial, Lucida Grande, sans-serif';
      cornerstoneTools.textStyle.setFont(`16px ${fontFamily}`);
    },
    initListCanvas() {
      let that = this
      let bucketNameOfMe = that.$store.getters.bucketName
      that.makerImageList.forEach(item => {
        let tempCanvas = that.$refs[item.dicomMakerId][0]

        let address = minioUrl + bucketNameOfMe + '/' + item.makerImageAddress

        cornerstone.enable(tempCanvas)
        cornerstone.loadImage(address).then(function (image) {
          cornerstone.displayImage(tempCanvas, image)
        })
      })
    },
    changeInvert() {
      this.displayOneCanvasImage();
    },
    changeCurrentImagesIds(row) {
      console.log("2222222")

      this.makerImageInitInfo(row)
      this.displayOneCanvasImage()
    },
    /*
    改变视图样式
     */
    changeWidth() {
      console.log(this.isOpen, this.openStudySeries)
      if (this.isOpen === true && this.openStudySeries === true) {
        this.divTempWidth = 'calc(100vw - 200px)'
        this.divTempWidth2 = 'calc(80vw - 200px)'
      } else if (this.isOpen === false && this.openStudySeries === true) {
        this.divTempWidth = 'calc(100vw - 54px)'
        this.divTempWidth2 = 'calc(80vw - 54px)'
      } else if (this.isOpen === false && this.openStudySeries === false) {
        this.divTempWidth = 'calc(100vw - 54px)'
        this.divTempWidth2 = 'calc(100vw - 54px)'
      } else {
        this.divTempWidth = 'calc(100vw - 200px)'
        this.divTempWidth2 = 'calc(100vw - 200px)'
      }
      this.displayOneCanvasImage()
    },
    /*
    设置默认的ct图像提供操作。
     */
    initCanvas() {
      let that = this
      //初始化工具
      cornerstoneTools.init()
      const canvas = this.$refs.canvas
      //初始化tools,方法包含是否开启触摸监听，鼠标监听，等
      // 在 DOM 中将 canvas 元素注册到 cornerstone
      cornerstone.enable(canvas)
      //初始化自己的工具设置
      this.initTools(canvas)
      this.displayOneCanvasImage()
    },
    ...mapActions(['updatePatientsStudySeries', 'updateMakerNeed','updateMakerImageList']),

  },
  beforeRouteLeave(to, from, next) {
    console.log("---------makerImage-----from----", from)
    console.log("---------makerImage------to-----", to)
    if ((to.name === null) || (to.name === undefined)) {
      this.$router.replace({name: 'maker'})
    } else {
      next();
    }

  },
  computed: {
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

    //region dicom 信息展示开关
    isShowPatientInfo() {
      return this.$store.getters.isShowPatientInfo
    },
    isShowStudyInfo() {
      return this.$store.getters.isShowStudyInfo
    },
    isShowSeriesInfo() {
      return this.$store.getters.isShowSeriesInfo
    },
    isShowInstancesInfo() {
      return this.$store.getters.isShowInstancesInfo
    },
    isShowImageInfo() {
      return this.$store.getters.isShowImageInfo
    },
    isShowEquipmentInfo() {
      return this.$store.getters.isShowEquipmentInfo
    },
    isShowUIDS() {
      return this.$store.getters.isShowUIDS
    },

    openStudySeries() {
      return this.$store.getters.openStudy
    },
    isOpen() {
      console.log("isopen", this.$store.getters.sidebar.opened)
      return this.$store.getters.sidebar.opened
    },
  },
  watch: {
    getInvert: function () {
      this.displayOneCanvasImage()
    },
    getHflip: function () {
      this.displayOneCanvasImage()
    },
    getVflip: function () {
      this.displayOneCanvasImage()
    },
    getPixelReplication: function () {
      this.displayOneCanvasImage()
    },
    openStudySeries: function () {
      this.changeWidth()
    },
    isOpen: function () {
      this.changeWidth()
    },
    //  监视并修改样式宽度
  },
  components: {}
}

</script>

<style lang="scss" scoped>
@import "~@assets/styles/mixin.scss";
@import "~@assets/styles/variables.scss";

.overlay {
  /* prevent text selection on overlay */
  -webkit-touch-callout: none;
  -webkit-user-select: none;
  -khtml-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;

  /* ignore pointer event on overlay */
  pointer-events: none;
}

.ct-container {

  box-sizing: border-box;
  //width: 100%;
  //height: 100%;
  //--openStudyWidth:200px;
  //width: var(--width); //设置为变量
  height: calc(100vh - 84px);
  //transition: width 0.28s;
  background-color: #282c34;
  display: flex;
  flex-direction: row;
  //设置 滚动条，x轴隐藏
  ::v-deep .el-scrollbar__wrap {
    overflow-x: hidden;
  }

  .left {
    padding-left: 5px;
    width: 20vw;
    height: 100vh;
    background-color: #282c34 !important;
    //字体颜色
    color: white !important;

    .left-collapse {
      //width: 100%;
      //height: 100%;
      background-color: #282c34 !important;
      display: block;

      ::v-deep .el-collapse-item__header {
        background-color: #282c34 !important;
        color: #e3a5a5 !important;
        border-bottom-color: #f8f6f6;
        font-size: 10px;
      }

      ::v-deep .el-collapse-item__wrap {
        background-color: #17191c !important;
        color: white !important;
      }

      ::v-deep .el-collapse-item__content {
        padding-bottom: 0px;
      }

      ::v-deep .el-card {
        border-radius: 28px;
        border: 3px solid #e6ebf5;
        background-color: #FFFFFF;
        overflow: hidden;
        color: #303133;
        -webkit-transition: 0.3s;
        transition: 0.3s;
        margin-top: 5px;
        margin-bottom: 5px;
        margin-right: 5px;
      }

      .left-label {
        .left-label-item {
          background-color: #282c34 !important;
          color: white !important;
          font-size: 10px;
          width: 20vw;
          padding: 14px;
        }

        .left-label-item-save {
          background-color: #282c34 !important;
          color: #e3a5a5 !important;
          font-size: 10px;
          width: 20vw;
          height: auto;

          ::v-deep.uploader-btn {
            margin: 3% 23.6%;
          }

          ::v-deep .el-button--medium {
            width: 50%;
            font-size: 14px;
            border-radius: 22px;
            background-color: #343536;
            border: none;
            color: white;
          }

          .noteOfMe {
            margin-bottom: 1%;
          }

        }
      }

      .left-study {
        display: block;

        .ct-image1 {
          width: 20vw;
          height: 35vh;
          display: block;
          //阻止所有鼠标事件
          pointer-events: none;
          background-color: #000 !important;
        }

        .left-study-collapse-item {
          background-color: #282c34 !important;
          font-size: 10px;
          color: white;
          display: block;
        }
      }
    }


  }

  .ct-father-Open {
    height: 100%;
    position: relative;
    background-color: #000 !important;
    color: white;

    .ct-image {
      background-color: #000 !important;
      width: 100%;
      height: 100%;
    }
  }
}


.time {
  font-size: 13px;
  color: #999;
}

.bottom {
  margin-top: 13px;
  line-height: 12px;
}

.button {
  padding: 0;
  float: right;
}


.clearfix:before,
.clearfix:after {
  display: table;
  content: "";
}

.clearfix:after {
  clear: both
}


</style>

