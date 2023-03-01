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
          <el-collapse-item v-if="makerFlag" title="标记管理" name="1" class="left-label" >
            <el-card v-for="item in makerInfoList"
                     :body-style="{ padding: '0px' }">
              <div style="padding: 14px;" class="left-label-item" @click="viewImage(item)">
                <div>图像id：{{ item.instanceUID }}</div>
                <div>拍摄CT时间：{{ item.studyDate }}</div>
                <div class="bottom clearfix">
                  <span class="time">标记日期:{{ item.makerTime }}</span>
                </div>
              </div>
            </el-card>
          </el-collapse-item>

          <el-collapse-item title="病人study列表" name="2" class="left-study">

            <el-collapse v-model="activeNames" v-for="(index,key) in studySeriesList" :index="key" class="left-study-collapse"

            >
              <!--              study-->
              <el-collapse-item  :title="'studyID:'+key"  class="left-study-collapse left-study-collapse-item" name="3"
                                >
<!--                @click="listenerDisplayCanvas()"-->
                <!--                series-->
                <el-card v-for="(childrenIndex,childrenKey) in studySeriesList[key]"
                         :childrenIndex="studySeriesList[key][childrenKey].dicomId"
                         :body-style="{ padding: '0px' }"
                         @click="changeCurrentImagesIds(studySeriesList[key][childrenKey])"
                >
                  <div
                    :ref="studySeriesList[key][childrenKey].dicomId"
                    class="ct-image1"
                  >
                  </div>
                  <!--  <img src="https://shadow.elemecdn.com/app/element/hamburger.9cf7b091-55e9-11e9-a976-7f4d0b07eef6.png" class="image">-->
                  <div style="padding: 14px;" class="left-study-collapse-item"
                       @click="changeCurrentImagesIds(studySeriesList[key][childrenKey])"
                  >
                    <div>id：{{ studySeriesList[key][childrenKey].dicomId }}</div>
                    <div>研究id：{{ studySeriesList[key][childrenKey].dicomCtStudyUid }}</div>
                    <div>序列id：{{ studySeriesList[key][childrenKey].dicomCtSeriesUid }}</div>
                    <div>检查部位：{{ studySeriesList[key][childrenKey].dicomCtBody }}</div>
                    <div class="bottom clearfix">
                      <span class="time">日期:{{ studySeriesList[key][childrenKey].dicomCtTime }}</span>
                      <!--                      <el-button type="text" class="button" @click="ownData(studySeriesList[key][childrenKey])">操作按钮-->
                      <!--                      </el-button>-->
                    </div>
                  </div>
                </el-card>
              </el-collapse-item>

            </el-collapse>
          </el-collapse-item>

        </el-collapse>

      </div>
    </el-scrollbar>
    <!--    </div>-->

    <div
      class="ct-father-Open"
      :style="{
         width:divTempWidth2,
       }"
      oncontextmenu=" return false"
      onmousedown="return false">
      <!--      图像-->
      <div id="dicomImage"
           ref="canvas"
           class="ct-image"
      >
      </div>
      <!--      region as-->
      <!--      病人信息-->
      <!--  病人信息    左上角-->
      <div id="topleft" v-show="isShowPatientInfo" class="overlay"
           style="position:absolute;top:10px;left:10px;font-size:15px">
        sop Instance Uid: {{ patient.sopInstanceUid }}
        <br>
        是否反转：{{ getInvert }}
      </div>
      <!--      右上角-->
      <div id="topright" v-show="isShowPatientInfo" class="overlay"
           style="position:absolute;top:10px;right:10px;font-size:15px">
        patient ID: {{ patient.patientId }},
        <br>
        patient Name: {{ patient.patientName }}
        <br>
      </div>
      <!--      左下角-->
      <div id="bottomleft" v-show="isShowPatientInfo" class="overlay"
           style="position:absolute;bottom:10px;left:10px;font-size:15px">
        Patient sex: {{ patient.patientSex }}
        <br>
        Patient age: {{ patient.patientAge }}
      </div>
      <!--      右下角-->
      <div id="bottomright" v-show="isShowPatientInfo" class="overlay"
           style="position:absolute;bottom:10px;right:10px;font-size:15px">
        Patient birth date: {{ patient.patientBirthDate }}
        <br>
      </div>
      <!--study信息-->
      <!--study:isShowStudyInfo-->
      <div id="topleft" v-show="isShowStudyInfo" class="overlay"
           style="position:absolute;top:10px;left:10px; font-size:15px">
        study Description: {{ studyInfo.studyDescription }}
        <br>
        protocol Name:{{ studyInfo.protocolName }}
      </div>
      <!--      右上角-->
      <div id="topright" v-show="isShowStudyInfo" class="overlay"
           style="position:absolute;top:10px;right:10px;font-size:15px"
      >
        accession: {{ studyInfo.accession }},
        <br>
        studyId: {{ studyInfo.studyId }}
        <br>

      </div>
      <!--      左下角-->
      <div id="bottomleft" v-show="isShowStudyInfo" class="overlay"
           style="position:absolute;bottom:10px;left:10px;font-size:15px">
        study Date: {{ studyInfo.studyDate }}
        <br>
        study Time: {{ studyInfo.studyTime }}
      </div>
      <!--      右下角-->
      <div id="bottomright" v-show="isShowStudyInfo" class="overlay"
           style="position:absolute;bottom:10px;right:10px;font-size:15px">
      </div>

      <!--       序列信息-->
      <!-- study:isShowSeriesInfo -->
      <div id="topleft" v-show="isShowSeriesInfo" class="overlay"
           style="position:absolute;top:10px;left:10px; font-size:15px">
        series Description: {{ seriesInfo.seriesDescription }}
        <br>
        series:{{ seriesInfo.series }}
      </div>
      <!--      右上角-->
      <div id="topright" v-show="isShowSeriesInfo" class="overlay"
           style="position:absolute;top:10px;right:10px;font-size:15px"
      >
        modality: {{ seriesInfo.modality }},
        <br>
        bodyPart: {{ seriesInfo.bodyPart }}
        <br>

      </div>
      <!--      左下角-->
      <div id="bottomleft" v-show="isShowSeriesInfo" class="overlay"
           style="position:absolute;bottom:10px;left:10px;font-size:15px">
        series Date: {{ seriesInfo.seriesDate }}
        <br>
        series Time: {{ seriesInfo.seriesTime }}
      </div>
      <!--      右下角-->
      <div id="bottomright" v-show="isShowSeriesInfo" class="overlay"
           style="position:absolute;bottom:10px;right:10px;font-size:15px">
      </div>

      <!--      instances 信息-->
      <!--      -->
      <div id="topleft" v-show="isShowInstancesInfo" class="overlay"
           style="position:absolute;top:10px;left:10px; font-size:15px">
        instance: {{ instanceInfo.instance }}
        <br>
        acquisition:{{ instanceInfo.acquisition }}
      </div>
      <!--      右上角-->
      <div id="topright" v-show="isShowInstancesInfo" class="overlay"
           style="position:absolute;top:10px;right:10px;font-size:15px"
      >
        acquisition Date: {{ instanceInfo.acquisitionDate }},
        <br>
        acquisition Time: {{ instanceInfo.acquisitionTime }}
        <br>

      </div>
      <!--      左下角-->
      <div id="bottomleft" v-show="isShowInstancesInfo" class="overlay"
           style="position:absolute;bottom:10px;left:10px;font-size:15px">
        content Date: {{ instanceInfo.contentDate }}
        <br>
        content Time: {{ instanceInfo.contentTime }}
      </div>
      <!--      右下角-->
      <div id="bottomright" v-show="isShowInstancesInfo" class="overlay"
           style="position:absolute;bottom:10px;right:10px;font-size:15px">
      </div>


      <!--       image 信息-->
      <!--      -->
      <div id="topleft" v-show="isShowImageInfo" class="overlay"
           style="position:absolute;top:10px;left:10px; font-size:15px">
        rows: {{ imageInfo.rows }}<br>
        columns:{{ imageInfo.columns }}<br>
        photometric Interpretation:{{ imageInfo.photometricInter }}<br>
        image Type:{{ imageInfo.imageType }}<br>
        bits Allocated:{{ imageInfo.bitsAllocated }}<br>
      </div>
      <!--      右上角-->
      <div id="topright" v-show="isShowImageInfo" class="overlay"
           style="position:absolute;top:10px;right:10px;font-size:15px"
      >
        bits Stored:{{ imageInfo.bitsStored }}<br>
        pixel Representation:{{ imageInfo.pixelRepre }}<br>
        high Bit:{{ imageInfo.highBit }}<br>
      </div>
      <!--      左下角-->
      <div id="bottomleft" v-show="isShowImageInfo" class="overlay"
           style="position:absolute;bottom:10px;left:10px;font-size:15px">
        rescale Slope:{{ imageInfo.rescaleSlope }}<br>
        rescale Intercept:{{ imageInfo.rescaleIntercept }}<br>
        image Position Patient:{{ imageInfo.imagePositionPatient }}<br>
      </div>
      <!--      右下角-->
      <div id="bottomright" v-show="isShowImageInfo" class="overlay"
           style="position:absolute;bottom:10px;right:10px;font-size:15px">
        image Orientation Patient:{{ imageInfo.imageOrientationPatient }}<br>
        pixel Spacing:{{ imageInfo.pixelSpacing }}<br>
        samples Per Pixel:{{ imageInfo.samplesPerPixel }}<br>
      </div>

      <!--     equipmentInfo   设备信息-->
      <!--      -->
      <div id="topleft" v-show="isShowEquipmentInfo" class="overlay"
           style="position:absolute;top:10px;left:10px; font-size:15px">
        manufacturer:{{ equipmentInfo.manufacturer }}<br>
        model:{{ equipmentInfo.model }}<br>
      </div>
      <!--      右上角-->
      <div id="topright" v-show="isShowEquipmentInfo" class="overlay"
           style="position:absolute;top:10px;right:10px;font-size:15px"
      >
        station Name:{{ equipmentInfo.stationName }}<br>
        AE Title:{{ equipmentInfo.AETitle }}<br>
      </div>
      <!--      左下角-->
      <div id="bottomleft" v-show="isShowEquipmentInfo" class="overlay"
           style="position:absolute;bottom:10px;left:10px;font-size:15px">
        institution Name:{{ equipmentInfo.institutionName }}<br>
        software Version:{{ equipmentInfo.softwareVersion }}<br>
      </div>
      <!--      右下角-->
      <div id="bottomright" v-show="isShowEquipmentInfo" class="overlay"
           style="position:absolute;bottom:10px;right:10px;font-size:15px">
        implementation Version Name:{{ equipmentInfo.implementationVersionName }}<br>
      </div>
      <!--     UIDS   uid信息-->
      <!--      -->
      <div id="topleft" v-show="isShowUIDS" class="overlay"
           style="position:absolute;top:10px;left:10px; font-size:15px">
        study UID:{{ UIDS.studyUID }}<br>
        series UID:{{ UIDS.seriesUID }}<br>
      </div>
      <!--      右上角-->
      <div id="topright" v-show="isShowUIDS" class="overlay"
           style="position:absolute;top:10px;right:10px;font-size:15px"
      >
        instance UID:{{ UIDS.instanceUID }}<br>
        SOP Class UID:{{ UIDS.SOPClassUID }}<br>
      </div>
      <!--      左下角-->
      <div id="bottomleft" v-show="isShowUIDS" class="overlay"
           style="position:absolute;bottom:10px;left:10px;font-size:15px">
        transfer Syntax UID:{{ UIDS.transferSyntaxUID }}<br>
        frame Of Reference UID:{{ UIDS.frameOfReferenceUID }}<br>
      </div>
      <!--      右下角-->
      <div id="bottomright" v-show="isShowUIDS" class="overlay"
           style="position:absolute;bottom:10px;right:10px;font-size:15px">
      </div>
      <!--endregion-->
    </div>

  </div>

</template>

<script>
//region 包引入
import {mapGetters, mapState, mapMutations, mapActions} from "vuex"
// import patientInfo, {trunInfo} from "./patient";
import * as cornerstone from 'cornerstone-core'
import * as dicomParser from 'dicom-parser'

import * as cornerstoneWebImageLoader from 'cornerstone-web-image-loader'
import * as cornerstoneWADOImageLoader from 'cornerstone-wado-image-loader'
import Hammer from 'hammerjs'
import * as cornerstoneMath from 'cornerstone-math'
import * as cornerstoneTools from 'cornerstone-tools'
import upload from "element-ui/packages/upload/src/ajax";
import eventBus from "@/eventBus";

cornerstoneTools.external.cornerstone = cornerstone
cornerstoneTools.external.cornerstoneMath = cornerstoneMath
cornerstoneTools.external.Hammer = Hammer
//指定要注册加载程序的基石实例
cornerstoneWADOImageLoader.external.cornerstone = cornerstone
cornerstoneWADOImageLoader.external.dicomParser = dicomParser
cornerstoneWADOImageLoader.external.cornerstoneMath = cornerstoneMath
cornerstoneWebImageLoader.external.cornerstone = cornerstone
//endregion
export default {
  name: 'ct2',
  data() {
    return {

      activeNames:['1','2','3'],
      routePatient: this.$route.params.patient,
      imageIds: [
        'wadouri:http://westChinaBackend:9000/dicom/7/1_0.dcm',
      ],
      //region dicom 各个部分信息
      patient: {
        patientId: '',
        patientName: '',
        patientBirthDate: '',
        patientSex: '',
        patientAge: '',
        sopInstanceUid: ''
      },
      studyInfo: {
        studyDescription: '',
        protocolName: '',
        accession: '',
        studyId: '',
        studyDate: '',
        studyTime: ''
      },
      seriesInfo: {
        seriesDescription: '',
        series: '',
        modality: '',
        bodyPart: '',
        seriesDate: '',
        seriesTime: ''
      },
      instanceInfo: {
        instance: '',
        acquisition: '',
        acquisitionDate: '',
        acquisitionTime: '',
        contentDate: '',
        contentTime: ''
      },
      imageInfo: {
        rows: '',
        columns: '',
        photometricInter: '',
        imageType: '',
        bitsAllocated: '',
        bitsStored: '',
        pixelRepre: '',
        highBit: '',
        rescaleSlope: '',
        rescaleIntercept: '',
        imagePositionPatient: '',
        imageOrientationPatient: '',
        pixelSpacing: '',
        samplesPerPixel: ''
      },
      equipmentInfo: {
        manufacturer: '',
        model: '',
        stationName: '',
        AETitle: '',
        institutionName: '',
        softwareVersion: '',
        implementationVersionName: ''
      },
      UIDS: {
        studyUID: '',
        seriesUID: '',
        instanceUID: '',
        SOPClassUID: '',
        transferSyntaxUID: '',
        frameOfReferenceUID: ''
      },
      //endregion
      // wheelEvents: ['mousewheel', 'DOMMouseScroll'],
      canvasStack: {
        currentImageIdIndex: 0,
        imageIds: []
      },
      divTempWidth: 'calc(100vw - 200px)',
      divTempWidth2: 'calc(80vw - 200px)',
      studyCanvasList: {},

      makerInfoList: {},
      makerFlag:true,
    }
  },
  created() {
    let that = this
    //这里可以拿到数据
    let studyList = that.$store.getters.studySeriesList
    for (let studyListKey in studyList) {
      for (let studyListKeyKey in studyList[studyListKey]) {
        that.studyCanvasList[studyList[studyListKey][studyListKeyKey].dicomId] = studyList[studyListKey][studyListKeyKey].imageIds[0]
      }
    }

  },
  mounted() {

    const that = this
    const canvas = this.$refs.canvas
    //监听滚动事件
    canvas.addEventListener(cornerstoneTools.EVENTS.MOUSE_WHEEL, this.handleScroll, false)
    canvas.addEventListener(cornerstoneTools.EVENTS.MEASUREMENT_COMPLETED, function (params) {
      //得到image
      let imageSave = cornerstone.getImage(canvas)
      that.makerImageDeal(imageSave, canvas)
    });
    that.initCanvas()
    //下面：initListCanvas的初始化必须进行
    that.initListCanvas()
  },
  upload() {

  },
  methods: {
    viewImage(row){
      let canvas = this.$refs.canvas
        cornerstone.displayImage(canvas, row.makerImage)
    },
    makerImageDeal(imageSave, canvas) {
      let that = this
      //解析图像信息
      const byteArray = imageSave.data.byteArray
      const dataSet = dicomParser.parseDicom(byteArray)
      let makerInfo = {}
      let instanceUID = dataSet.string('x00080018')
      makerInfo.instanceUID = dataSet.string('x00080018')
      makerInfo.studyUID = dataSet.string('x0020000d')
      makerInfo.seriesUID = dataSet.string('x0020000e')
      makerInfo.studyDate = dataSet.string('x00080020')
      //获取病人信息
      makerInfo.patCardId = that.$store.getters.patCardId
      makerInfo.patientName = that.$store.getters.patName
      //获取医生信息和企业信息
      makerInfo.makerDoctor = that.$store.getters.name
      makerInfo.makerEnterpriseName = that.$store.getters.enterpriseName
      //设置标记图像时间
      makerInfo.makerTime = new Date().toLocaleString()
      //存储图像在服务器上的地址
      makerInfo.markerImageAddress = ""
      makerInfo.makerDescription = ''
      //canvas类型图像信息，方便后面上传，数据库表中没有该字段
      makerInfo.makerImage = imageSave
      //将此次标记图像和信息存储到页面中
      console.log(that.makerInfoList)
      that.makerInfoList[instanceUID] = makerInfo
      that.makerFlag=false
      that.$nextTick(() => {
        that.makerFlag=true
      });
      // const viewport = cornerstone.getViewport(canvas)
      // const zoom = viewport.scale.toFixed(2)
      // const cols = imageSave.columns * zoom
      // const rows = imageSave.rows * zoom
      // let myCanvas = document.createElement('canvas')
      // let canvasTemp = canvas.firstElementChild
      // console.log("打印",canvasTemp)
      // myCanvas = that.cropCanvas(
      //   canvasTemp,
      //   Math.round(canvasTemp.width / 2 - cols / 2),
      //   Math.round(canvasTemp.height / 2 - rows / 2),
      //   cols, rows)
      // // 创建一个a标签
      // let a = document.createElement("a")
      // // let imagemy = myCanvas.toDataURL(`image/jpeg`)
      // a.href = myCanvas.toDataURL(`image/png`)
      // // a.href = myCanvas.toDataURL(`image/${type}`)
      // a.download = `test.png`
      // document.body.appendChild(a) // Required for this to work in FireFox为使其在FireFox中工作，这是必要的
      // a.click()
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
      debugger
      return newCanvas
    },
    listenerDisplayCanvas() {
      this.initListCanvas()
    },
    showDicom() {
      let that = this
      //初始化工具
      cornerstoneTools.init()
      const canvas = this.$refs.canvas
      //初始化tools,方法包含是否开启触摸监听，鼠标监听，等
      // 在 DOM 中将 canvas 元素注册到 cornerstone

      cornerstone.enable(canvas)
      //初始化自己的工具设置
      this.initTools(canvas)
      // this.initTools(canvasMini)
      //展示
      this.displayOneCanvasImage()
      // this.displayOneCanvasImage1()

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
      for (const temp in that.studyCanvasList) {
        let tempCanvas = that.$refs[temp][0]
        let address = that.studyCanvasList[temp]
        cornerstone.enable(tempCanvas)
        cornerstone.loadAndCacheImage(address).then(function (image) {
          cornerstone.displayImage(tempCanvas, image)
        })
      }
    },
    convertCanvasToImage(canvas) {
      //新Image对象，可以理解为DOM
      var image = new Image();
      // canvas.toDataURL 返回的是一串Base64编码的URL，当然,浏览器自己肯定支持
      // 指定格式 PNG
      image.src = canvas.toDataURL("image/png");
      return image;
    },
    displayOneCanvasImage1() {
      let that = this
      const canvasMini = this.$refs.canvasMini
      // let tempIndex = that.canvasStack.currentImageIdIndex
      debugger
      return cornerstone.loadAndCacheImage(that.canvasStack.imageIds[1])
        .then(function (image) {
          //设置视口
          // let viewport = {}
          // const viewport = cornerstone.getDefaultViewportForImage(
          //   canvasMini,
          //   image,
          // )
          // viewport.scale=1
          // viewport.invert = that.getInvert
          // viewport.hflip = that.getHflip
          // viewport.vflip = that.getVflip
          // const views = cornerstone.getViewport(canvasMini)
          // cornerstone.displayImage(canvasMini, image)
          // canvasMini.style.width = '200px'
          // canvasMini.style.height = "200px"
          debugger
          cornerstone.displayImage(canvasMini, image)
          // cornerstone.resize(canvasMini)
          console.log("sadasdas")
        })
    },
    displayOneCanvasImage() {
      let that = this
      const canvas = this.$refs.canvas
      // console.log("-------------------展示第_张---------", that.canvasStack.currentImageIdIndex)
      let tempIndex = that.canvasStack.currentImageIdIndex
      return cornerstone.loadAndCacheImage(that.canvasStack.imageIds[tempIndex])
        .then(function (image) {
          //设置视口
          let viewport = {}
          // viewport.scale=1
          viewport.invert = that.getInvert
          viewport.hflip = that.getHflip
          viewport.vflip = that.getVflip
          // viewport.pixelReplication = that.getPixelReplication
          // viewport.translation.x=100
          // viewport.translation.y=100
          // // viewport.voi.windowCenter=100
          // // viewport.voi.windowWidth=200
          // viewport.pixelReplication=
          // console.log("获取图像信息", viewport)
          //打印，看数据
          // console.log('----------------image-----------------', image)
          //设置图像视口
          // const viewport = cornerstone.getDefaultViewportForImage(
          //   canvas,
          //   image,
          // )
          // const views = cornerstone.getViewport(canvas)
          // console.log("获取图像信息", image)
          //显示
          // let canvas=this.$refs.canvas

          // canvas.style.width = "100%"
          // canvas.style.height = "calc(100vh - 84px)"
          cornerstone.displayImage(canvas, image, viewport)
          // cornerstone.resize(canvas)
          // 图像信息显示
          that.imageInfos(image)
        })
    },
    //图像信息处理
    imageInfos(image) {
      let that = this
      //region dicom 信息解析映射
      // console.log('image.data.byteArray', image.data.byteArray)
      const byteArray = image.data.byteArray
      const dataSet = dicomParser.parseDicom(byteArray)

      that.patient.patientId = dataSet.string('x00100020')
      that.patient.patientName = dataSet.string("x00100010")
      that.patient.patientBirthDate = dataSet.string('x00100030')
      that.patient.patientSex = dataSet.string('x00100040')
      that.patient.patientAge = dataSet.string('x00101010')
      that.patient.sopInstanceUid = dataSet.string('x00080018')
      console.log(that.patient.sopInstanceUid)
      that.studyInfo.studyDescription = dataSet.string('x00081030')
      that.studyInfo.protocolName = dataSet.string('x00181030')
      that.studyInfo.accession = dataSet.string('x00080050')
      that.studyInfo.studyId = dataSet.string('x00200010')
      that.studyInfo.studyDate = dataSet.string('x00080020')
      that.studyInfo.studyTime = dataSet.string('x00080030')

      that.seriesInfo.seriesDescription = dataSet.string('x0008103e')
      that.seriesInfo.series = dataSet.string('x00200011')
      that.seriesInfo.modality = dataSet.string('x00080060')
      that.seriesInfo.bodyPart = dataSet.string('x00180015')
      that.seriesInfo.seriesDate = dataSet.string('x00080021')
      that.seriesInfo.seriesTime = dataSet.string('x00080031')

      that.instanceInfo.instance = dataSet.string('x00200013')
      that.instanceInfo.acquisition = dataSet.string('x00200012')
      that.instanceInfo.acquisitionDate = dataSet.string('x00080022')
      that.instanceInfo.acquisitionTime = dataSet.string('x00080032')
      that.instanceInfo.contentDate = dataSet.string('x00080023')
      that.instanceInfo.contentTime = dataSet.string('x00080033')

      that.imageInfo.rows = dataSet.string('x00280010')
      that.imageInfo.columns = dataSet.string('x00280011')
      that.imageInfo.photometricInter = dataSet.string('x00280004')
      that.imageInfo.imageType = dataSet.string('x00080008')
      that.imageInfo.bitsAllocated = dataSet.string('x00280100')
      that.imageInfo.bitsStored = dataSet.string('x00280101')
      that.imageInfo.highBit = dataSet.string('x00280102')
      that.imageInfo.pixelRepre = dataSet.string('x00280103')
      that.imageInfo.rescaleSlope = dataSet.string('x00281053')
      that.imageInfo.rescaleIntercept = dataSet.string('x00281052')
      that.imageInfo.imagePositionPatient = dataSet.string('x00200032')
      that.imageInfo.imageOrientationPatient = dataSet.string('x00200037')
      that.imageInfo.pixelSpacing = dataSet.string('x00280030')
      that.imageInfo.samplesPerPixel = dataSet.string('x00280002')

      that.equipmentInfo.manufacturer = dataSet.string('x00080070')
      that.equipmentInfo.model = dataSet.string('x00081090')
      that.equipmentInfo.stationName = dataSet.string('x00081010')
      that.equipmentInfo.AETitle = dataSet.string('x00020016')
      that.equipmentInfo.institutionName = dataSet.string('x00080080')
      that.equipmentInfo.softwareVersion = dataSet.string('x00181020')
      that.equipmentInfo.implementationVersionName = dataSet.string('x00020013')

      that.UIDS.studyUID = dataSet.string('x0020000d')
      that.UIDS.seriesUID = dataSet.string('x0020000e')
      that.UIDS.instanceUID = dataSet.string('x00080018')
      that.UIDS.SOPClassUID = dataSet.string('x00080016')
      that.UIDS.transferSyntaxUID = dataSet.string('x00020010')
      that.UIDS.frameOfReferenceUID = dataSet.string('x00200052')
      //endregion

      //region 存储标记图像的信息
      // let tempMakerImage={}

      //endregion
    },

    //滚动处理
    handleScroll(e) {
      //滚动 展示下一个图像
      this.displayOneCanvasImage();
    },
    changeInvert() {
      this.displayOneCanvasImage();
    },
    getPatientData(value) {
      let that = this
      const dealWith = new Promise((resolve, reject) => {
        getDicomListByPatCardId({patCardId: value}).then(result => {
          let list = result.data.items;
          let newList = []
          list.forEach(one => {
            let temp = {...one}
            temp.imageIds = []
            for (var i = 1; i <= temp.dicomCtCount; i++) {
              let path = temp.dicomCtPath.substring(0, temp.dicomCtPath.lastIndexOf("/"));
              let newPath = 'wadouri:' + path + '/' + i.toString() + '.dcm'
              temp.imageIds.push(newPath)
              that.imageIds.push(newPath)
              that.canvasStack.imageIds.push(newPath)
            }
          })
          resolve()
        }).catch(res => {
          reject("fail")
        })
      })
      dealWith.then(() => {
        that.showDicom()
      })

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
      const that = this
      let studyList = this.studySeriesList
      for (let studyListKey in studyList) {
        let flag = false
        for (let studyListKeyKey in studyList[studyListKey]) {
          if (studyList[studyListKey][studyListKeyKey].imageIds.length > 0) {
            // that.canvasStack.imageIds=that.imageIds
            that.canvasStack.imageIds = studyList[studyListKey][studyListKeyKey].imageIds
            flag = true
            break
          }
        }
        if (flag === true) {
          break
        }
      }
      that.showDicom()
    },
    ownData(row) {
      // console.log('---', row)
    },
    /**
     * 点击更换当前正在阅片的图像
     * @param row
     */
    changeCurrentImagesIds(row) {
      console.log("-------", row)
      this.canvasStack.imageIds = row.imageIds
      this.canvasStack.currentImageIdIndex = 0
      this.displayOneCanvasImage()
    },
    ...mapActions(['updatePatientsStudySeries']),

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
    /**
     * 样式开关
     * @returns {boolean}
     */
    // isCollapse() {
    //   this.isOpen = this.$store.getters.sidebar.opened
    //   console.log("isopen", isOpen)
    //   return this.$store.getters.sidebar.opened
    // },
    //  endregion
    studySeriesList() {
      return this.$store.getters.studySeriesList
    }
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
        color: white !important;
        //border-bottom-color: #ea768b;
      }

      ::v-deep .el-collapse-item__wrap {
        background-color: #17191c !important;
        color: white !important;
      }

      ::v-deep .el-collapse-item__content {
        padding-bottom: 0px;
      }

      .left-label {
        .left-label-item {
          background-color: #282c34 !important;
          color: white !important;
          font-size: 1px;
          width: 20vw;
        }
      }

      .left-study {
        display: block;

        .left-study-collapse {
          background-color: #282c34 !important;
          color: white !important;
          display: block;

          .left-study-collapse-item {

            .ct-image1 {
              width: 20vw;
              height: 35vh;
              display: block;
              //阻止所有鼠标事件
              pointer-events: none;
              background-color: #000 !important;
            }

            background-color: #282c34 !important;
            font-size: 1px;
            color: white;
            display: block;
          }
        }
      }
    }


  }

  .ct-father-Open {
    //width: 70%;
    //height: 100%;
    //width: var(--width2);/\*/
    height: 100%;
    position: relative;
    background-color: #000 !important;
    color: white;

    .ct-image {
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

//.ct-father-notOpen {
//  width: 90vw;
//  height: 100%;
//  position: relative;
//  color: white;
//}

//.ct-image {
//  width: 100%;
//  //width: 87.9vw;
//  height: 100%;
//  //width: 87.9vw;
//  //height: 88vh;
//  background-color: #000000;
//}

//.info{
//  width: 87vw;
//  height: 90vh;
//  background-color: red;
//
//  z-index: 99;
//  position: absolute;
//}

</style>

