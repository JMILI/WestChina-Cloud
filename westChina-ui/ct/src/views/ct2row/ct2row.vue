<template>
  <div class="ct-container"
       :style="{
         width:divTempWidth,
       }"
  >
    <el-scrollbar>
      <div class="left" v-show="openStudySeries">

        <el-collapse v-model="activeName" class="left-collapse">
          <!--          <ul class="infinite-list" v-infinite-scroll="load" style="overflow:auto">-->
          <el-collapse-item title="标记管理" name="1" class="left-label">
            <div class="left-label-item">与现实生活一致：与现实生活的流程、逻辑</div>
            <div class="left-label-item">在界面中一致：所有的元素和结构需保</div>
          </el-collapse-item>
          <el-collapse-item title="病人study列表" name="2" class="left-study">
            <el-collapse v-model="activeName" class="left-study-collapse">
              <el-collapse-item title="1.2.156.14702.6.146.20210819000527" name="3" class="left-study-collapse-item">

                <el-card :body-style="{ padding: '0px' }">
                  <div
                    ref="canvasMini"
                    class="ct-image1"
                  >
                  </div>
                  <!--                <img src="https://shadow.elemecdn.com/app/element/hamburger.9cf7b091-55e9-11e9-a976-7f4d0b07eef6.png" class="image">-->
                  <div style="padding: 14px;">
                    <span>1.3.12.2.1107.5.1.4.77426.30000021081723585752900164339</span>
                    <div class="bottom clearfix">
                      <time class="time">1.3.12.2.1107.5.1.4.77426.30000021081723585752900164339</time>
                      <el-button type="text" class="button">操作按钮</el-button>
                    </div>
                  </div>
                </el-card>
              </el-collapse-item>
              <el-collapse-item title="1.2.156.14702.6.146.20210819000527" name="4" class="left-color">
                <div class="left-color">与现实生活一致：与现实生活的流程、逻辑</div>
                <div class="left-color">在界面中一致：所有的元素和结构需保</div>
              </el-collapse-item>
              <el-collapse-item title="1.2.156.14702.6.146.20210819000527" name="5" class="left-color">
                <div class="left-color">与现实生活一致：与现实生活的流程、逻辑</div>
                <div class="left-color">在界面中一致：所有的元素和结构需保</div>
              </el-collapse-item>
              <el-collapse-item title="1.2.156.14702.6.146.20210819000527" name="6" class="left-color">
                <div class="left-color">与现实生活一致：与现实生活的流程、逻辑</div>
                <div class="left-color">在界面中一致：所有的元素和结构需保</div>
              </el-collapse-item>
              <el-collapse-item title="1.2.156.14702.6.146.20210819000527" name="4" class="left-color">
                <div class="left-color">与现实生活一致：与现实生活的流程、逻辑</div>
                <div class="left-color">在界面中一致：所有的元素和结构需保</div>
              </el-collapse-item>
              <el-collapse-item title="1.2.156.14702.6.146.20210819000527" name="5" class="left-color">
                <div class="left-color">与现实生活一致：与现实生活的流程、逻辑</div>
                <div class="left-color">在界面中一致：所有的元素和结构需保</div>
              </el-collapse-item>
              <el-collapse-item title="1.2.156.14702.6.146.20210819000527" name="6" class="left-color">
                <div class="left-color">与现实生活一致：与现实生活的流程、逻辑</div>
                <div class="left-color">在界面中一致：所有的元素和结构需保</div>
              </el-collapse-item>
            </el-collapse>
          </el-collapse-item>

        </el-collapse>

      </div>
    </el-scrollbar>
    <!--    <div >-->
    <!--      -->
    <!--    </div>-->
    <div
      class="ct-father-Open1"
      :style="{
         width:divTempWidth1,
       }"
      oncontextmenu="return false"
      onmousedown="return false"
    >
      <div id="dicomImage1"
           data-id="1"
           ref="canvas"
           class="ct-image"
           @mouseover="hoverOver(1)"
           @click="select(1,'dicomImage1')"
      >
      </div>
    </div>

    <div
      class="ct-father-Open2"
      :style="{
         width:divTempWidth2,
       }"
      oncontextmenu="return false"
      onmousedown="return false"
    >
      <div
        id="dicomImage2"
        ref="canvas2"
        class="ct-image"
        @mouseover="hoverOver(2)"
        @click="select(2,'dicomImage2')"
      >
      </div>
    </div>
    <!--    <el-button @click="saveImages()">-->
    <!--      保存-->
    <!--    </el-button>-->
    <!--    <div class="minioBox">-->
    <!--      <el-button style="marginRight:10px;" @click="getFileName" size="mini" type="success">选择文件</el-button>-->
    <!--      -->
    <!--      <input accept="*/*" type="file" multiple="multiple" id="minIoFile" ref="minIoFile" v-show="false"-->
    <!--             @change="getFile"-->
    <!--      >-->
    <!--      <el-button v-if="fileList.length>0" style="marginRight:10px;" @click="upload" size="mini" type="success">上传-->
    <!--      </el-button>-->
    <!--    </div>-->
    <!--    <ul class="uploadFileList">-->
    <!--      <li v-for="item of fileList" :key="item.index">-->
    <!--        <span class="subString">{{ item.name }}</span>&nbsp;-->
    <!--        <span>({{ (item.size / 1024 / 1024).toFixed(2) }}M)</span>-->
    <!--        <div class="floatRight" style="float: right;">-->
    <!--          <i class="el-icon-close" style="cursor: pointer;" @click="deleteMinioFile(index)"></i>-->
    <!--        </div>-->
    <!--      </li>-->
    <!--    </ul>-->
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
import {ctFile} from "../../api/ct/ctFileUpload";
import stream from "stream";
import cornerstoneFileImageLoader from "cornerstone-file-image-loader/src";

cornerstoneTools.external.cornerstone = cornerstone
cornerstoneTools.external.cornerstoneMath = cornerstoneMath
cornerstoneTools.external.Hammer = Hammer
//指定要注册加载程序的基石实例
cornerstoneWADOImageLoader.external.cornerstone = cornerstone
cornerstoneWADOImageLoader.external.dicomParser = dicomParser
cornerstoneWADOImageLoader.external.cornerstoneMath = cornerstoneMath
//如果是从服务器端请求png,jpeg文件，使用这个文件
cornerstoneWebImageLoader.external.cornerstone = cornerstone
//如果是直接从前端上传的png,jpeg文件，使用这个加载图像
cornerstoneFileImageLoader.external.cornerstone = cornerstone
//endregion
export default {
  name: 'ct2row',
  data() {
    return {
      element1: this.$refs.canvas,
      element2: this.$refs.canvas2,
      imageIds1: [
        'wadouri:http://tune01:9000/dicom/7/1_0.dcm',
        'wadouri:http://tune01:9000/dicom/7/2_1.dcm',
        'wadouri:http://tune01:9000/dicom/7/3_2.dcm',
        'wadouri:http://tune01:9000/dicom/7/4_3.dcm',
        'wadouri:http://tune01:9000/dicom/7/5_4.dcm',
        'wadouri:http://tune01:9000/dicom/7/6_5.dcm',
        'wadouri:http://tune01:9000/dicom/7/7_6.dcm',
        'wadouri:http://tune01:9000/dicom/7/8_7.dcm',
        'wadouri:http://tune01:9000/dicom/7/9_8.dcm',
      ],
      imageIds2: [
        'wadouri:http://tune01:9000/dicom/7/1_0.dcm',
        'wadouri:http://tune01:9000/dicom/7/2_1.dcm',
        'wadouri:http://tune01:9000/dicom/7/3_2.dcm',
        'wadouri:http://tune01:9000/dicom/7/4_3.dcm',
        'wadouri:http://tune01:9000/dicom/7/5_4.dcm',
        'wadouri:http://tune01:9000/dicom/7/6_5.dcm',
        'wadouri:http://tune01:9000/dicom/7/7_6.dcm',
        'wadouri:http://tune01:9000/dicom/7/8_7.dcm',
        'wadouri:http://tune01:9000/dicom/7/9_8.dcm',
      ],
      fileList: [],
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

      //region 图像展示cavas信息
      canvasStack1: {
        currentImageIdIndex: 0,
        imageIds: []
      },
      canvasStack2: {
        currentImageIdIndex: 0,
        imageIds: []
      },
      currentCanvas: 1,
      currentWheelCanvas: 1,
      //endregion

      /**
       * 将本页面路由path信息赋给本页面变量，后面防止滚轮事件要用到
       * @type {string}
       */
      currentRoutePath: '',

      divTempWidth: 'calc(100vw - 200px)',
      divTempWidth1: 'calc(40vw - 100px)',
      divTempWidth2: 'calc(40vw - 100px)',
    }
  },
  methods: {

    saveImages() {
      let that = this
      let tempSize = that.canvasStack1.imageIds.length
      const canvas = document.getElementById('dicomImage1')
      const viewport = cornerstone.getViewport(canvas)
      debugger
      for (let i = 0; i < 1; i++) {
        cornerstone.loadAndCacheImage(that.canvasStack1.imageIds[i]).then(function (image) {
          debugger
          //toFixed,小数点后几位进位，例如123.7654 toFixed(3)是123.765
          const zoom = viewport.scale.toFixed(2)
          const cols = image.columns * zoom
          const rows = image.rows * zoom
          //创建一个canvas元素
          let myCanvas = document.createElement('canvas')
          let canvasTemp = canvas.firstElementChild
          myCanvas = that.cropCanvas(
            canvasTemp,
            Math.round(canvasTemp.width / 2 - cols / 2),
            Math.round(canvasTemp.height / 2 - rows / 2),
            cols, rows)
          //创建一个a标签
          let a = document.createElement("a")
          // let imagemy = myCanvas.toDataURL(`image/jpeg`)
          a.href = myCanvas.toDataURL(`image/jpeg`)
          // a.href = myCanvas.toDataURL(`image/${type}`)
          a.download = `test.png`
          document.body.appendChild(a) // Required for this to work in FireFox为使其在FireFox中工作，这是必要的
          a.click()
          // debugger
          // debugger
          // const temp = cornerstoneTools.SaveAs(element1, `test.png`, `image/png`)
          // const canvas = document.getElementsByClassName('dicomImage1')[this.props.activeDcmIndex]
          // cornerstone.getActiveLayer(element1)
          // const layers = cornerstone.getLayers(element1)
          // const aa = cornerstone.getDisplayedArea(image)
          // let temp = cornerstone.imageCache
          // cornerstone.getImage(element1)
          // // cornerstone.getElementData(element1,multiple)
          // const bb = cornerstone.getEnabledElementsByImageId(that.canvasStack1.imageIds[i])
          // // cornerstone.getEnabledElements()
          // debugger
          // that.fileList.push(image)
          // ctFile(image).then(function (result) {
          //   console.log(result)
          //   debugger
          // })
        })
      }
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
    //  region
    upload() {
      console.log('wenjian:', this.fileList[0])
      var reader = new FileReader()

      var file = this.fileList[0]
      //将上传的文件给cornerstoneWADOImageLoader
      const imageId = cornerstoneWADOImageLoader.wadouri.fileManager.add(file);
      const canvas2 = this.$refs.canvas
      cornerstone.loadAndCacheImage(imageId).then(function (image) {
        var viewport = cornerstone.getDefaultViewportForImage(
          canvas2,
          image
        )
        debugger
        cornerstone.displayImage(canvas2, image, viewport)
      })
      reader.readAsArrayBuffer(file)
      reader.onload = function (file) {
        var arrayBuffer = reader.result;
        debugger
        console.log("file", file)
        var byteArray = new Uint8Array(arrayBuffer)
        let dataSet = dicomParser.parseDicom(byteArray)

        let patientName = dataSet.string('x00100010')
        let patientId = dataSet.string('x00100020')
        let patientDob = dataSet.string('x00100030')
        let patientSex = dataSet.string('x00100040')

        let scanOpt = dataSet.string('x00180022')
        let encodingOpt = dataSet.string('x00080102')

        // renderData(patientName, patientId, patientDob, patientSex);

        console.log('Patient Name          = ' + patientName)
        console.log('Patient ID            = ' + patientId)
        console.log('Patient Date of Birth = ' + patientDob)
        console.log('Patient Gender        = ' + patientSex)
        console.log('Scan optionss         = ' + scanOpt)
        console.log('Encoding type         = ' + encodingOpt)
        //上传之前将信息存到数据库
        //联通OSS对象存储
        // this.fileList.map((item,index) => {
        //   // this.uploadMinIo(item,index);
        // })
        //  上传之后清空文件列表
      }
      //

    },
    deleteMinioFile(index = 0) {
      // this.fileList.splice(index,1)

    },
    getFileName() {
      let inputDOM = this.$refs.minIoFile
      console.log("minIoFile", this.$refs.minIoFile)
      inputDOM.click()
      console.log("minIoFile2")
    },
    getFile(event) {
      console.log("minIoFile3")
      console.log(document.getElementById('minIoFile').files)
      let files = document.getElementById('minIoFile').files
      let arr = []
      //
      let fileSwitch = true
      if (files.length > 0) {
        for (let i = 0; i < files.length; i++) {
          //文件大小限制
          if ((files[i].size / 1024 / 1024).toFixed(2) > 64) {
            this.$message({
              message: `${item.name}超过文件的最大长度`,
              type: 'warning'
            })
            fileSwitch = false
          }
        }
        if (fileSwitch) {
          for (let i = 0; i < files.length; i++) {
            console.log("files[i][File]", files[i][File])
            this.fileList.push(files[i])
          }
        }
      }
    },
    //上传文件到minio
    uploadMinIo(fileObj, index) {
      let vm = this
      // const files = fileObj;
      if (fileObj) {
        let file = fileObj
        //判断是否选择了文件
        if (file == undefined) {
          //未选择
          console.log('请上传文件')
        } else {
          //选择
          //获取文件类型及大小
          const fileName = file.name
          const mineType = file.type
          const fileSize = file.size

          //参数
          let metadata = {
            'content-type': mineType,
            'content-length': fileSize
          }
          //判断储存桶是否存在
          minioClient.bucketExists('testfile', function (err) {
            if (err) {
              if (err.code == 'NoSuchBucket') return console.log('bucket does not exist.')
              return console.log(err)
            }
            //存在
            console.log('Bucket exists.')
            //准备上传
            let reader = new FileReader()
            reader.readAsDataURL(file)
            reader.onloadend = function (e) {
              const dataurl = e.target.result
              //base64转blob
              const blob = vm.toBlob(dataurl)
              //blob转arrayBuffer
              let reader2 = new FileReader()
              reader2.readAsArrayBuffer(blob)

              reader2.onload = function (ex) {
                //定义流
                let bufferStream = new stream.PassThrough()
                //将buffer写入
                bufferStream.end(new Buffer(ex.target.result))
                //上传
                minioClient.putObject('testfile', fileName, bufferStream, fileSize, metadata, function (err, etag) {
                  if (err == null) {
                    minioClient.presignedGetObject('testfile', fileName, 24 * 60 * 60, function (err, presignedUrl) {
                      if (err) return console.log(err)
                      //输出url
                      console.log(presignedUrl)
                      // this.$notify({
                      //   title: '标题名称',
                      //   message: h('i', { style: 'color: teal'}, '这是提示文案这是提示文案这是提示文案这是提示文案这是提示文案这是提示文案这是提示文案这是提示文案')
                      // });
                    })
                  }
                  //return console.log(err, etag)
                })
              }
            }
          })
        }

      }
    },
    //base64转blob
    toBlob(base64Data) {
      let byteString = base64Data
      if (base64Data.split(',')[0].indexOf('base64') >= 0) {
        byteString = atob(base64Data.split(',')[1]) // base64 解码
      } else {
        byteString = unescape(base64Data.split(',')[1])
      }
      // 获取文件类型
      let mimeString = base64Data.split(';')[0].split(':')[1] // mime类型

      // ArrayBuffer 对象用来表示通用的、固定长度的原始二进制数据缓冲区
      // let arrayBuffer = new ArrayBuffer(byteString.length) // 创建缓冲数组
      // let uintArr = new Uint8Array(arrayBuffer) // 创建视图

      let uintArr = new Uint8Array(byteString.length) // 创建视图

      for (let i = 0; i < byteString.length; i++) {
        uintArr[i] = byteString.charCodeAt(i)
      }
      // 生成blob
      const blob = new Blob([uintArr], {
        type: mimeString
      })
      // 使用 Blob 创建一个指向类型化数组的URL, URL.createObjectURL是new Blob文件的方法,可以生成一个普通的url,可以直接使用,比如用在img.src上
      return blob
    },
    //  endregion


    showDicom() {
      let that = this
      console.log('showDicom')
      //获取div区域
      //初始化工具
      cornerstoneTools.init()
      const canvas = this.$refs.canvas
      const canvas2 = this.$refs.canvas2
      //初始化tools,方法包含是否开启触摸监听，鼠标监听，等
      // 在 DOM 中将 canvas 元素注册到 cornerstone
      cornerstone.enable(canvas)
      cornerstone.enable(canvas2)
      //region 测试

      //endregion


      //初始化自己的工具设置
      this.initTools()
      //展示
      this.displayCanvas2()
      this.displayCanvas1()

    },
    initTools() {
      //stack滚动工具
      let that = this
      const canvas = this.$refs.canvas
      const canvas2 = this.$refs.canvas2
      console.log("设置默认工具")
      const StackScrollMouseWheelTool = cornerstoneTools.StackScrollMouseWheelTool
      cornerstoneTools.addTool(StackScrollMouseWheelTool)
      cornerstoneTools.setToolActive('StackScrollMouseWheel', {})
    },


    /**
     * 1.加载图像，2.处理图像信息，3，显示图像，4.保存图像
     */
    displayCanvas1() {
      console.log('disp1')
      let that = this
      const canvas1 = this.$refs.canvas
      let tempIndex = that.canvasStack1.currentImageIdIndex
      //TODO file
      cornerstone.loadAndCacheImage(that.canvasStack1.imageIds[tempIndex])
        .then(function (image) {
          //设置视口
          let viewport = {}
          viewport.invert = that.getInvert
          viewport.hflip = that.getHflip
          viewport.vflip = that.getVflip
          viewport.pixelReplication = !that.getPixelReplication
          //显示
          canvas1.style.width = "100%"
          canvas1.style.height = "100%"
          cornerstone.resize(canvas1, true)
          // canvas1.style.height = "calc(100vh - 84px)"
          cornerstone.displayImage(canvas1, image, viewport)

          cornerstoneTools.addStackStateManager(canvas1, ['stack'])
          cornerstoneTools.addToolState(canvas1, 'stack', that.canvasStack1)
        })

    },
    /**
     * 1.加载图像，2.处理图像信息，3，显示图像，4.保存图像
     */
    displayCanvas2() {
      console.log('disp2')
      let that = this
      const canvas2 = this.$refs.canvas2
      let tempIndex = that.canvasStack2.currentImageIdIndex


      cornerstone.loadAndCacheImage(that.canvasStack2.imageIds[tempIndex])
        .then(function (image) {
          //设置视口
          let viewport = {}
          viewport.invert = that.getInvert
          viewport.hflip = that.getHflip
          viewport.vflip = that.getVflip
          // viewport.pixelReplication = !that.getPixelReplication
          //显示
          canvas2.style.width = "100%"
          canvas2.style.height = "100%"
          // canvas2.style.height = "calc(100vh - 84px)"
          cornerstone.resize(canvas2, true)
          cornerstone.displayImage(canvas2, image, viewport)
        })
      cornerstoneTools.addStackStateManager(canvas2, ['stack'])
      cornerstoneTools.addToolState(canvas2, 'stack', that.canvasStack2)
    },
    /**
     * 图像信息处理
     * @param image
     */
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
    },
    /**
     * 鼠标覆盖时，设置当前currentWheelCanvas参数
     * @param e
     */
    hoverOver(e) {
      console.log('hoverOver', e)
      this.currentWheelCanvas = e
    },
    /**
     * 点击，选中所选element
     * @param id
     * @param classId
     */
    select(id, classId) {
      console.log('select', id)
      this.currentCanvas = id
      // 处理css样式，有待完成
    },
    /**
     * 滚动处理
     * @param e
     */
    handleScroll(e) {
      // 滚动，展示当前选中的视图的下一张图像。
      this.displayWheelCanvas()
    },
    /**
     * 鼠标滚动时，根据鼠标所在图像位置，滚动图像
     */
    displayWheelCanvas() {
      //滚轮滚动时，只有在当前页面才可以触发，
      // if (this.$route.path != this.currentRoutePath) {
      //   return
      // } else {
      if (this.currentWheelCanvas == 1) {
        this.displayCanvas1()
      } else if (this.currentWheelCanvas == 2) {
        this.displayCanvas2()
      }
      // }
    },
    /**
     * 鼠标点击时，
     */
    displayCanvas() {
      if (this.currentCanvas == 1) {
        this.displayCanvas1()
      } else if (this.currentCanvas == 2) {
        this.displayCanvas2()
      }
    },
    //region 备用
    // /*
    //    * Window Resize
    //    *
    //    */
    // listenForWindowResize() {
    //   this.$nextTick(function () {
    //     window.addEventListener(
    //       "resize",
    //       this.debounce(this.onWindowResize, 100)
    //     );
    //   });
    // },
    // onWindowResize() {
    //   let canvas1 = this.$refs.canvas
    //   let canvas2 = this.$refs.canvas2
    //   canvas1.style.width = "100%"
    //   canvas1.style.height = "100%"
    //   canvas2.style.width = "100%"
    //   canvas2.style.height = "100%"
    //   cornerstone.resize(canvas1);
    //   cornerstone.resize(canvas2);
    // },
    //
// endregion

    changeWidth() {
      console.log(this.isOpen, this.openStudySeries)
      if (this.isOpen === true && this.openStudySeries === true) {
        this.divTempWidth = 'calc(100vw - 200px)'
        this.divTempWidth1 = 'calc(40vw - 100px)'
        this.divTempWidth2 = 'calc(40vw - 100px)'
      } else if (this.isOpen === false && this.openStudySeries === true) {
        this.divTempWidth = 'calc(100vw - 54px)'
        this.divTempWidth1 = 'calc(40vw - 27px)'
        this.divTempWidth2 = 'calc(40vw - 27px)'
      } else if (this.isOpen === false && this.openStudySeries === false) {
        this.divTempWidth = 'calc(100vw - 54px)'
        this.divTempWidth1 = 'calc(50vw - 27px)'
        this.divTempWidth2 = 'calc(50vw - 27px)'
      } else {
        //true flase
        this.divTempWidth = 'calc(100vw - 200px)'
        this.divTempWidth1 = 'calc(50vw - 100px)'
        this.divTempWidth2 = 'calc(50vw - 100px)'
      }
      this.displayCanvas1()
      this.displayCanvas2()
    },
  },
  mounted() {
    const that = this
    this.canvasStack1.imageIds = this.imageIds1
    this.canvasStack2.imageIds = this.imageIds2
    //
    let element1 = this.$refs.canvas
    let element2 = this.$refs.canvas2
    this.currentRoutePath = this.$route.path
    //加载初始化
    that.showDicom()
    //监听滚动事件:mounted是vue已经渲染好了最终模板，
    // 也就是可以拿到页面的元素了，或者监听页面2021年12月28日22:23:52
    element1.addEventListener(cornerstoneTools.EVENTS.MOUSE_WHEEL, this.handleScroll, false)
    element2.addEventListener(cornerstoneTools.EVENTS.MOUSE_WHEEL, this.handleScroll, false)
    // let marking = cornerstoneTools.getToolState(element1, 'FreehandRoi')
    // let temp = cornerstone.getElementToolStateManager()
    console.log("sd")
    //region 备用
    // window.addEventListener('resize', this.listenForWindowResize);
    // 像素反转，水平反转，垂直反转，使用cornerstoneTools.EVENTS.MEASUREMENT_COMPLETED方法来监听
    // this.element1.addEventListener(cornerstoneTools.EVENTS.MEASUREMENT_ADDED, function (params) {
    //   const eventData = params.detail;
    //   console.log("ADDED", eventData)
    // });
    // this.element2.addEventListener(cornerstoneTools.EVENTS.MEASUREMENT_ADDED, function (params) {
    //   const eventData = params.detail;
    //   console.log("ADDED", eventData)
    // });
    // // 用户用操作用具标注图像完成之后，触发这个监听事件MEASUREMENT_COMPLETED。用来保存图像png/jpeg
    // this.element1.addEventListener(cornerstoneTools.EVENTS.MEASUREMENT_COMPLETED, function (params) {
    //   const eventData = params.detail;
    //   console.log("COMPLETED", eventData)
    // });
    // this.element2.addEventListener(cornerstoneTools.EVENTS.MEASUREMENT_COMPLETED, function (params) {
    //   const eventData = params.detail;
    //   console.log("COMPLETED", eventData)
    // });
    // // 使用橡皮擦修改图像后，重新保存图像
    // this.element1.addEventListener(cornerstoneTools.EVENTS.MEASUREMENT_REMOVED, function (params) {
    //   const eventData = params.detail;
    //   console.log("REMOVED", eventData)
    // });
    // this.element2.addEventListener(cornerstoneTools.EVENTS.MEASUREMENT_REMOVED, function (params) {
    //   const eventData = params.detail;
    //   console.log("REMOVED", eventData)
    // });
    // Dicom 加载 进度
//     cornerstone.events.addEventListener(
//       "cornerstoneimageloadprogress",
//       function(event) {
//         const eventData = event.detail;
//         const loadProgress = document.getElementById("loadProgress");
//         loadProgress.textContent = `Dicom加载: ${eventData.percentComplete}%`;
//       }
//     );

    //endregion
  },
  created() {

  },
  beforeUpdate() {
    //对需要修改的数据进行处理，此时数据还没有在页面更新，就是在页面更新之前的操作
  },
  updated() {
    //只要有数据更新就会执行。
    // this.displayCanvas()
  },

  computed: {
    //region viewport监视设置
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
    //endregion

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

    //  endregion
    //region 窗口变化监视
    openStudySeries() {
      return this.$store.getters.openStudy
    },
    isOpen() {
      return this.$store.getters.sidebar.opened
    },
    //  endregion
  },
  watch: {
    //region viewpost 监视设置 逻辑操作
    getInvert: function (value) {
      this.displayCanvas()
    },
    getHflip: function () {
      this.displayCanvas()
    },
    getVflip: function () {
      this.displayCanvas()
    },
    getPixelReplication: function () {
      this.displayCanvas()
    },
    //  endregion
    //region 窗口变化监视
    openStudySeries: function () {
      this.changeWidth()
    },
    isOpen: function () {
      this.changeWidth()
    },
    //  endregion
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

  height: calc(100vh - 84px);
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
      border-color: #507cef !important;

      ::v-deep .el-collapse-item__header {
        background-color: #282c34 !important;
        color: white !important;
        border-bottom-color: #ea768b;
      }

      ::v-deep .el-collapse-item__wrap {
        background-color: #17191c !important;
        color: white !important;

        //border-color: white !important;
        border-bottom-color: #eada76 !important;

      }

      .left-label {
        .left-label-item {
          background-color: #17191c !important;
          color: white !important;
        }
      }

      .left-study {
        .left-study-collapse {
          background-color: #282c34 !important;
          color: white !important;

          .left-study-collapse-item {
            .ct-image1 {
              width: 100%;
              height: 280px;
              display: block;
              background-color: #282c34 !important;
            }
          }
        }
      }
    }


  }

  .ct-father-Open1 {

    height: 100%;
    position: relative;
    color: white;
    border-color: red;
    border-width: 5px;

    .ct-image {
      width: 100%;
      height: 100%;
      background-color: #000000;
      border-color: red;
      border-width: 5px;
    }
  }

  .ct-father-Open2 {
    height: 100%;
    position: relative;
    color: white;
    border-color: red;
    border-width: 5px;

    .ct-image {
      width: 100%;
      height: 100%;
      background-color: #000000;
      border-color: red;
      border-width: 5px;
    }
  }

}


</style>

