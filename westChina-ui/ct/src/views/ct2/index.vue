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
          <el-collapse-item v-if="makerFlag" title="标记管理" name="1" class="left-label">
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


          <el-collapse-item title="病人study列表" name="2" class="left-study">

            <el-collapse v-model="activeNames" v-for="(index,key) in studySeriesList" :index="key"
                         class="left-study-collapse"

            >
              <!--              study-->
              <el-collapse-item :title="'studyID:'+key" class="left-study-collapse left-study-collapse-item" name="3"
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
        rows: {{ imageInfoOfDicom.rows }}<br>
        columns:{{ imageInfoOfDicom.columns }}<br>
        photometric Interpretation:{{ imageInfoOfDicom.photometricInter }}<br>
        image Type:{{ imageInfoOfDicom.imageType }}<br>
        bits Allocated:{{ imageInfoOfDicom.bitsAllocated }}<br>
      </div>
      <!--      右上角-->
      <div id="topright" v-show="isShowImageInfo" class="overlay"
           style="position:absolute;top:10px;right:10px;font-size:15px"
      >
        bits Stored:{{ imageInfoOfDicom.bitsStored }}<br>
        pixel Representation:{{ imageInfoOfDicom.pixelRepre }}<br>
        high Bit:{{ imageInfoOfDicom.highBit }}<br>
      </div>
      <!--      左下角-->
      <div id="bottomleft" v-show="isShowImageInfo" class="overlay"
           style="position:absolute;bottom:10px;left:10px;font-size:15px">
        rescale Slope:{{ imageInfoOfDicom.rescaleSlope }}<br>
        rescale Intercept:{{ imageInfoOfDicom.rescaleIntercept }}<br>
        pixel Spacing:{{ imageInfoOfDicom.pixelSpacing }}<br>
        samples Per Pixel:{{ imageInfoOfDicom.samplesPerPixel }}<br>
        image Position Patient:{{ imageInfoOfDicom.imagePositionPatient }}<br>
        image Orientation Patient:{{ imageInfoOfDicom.imageOrientationPatient }}<br>

      </div>
      <!--      右下角-->
      <div id="bottomright" v-show="isShowImageInfo" class="overlay"
           style="position:absolute;bottom:10px;right:10px;font-size:15px">

      </div>

      <!--     equipmentInfo   设备信息-->
      <!--      -->
      <div id="topleft" v-show="isShowEquipmentInfo" class="overlay"
           style="position:absolute;top:10px;left:10px; font-size:15px">
        manufacturer:{{ equipmentInfo.manufacturer }}<br>
        model:{{ equipmentInfo.model }}<br>
      </div>
      <!--      右上角-->
      <div id="topright" v-show="isShowEquipmentInfo" class="overlay" style="position:absolute;top:10px;right:10px;font-size:15px">
        station Name:{{ equipmentInfo.stationName }}<br>
        AE Title:{{ equipmentInfo.AeTitle }}<br>
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
import {mapActions} from "vuex"
import * as cornerstone from 'cornerstone-core'
import * as dicomParser from 'dicom-parser'

import * as cornerstoneWebImageLoader from 'cornerstone-web-image-loader'
import * as cornerstoneWADOImageLoader from 'cornerstone-wado-image-loader'
import Hammer from 'hammerjs'
import * as cornerstoneMath from 'cornerstone-math'
import * as cornerstoneTools from '@cornerstoneTools'
import {ctFile} from "../../api/ct/ctFileUpload";
import {addMaker} from "../../api/ct/maker";

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
      activeNames: ['1', '2', '3'],
      //region dicom 各个部分信息
      patient: {
        patientId: null,
        patientName: null,
        patientBirthDate: null,
        patientSex: null,
        patientAge: null,
        sopInstanceUid: null
      },
      studyInfo: {
        studyDescription: null,
        protocolName: null,
        accession: null,
        studyId: null,
        studyDate: null,
        studyTime: null
      },
      seriesInfo: {
        seriesDescription: null,
        series: null,
        modality: null,
        bodyPart: null,
        seriesDate: null,
        seriesTime: null
      },
      instanceInfo: {
        instance: null,
        acquisition: null,
        acquisitionDate: null,
        acquisitionTime: null,
        contentDate: null,
        contentTime: null
      },
      imageInfoOfDicom: {
        rows: null,
        columns: null,
        photometricInter: null,
        imageType: null,
        bitsAllocated: null,
        bitsStored: null,
        pixelRepre: null,
        highBit: null,
        rescaleSlope: null,
        rescaleIntercept: null,
        imagePositionPatient: null,
        imageOrientationPatient: null,
        pixelSpacing: null,
        samplesPerPixel: null
      },
      equipmentInfo: {
        manufacturer: null,
        model: null,
        stationName: null,
        AeTitle: null,
        institutionName: null,
        softwareVersion: null,
        implementationVersionName: null
      },
      UIDS: {
        studyUID: null,
        seriesUID: null,
        instanceUID: null,
        SOPClassUID: null,
        transferSyntaxUID: null,
        frameOfReferenceUID: null
      },
      //endregion
      canvasStack: {
        currentImageIdIndex: 0,
        isUPOrDown: 0,
        isInvertAboutUpAndDown: 0,
        currentImageId: null,
        imageIds: []
      },
      divTempWidth: 'calc(100vw - 200px)',
      divTempWidth2: 'calc(80vw - 200px)',
      studyCanvasList: {},

      makerInfoList: {},
      makerFlag: true,
      isDisplaySave: false,
      scaleOfMe: 1.5,


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

    let that = this
    let canvas = this.$refs.canvas
    window.addEventListener("load", () => {
      //写入你想要执行的代码

      that.$store.dispatch('app/setDefaultOpenedOfMe')
      that.setDefaultStudy()
    });
    //监听滚动事件
    canvas.addEventListener(cornerstoneTools.EVENTS.MOUSE_WHEEL, this.handleScroll, false)
    //MEASUREMENT_REMOVED 使用橡皮擦时触发
    canvas.addEventListener(cornerstoneTools.EVENTS.MEASUREMENT_REMOVED, function (params) {
      that.makerImageDeal()
    });
    canvas.addEventListener(cornerstoneTools.EVENTS.MEASUREMENT_COMPLETED, function (params) {
      //操作完成保存图像
      that.makerImageDeal()
    });

    that.initCanvas()
    //下面：initListCanvas的初始化必须进行
    that.initListCanvas()
  },

  methods: {
    displayOneCanvasImage() {
      let that = this
      const canvas = this.$refs.canvas
      // console.log("tools", cornerstoneTools)
      // console.log("-------------------展示第_张---------", that.canvasStack.currentImageIdIndex)
      let tempIndex = that.canvasStack.currentImageIdIndex
      return cornerstone.loadAndCacheImage(that.canvasStack.imageIds[tempIndex])
        .then(function (image) {

          let dealImageInfo = new Promise((resolve, reject) => {
            // 图像信息显示
            that.canvasStack.currentImageId = image.imageId
            that.imageInfos(image)
            // console.log(image)
            resolve()
          })
          dealImageInfo.then(() => {
            //设置视口
            let viewport = {}
            viewport.scale = that.scaleOfMe
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
          })

        })

    },
    makerImageDeal() {
      let that = this
      //canvas中包含标注信息
      let canvas = that.$refs.canvas
      //主要用来获取图像信息，这些信息里不包含标注的信息
      // console.log(cornerstone.getImage(canvas))

      let cachedImagesList = cornerstone.imageCache.cachedImages
      let imageSave = null
      for (const item of cachedImagesList) {
        if (item.imageId === that.canvasStack.currentImageId) {
          imageSave = item.image
        }
      }
      //解析图像信息
      const byteArray = imageSave.data.byteArray
      const dataSet = dicomParser.parseDicom(byteArray)
      let makerInfo = {}
      let instanceUid = dataSet.string('x00080018')
      makerInfo.instanceUid = dataSet.string('x00080018')
      makerInfo.studyUid = dataSet.string('x0020000d')
      makerInfo.seriesUid = dataSet.string('x0020000e')
      makerInfo.studyDate = dataSet.string('x00080020')
      //获取病人信息
      makerInfo.patCardId = that.$store.getters.patCardId
      makerInfo.patientName = that.$store.getters.patName
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
      const zoom = viewport.scale.toFixed(5)
      const cols = imageSave.columns * zoom
      const rows = imageSave.rows * zoom
      let myCanvas = document.createElement('canvas')
      let canvasTemp = canvas.firstElementChild
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
      // console.log(base64Image)
      // image.src = myCanvas.toDataURL("image/png")
      let datetime = new Date().getTime()
      let fileName = makerInfo.instanceUid + "_" + datetime + ".png"
      let fileOfImage = that.dataURLtoFile(base64Image, fileName)

      //记录信息
      //canvas类型图像信息，方便后面上传，数据库表中没有该字段，临时存储起来,
      // fileOfImage:需要保存的图像，png类型文件
      //imageSave：存放可以直接通过：displayImage(imageSave)展示该图像
      let makerImage = {}
      makerImage.fileOfImage = fileOfImage
      makerImage.imageSave = imageSave
      makerInfo.makerImage = makerImage
      // console.log("打印",cornerstone)
      // console.log("打印",cornerstoneTools)

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
          let uploadImage = new Promise((resolve, reject) => {
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
          }).then((dicomMaker) => {
            addMaker(dicomMaker).then(res => {
              console.log(res)
            })
            resolve()
          })
        }
      })

      //上传完之后，清空列表
      upload.then((resolve, reject) => {
        that.$nextTick(() => {
          that.makerInfoList = {}
          that.makerFlag = true
          that.isDisplaySave = false
          setTimeout(() => {
            that.$modal.closeLoading();
          }, 500)
        });
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
    isCanvas(i) {
      return i instanceof HTMLCanvasElement;
    },
    isImage(i) {
      return i instanceof HTMLImageElement;
    },
    //点击
    viewImage(row) {
      let canvas = this.$refs.canvas
      cornerstone.displayImage(canvas, row.makerImage.imageSave)
      // cornerstone.drawImage(row.makerImage.imageSave)
      this.imageInfos(row.makerImage.imageSave)
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

    },
    initTools(canvas) {
      //stack滚动工具
      let that = this
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
      cornerstoneTools.toolColors.setActiveColor('rgb(246,97,119)');
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
      setTimeout(() => {
        for (const temp in that.studyCanvasList) {
          let tempCanvas = that.$refs[temp][0]
          let address = that.studyCanvasList[temp]
          cornerstone.enable(tempCanvas)
          cornerstone.loadImage(address).then(function (image) {
            cornerstone.displayImage(tempCanvas, image)
          })
        }
      }, 300)
    },


    //图像信息处理
    imageInfos(image) {
      let that = this
      //region dicom 信息解析映射
      const byteArray = image.data.byteArray
      const dataSet = dicomParser.parseDicom(byteArray)
      that.$nextTick(() => {
        that.patient.patientId = dataSet.string('x00100020')
        that.patient.patientName = dataSet.string("x00100010")
        // console.log(that.patient.patientName)
        that.patient.patientBirthDate = dataSet.string('x00100030')
        that.patient.patientSex = dataSet.string('x00100040')
        that.patient.patientAge = dataSet.string('x00101010')
        that.patient.sopInstanceUid = dataSet.string('x00080018')
        // console.log(that.patient.sopInstanceUid)
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

        that.imageInfoOfDicom.rows = dataSet.int16('x00280010')
        that.imageInfoOfDicom.columns = dataSet.int16('x00280011')
        that.imageInfoOfDicom.samplesPerPixel = dataSet.int16('x00280002')
        that.imageInfoOfDicom.bitsAllocated = dataSet.int16('x00280100')
        that.imageInfoOfDicom.bitsStored = dataSet.int16('x00280101')
        that.imageInfoOfDicom.highBit = dataSet.int16('x00280102')
        that.imageInfoOfDicom.pixelRepre = dataSet.int16('x00280103')
        that.imageInfoOfDicom.photometricInter = dataSet.string('x00280004')
        that.imageInfoOfDicom.imageType = dataSet.string('x00080008')
        that.imageInfoOfDicom.rescaleSlope = dataSet.string('x00281053')
        that.imageInfoOfDicom.rescaleIntercept = dataSet.string('x00281052')
        that.imageInfoOfDicom.imagePositionPatient = dataSet.string('x00200032')
        that.imageInfoOfDicom.imageOrientationPatient = dataSet.string('x00200037')
        that.imageInfoOfDicom.pixelSpacing = dataSet.string('x00280030')

        that.equipmentInfo.manufacturer = dataSet.string('x00080070')
        that.equipmentInfo.model = dataSet.string('x00081090')
        that.equipmentInfo.stationName = dataSet.string('x00081010')

        that.equipmentInfo.AeTitle = dataSet.string('x00020016')

        that.equipmentInfo.institutionName = dataSet.string('x00080080')
        that.equipmentInfo.softwareVersion = dataSet.string('x00181020')
        that.equipmentInfo.implementationVersionName = dataSet.string('x00020013')

        that.UIDS.studyUID = dataSet.string('x0020000d')
        that.UIDS.seriesUID = dataSet.string('x0020000e')
        that.UIDS.instanceUID = dataSet.string('x00080018')
        that.UIDS.SOPClassUID = dataSet.string('x00080016')
        that.UIDS.transferSyntaxUID = dataSet.string('x00020010')
        that.UIDS.frameOfReferenceUID = dataSet.string('x00200052')


        //  当前图像的一些信息，有利于标记工具的使用
        let makerNeed = {
          columnPixelSpacingOfMe: image.columnPixelSpacing,
          columnsOfMe: image.columns,
          interceptOfMe: image.intercept,
          rowsOfMe: image.rows,
          rowPixelSpacingOfMe: image.rowPixelSpacing,
          slopeOfMe: image.slope,
          windowCenterOfMe: image.windowCenter,
          windowWidthOfMe: image.windowWidth,
          scaleOfMe: that.scaleOfMe,
          isDicomOfMe: 1,
        }
        that.updateMakerNeed(makerNeed)

      })
    },

    //滚动处理
    handleScroll(e) {
      //滚动 展示一个图像
      let up = -1
      let down = 1
      let upOrDown = e.detail.direction
      let isUPOrDown = this.canvasStack.isUPOrDown
      let currentIndex = this.canvasStack.currentImageIdIndex
      if (isUPOrDown === 0 && upOrDown === up) {
        //想要看上一张，发现isUPOrDown===0，也就是，初始化状态，之前没有使用鼠标滚轮，还是展示第一张
      } else if (isUPOrDown === 0 && upOrDown === down) {
        //想要看下一张，发现isUPOrDown===0，也就是，初始化状态，之前没有使用鼠标滚轮，展示下一张
        this.canvasStack.isUPOrDown = down
        this.canvasStack.currentImageIdIndex = currentIndex + down
      } else if (isUPOrDown === down && upOrDown === up) {
        //想要看上一张，发现isUPOrDown===1，也就是上次也是鼠标滚轮下移操作，，展示上一张
        this.canvasStack.isUPOrDown = up
        this.canvasStack.currentImageIdIndex = currentIndex + up + up
      } else if (isUPOrDown === down && upOrDown === down) {

      } else if (isUPOrDown === up && upOrDown === up) {

      } else if (isUPOrDown === up && upOrDown === down) {
        this.canvasStack.isUPOrDown = down
        this.canvasStack.currentImageIdIndex = currentIndex + down
      }
      this.displayOneCanvasImage();
      //设置，翻转，像素翻转的标志变量
      this.canvasStack.isInvertAboutUpAndDown = this.canvasStack.isUPOrDown
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
    ...mapActions(['updateMakerNeed', 'setDefaultStudy']),
    //提供下面的监视变量的使用，getInvert，getHflip，getVflip，getPixelReplication
    watchAssist() {
      this.canvasStack.currentImageIdIndex = this.canvasStack.currentImageIdIndex - this.canvasStack.isInvertAboutUpAndDown
      this.displayOneCanvasImage();
      this.canvasStack.isInvertAboutUpAndDown = 0
    },

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
    //  endregion
    studySeriesList() {
      return this.$store.getters.studySeriesList
    },


  },
  watch: {
    getInvert: function () {
      this.watchAssist()
    },
    getHflip: function () {
      this.watchAssist()
    },
    getVflip: function () {
      this.watchAssist()
    },
    getPixelReplication: function () {
      this.watchAssist()
    },
    openStudySeries: function () {
      this.changeWidth()
      this.watchAssist()
    },
    isOpen: function () {
      this.changeWidth()
      this.watchAssist()
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
            font-size: 10px;
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

