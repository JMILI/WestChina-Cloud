<template>
  <div>

    <div class="minioBox">
      <el-button style="marginRight:10px;" @click="getFileName" size="mini" type="success">选择文件</el-button>
      <input accept="*/*" type="file" multiple="multiple" id="minIoFile" ref="minIoFile" v-show="false"
             @change="getFile"
      >
      <el-button v-if="fileList.length>0" style="marginRight:10px;" @click="uploadMinIo" size="mini" type="success">上传
      </el-button>
    </div>
    <ul class="uploadFileList">
      <li v-for="item of fileList" :key="item.index">
        <span class="subString">{{ item.name }}</span>&nbsp;
        <span>({{ (item.size / 1024 / 1024).toFixed(2) }}M)</span>
        <div class="floatRight" style="float: right;">
          <i class="el-icon-close" style="cursor: pointer;" @click="deleteMinioFile(index)"></i>
        </div>
      </li>
    </ul>


    <div ref="canvas" style="width: 512px;height: 512px;margin-left: 400px;background-color: #00afff"></div>


  </div>

</template>
<!--<script src="https://unpkg.com/cornerstone-wado-image-loader@3.1.2/dist/cornerstoneWADOImageLoader.min.js"></script>-->
<!--<script src="../"></script>-->
<script>
//region 包引入
//引入 cornerstone,dicomParser,cornerstoneWADOImageLoader
import * as cornerstone from 'cornerstone-core'
import * as dicomParser from 'dicom-parser'

// 不建议 npm 安装 cornerstoneWADOImageLoader 如果你做了 会很头疼
// import * as cornerstoneWADOImageLoader from "../../../static/cornerstoneWADOImageLoader.js";
import * as cornerstoneWebImageLoader from 'cornerstone-web-image-loader'
import * as cornerstoneWADOImageLoader from 'cornerstone-wado-image-loader'
import cornerstoneFileImageLoader from "cornerstone-file-image-loader/src";
// Cornerstone 工具外部依赖
import Hammer from 'hammerjs'
import * as cornerstoneMath from 'cornerstone-math'
import * as cornerstoneTools from '@cornerstoneTools'

// import {getModule} from "cornerstone-tools"
const BaseTool = cornerstoneTools.importInternal('base/BaseTool')
const cornerstoneStore = cornerstoneTools.importInternal('store')
// Specify external dependencies 指定外部依赖，什么意思？为什么指定
cornerstoneTools.external.cornerstone = cornerstone
cornerstoneTools.external.cornerstoneMath = cornerstoneMath
cornerstoneTools.external.Hammer = Hammer
//指定要注册加载程序的基石实例
cornerstoneWADOImageLoader.external.cornerstone = cornerstone
cornerstoneWADOImageLoader.external.dicomParser = dicomParser
cornerstoneWADOImageLoader.external.cornerstoneMath = cornerstoneMath
cornerstoneWebImageLoader.external.cornerstone = cornerstone
cornerstoneFileImageLoader.external.cornerstone = cornerstone
let Minio = require('minio')
let stream = require('stream')
var fs = require('fs');
cornerstoneTools.enableLogger('StackScrollMouseWheelTool');
//方法包含是否开启触摸监听，鼠标监听，
// cornerstoneTools.init();
//endregion
export default {
  name: 'ct',
  data() {
    return {
      imageIds: [
        'wadouri:http://westChinaBackend:8000/read1',
        'wadouri:http://westChinaBackend:8000/read2',
        'wadouri:http://westChinaBackend:8000/read3',
        'wadouri:http://westChinaBackend:8000/read4',
        'wadouri:http://westChinaBackend:8000/read5',
        'wadouri:http://westChinaBackend:8000/read6',
        'wadouri:http://westChinaBackend:8000/read7',
        'wadouri:http://westChinaBackend:8000/read8',
        'wadouri:http://westChinaBackend:8000/read9'],
      fileList: [],

    }
  },
  methods: {

    show() {
      console.log('show')
      //获取div区域
      //初始化工具
      cornerstoneTools.init()
      const canvas = this.$refs.canvas
      //初始化tools,方法包含是否开启触摸监听，鼠标监听，等
      // 在 DOM 中将 canvas 元素注册到 cornerstone
      cornerstone.enable(canvas)

      //初始化自己的工具设置
      this.initTools()
      //准备数据
      let canvasStack = {
        currentImageIdIndex: 0,
        imageIds: this.imageIds
      }
      //展示
      const o = this.displayOneCanvasImage(canvas, canvasStack)

    },
    initTools(canvas) {
      // //定义stack滚动工具
      const StackScrollMouseWheelTool = cornerstoneTools.StackScrollMouseWheelTool
      cornerstoneTools.addTool(StackScrollMouseWheelTool)
      cornerstoneTools.setToolActive('StackScrollMouseWheel', {})
      this.Tools()
    },
    displayOneCanvasImage(canvas, canvasStack) {
      console.log('第一张', this.imageIds[0])
      console.log('所有', this.imageIds)
      //下面的出错
      return cornerstone.loadAndCacheImage(this.imageIds[0]).then(function (image) {
        //打印，看数据
        console.log('----------------image-----------------')
        console.log(image)
        //显示图像
        console.log('----------------mounted3-----------------')
        var viewport = cornerstone.getDefaultViewportForImage(
          canvas,
          image
        )

        // let reader = new FileReader();
        // console.log("----------------mounted4-----------------");
        // reader.onloadend = function(image) {
        //   // Here we have the file data as an ArrayBuffer.  dicomParser requires as input a
        //   // Uint8Array so we create that here
        console.log('image.data.byteArray', image.data.byteArray)
        //   var byteArray = new Uint8Array(arrayBuffer);
        //   byteArray=image.data.byteArray
        //   // parseByteArray(byteArray);
        //   var dataSet = dicomParser.parseDicom(byteArray);
        //
        //   // access a string element
        //   var studyInstanceUid = dataSet.string('x0020000d');
        //   console.log("studyInstanceUid",studyInstanceUid)
        //   // get the pixel data element (contains the offset and length of the data)
        //   var pixelDataElement = dataSet.elements.x7fe00010;
        //   console.log("----------------mounted5-----------------");
        //   // create a typed array on the pixel data (this example assumes 16 bit unsigned data)
        //   var pixelData = new Uint16Array(dataSet.byteArray.buffer, pixelDataElement.dataOffset, pixelDataElement.length);
        // }
        cornerstone.displayImage(canvas, image, viewport)
        cornerstoneTools.addStackStateManager(canvas, ['stack'])
        cornerstoneTools.addToolState(canvas, 'stack', canvasStack)
        console.log('----------------mounted6-----------------')
        // reader.readAsArrayBuffer(file);
        var byteArray = image.data.byteArray
        var dataSet = dicomParser.parseDicom(byteArray)
        console.log('dataSet', dataSet)
        var sopInstanceUid = dataSet.string('x0020000d')
        console.log('sopInstanceUid', sopInstanceUid)
        // let patientName = formatName(dataSet.string("x00100010"));
        let patientId = dataSet.string('x00100020')
        let patientDob = dataSet.string('x00100030')
        let patientSex = dataSet.string('x00100040')

        let scanOpt = dataSet.string('x00180022')
        let encodingOpt = dataSet.string('x00080102')

        // renderData(patientName, patientId, patientDob, patientSex);

        // console.log("Patient Name          = " + patientName);
        console.log('Patient ID            = ' + patientId)
        console.log('Patient Date of Birth = ' + patientDob)
        console.log('Patient Gender        = ' + patientSex)
        console.log('Scan optionss         = ' + scanOpt)
        console.log('Encoding type         = ' + encodingOpt)

      })
    },
    dicomParserOne(dicom) {
      const formatName = (string) => {
        let name = string.split('^')
        return `${name[0]}_${name[1]}`
      }
      let arrayBuffer = dicom
      let byteArray = new Uint8Array(arrayBuffer)

      let dataSet = dicomParser.parseDicom(byteArray)

      let patientName = formatName(dataSet.string('x00100010'))
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
    },
    Tools() {
      // //角度工具
      // const AngleTool = cornerstoneTools.AngleTool;
      // cornerstoneTools.addTool(AngleTool);
      // cornerstoneTools.setToolActive('Angle', {mouseButtonMask: 2})
      // //长度工具
      // const LengthTool = cornerstoneTools.LengthTool;
      // cornerstoneTools.addTool(LengthTool);
      // cornerstoneTools.setToolActive('Length', {mouseButtonMask: 1})
      // //探针
      const DragProbeTool = cornerstoneTools.DragProbeTool
      cornerstoneTools.addTool(DragProbeTool)
      cornerstoneTools.setToolActive('DragProbe', {mouseButtonMask: 1})
      //探针注解
      // const ProbeTool = cornerstoneTools.ProbeTool;
      // cornerstoneTools.addTool(ProbeTool)
      // cornerstoneTools.setToolActive('Probe', { mouseButtonMask: 1 })
      // 放大镜 TODO 需要修改放大镜的位置
      // const MagnifyTool = cornerstoneTools.MagnifyTool;
      // cornerstoneTools.addTool(MagnifyTool)
      // cornerstoneTools.setToolActive('Magnify', { mouseButtonMask: 1 })
      //箭头 TODO 有问题，
      // const OrientationMarkersTool = cornerstoneTools.OrientationMarkersTool;
      // cornerstoneTools.addTool(OrientationMarkersTool)
      // cornerstoneTools.setToolActive('OrientationMarkers', { mouseButtonMask: 1 })
      // 图像移动 TODO 需要设置合适的视窗大小
      // const PanTool = cornerstoneTools.PanTool;
      // cornerstoneTools.addTool(PanTool)
      // cornerstoneTools.setToolActive('Pan', { mouseButtonMask: 1 })
      //旋转图像 越往外围，转动幅度越小
      // const RotateTool = cornerstoneTools.RotateTool;
      // cornerstoneTools.addTool(RotateTool)
      // cornerstoneTools.setToolActive('Rotate', { mouseButtonMask: 2 })
      //刻度工具 最好不要加 让器可以默认开启
      // const ScaleOverlayTool = cornerstoneTools.ScaleOverlayTool;
      // cornerstoneTools.addTool(ScaleOverlayTool)
      // cornerstoneTools.setToolActive('ScaleOverlay', {})
      //区域亮度 选中区域颜色的相反颜色
      // const WwwcRegionTool = cornerstoneTools.WwwcRegionTool;
      // cornerstoneTools.addTool(WwwcRegionTool)
      // cornerstoneTools.setToolActive('WwwcRegion', { mouseButtonMask: 1 })
      //亮度工具
      // const WwwcTool = cornerstoneTools.WwwcTool;
      // cornerstoneTools.addTool(WwwcTool)
      // cornerstoneTools.setToolActive('Wwwc', { mouseButtonMask: 1 })
      // 局部放大，不是放大镜
      // const ZoomTool = cornerstoneTools.ZoomTool;
      // cornerstoneTools.addTool(cornerstoneTools.ZoomTool, {
      //   // Optional configuration
      //   configuration: {
      //     invert: false,
      //     preventZoomOutsideImage: false,
      //     minScale: .1,
      //     maxScale: 20.0,
      //   }
      // });
      // cornerstoneTools.setToolActive('Zoom', { mouseButtonMask: 2 })
      //箭头注解功能
      // const ArrowAnnotateTool = cornerstoneTools.ArrowAnnotateTool;
      // cornerstoneTools.addTool(ArrowAnnotateTool)
      // cornerstoneTools.setToolActive('ArrowAnnotate', { mouseButtonMask: 1 })
      // //椭圆 TODO 如何获取面积
      // const EllipticalRoiTool = cornerstoneTools.EllipticalRoiTool;
      // cornerstoneTools.addTool(EllipticalRoiTool)
      // cornerstoneTools.setToolActive('EllipticalRoi', { mouseButtonMask: 1 })
      // //自由圈定区域
      // const FreehandRoiTool = cornerstoneTools.FreehandRoiTool;
      // cornerstoneTools.addTool(FreehandRoiTool)
      // cornerstoneTools.setToolActive('FreehandRoi', { mouseButtonMask: 1 })
      //矩阵注解
      // const RectangleRoiTool = cornerstoneTools.RectangleRoiTool;
      // cornerstoneTools.addTool(RectangleRoiTool)
      // cornerstoneTools.setToolActive('RectangleRoi', { mouseButtonMask: 1 })
      // 文字注解 TODO 需要窗口输入注释
      // const TextMarkerTool = cornerstoneTools.TextMarkerTool
      // const configuration = {
      //   markers: ['F5', 'F4', 'F3', 'F2', 'F1'],
      //   current: 'F5',
      //   ascending: true,
      //   loop: true,
      // }
      // cornerstoneTools.addTool(TextMarkerTool, { configuration })
      // cornerstoneTools.setToolActive('TextMarker', { mouseButtonMask: 1 })
      // TODO 自由画画 灵活一点
      // const toolName = 'Brush';
      // const apiTool = cornerstoneTools[`${toolName}Tool`];
      // cornerstoneTools.addTool(apiTool);
      // cornerstoneTools.setToolActive(toolName, { mouseButtonMask: 1 });
      //圆形选中剪裁 有四种策略
      // const CircleScissorsTool = cornerstoneTools.CircleScissorsTool;
      // cornerstoneTools.addTool(CircleScissorsTool)
      // cornerstoneTools.setToolActive('CircleScissors', { mouseButtonMask: 1 })
      //自由选中剪裁 有四种策略 有四种策略
      // const FreehandScissorsTool = cornerstoneTools.FreehandScissorsTool;
      // cornerstoneTools.addTool(FreehandScissorsTool)
      // cornerstoneTools.setToolActive('FreehandScissors', { mouseButtonMask: 1 })
      // //矩阵选中剪裁
      // const RectangleScissorsTool = cornerstoneTools.RectangleScissorsTool;
      // cornerstoneTools.addTool(RectangleScissorsTool)
      // cornerstoneTools.setToolActive('RectangleScissors', { mouseButtonMask: 1 })
    },
    //  region
    upload() {
      var file = this.fileList[0]
      const canvas2 = this.$refs.canvas
      const imageId = cornerstoneFileImageLoader.fileManager.add(file);
      cornerstone.loadImage(imageId).then(function (image) {
        debugger
        cornerstone.displayImage(canvas2, image);
      })
      // const imageId = cornerstoneFileImageLoader.fileManager.addBuffer(file);
      // cornerstone.loadImage(imageId).then(function(image) {
      //   cornerstone.displayImage(element, image);
      // })
    },
    // upload() {
    //   console.log('wenjian:', this.fileList[0])
    //   var reader = new FileReader()
    //
    //   var file = this.fileList[0]
    //   //将上传的文件给cornerstoneWADOImageLoader
    //   const imageId = cornerstoneWADOImageLoader.wadouri.fileManager.add(file);
    //   const canvas2 = this.$refs.canvas
    //   cornerstone.loadAndCacheImage(imageId).then(function(image) {
    //     var viewport = cornerstone.getDefaultViewportForImage(
    //       canvas2,
    //       image
    //     )
    //     cornerstone.displayImage(canvas2, image, viewport)
    //   })
    //   reader.readAsArrayBuffer(file)
    //   reader.onload = function(file) {
    //     var arrayBuffer = reader.result;
    //     debugger
    //     console.log("file",file)
    //     var byteArray = new Uint8Array(arrayBuffer)
    //     let dataSet = dicomParser.parseDicom(byteArray)
    //
    //     let patientName = dataSet.string('x00100010')
    //     let patientId = dataSet.string('x00100020')
    //     let patientDob = dataSet.string('x00100030')
    //     let patientSex = dataSet.string('x00100040')
    //
    //     let scanOpt = dataSet.string('x00180022')
    //     let encodingOpt = dataSet.string('x00080102')
    //
    //     // renderData(patientName, patientId, patientDob, patientSex);
    //
    //     console.log('Patient Name          = ' + patientName)
    //     console.log('Patient ID            = ' + patientId)
    //     console.log('Patient Date of Birth = ' + patientDob)
    //     console.log('Patient Gender        = ' + patientSex)
    //     console.log('Scan optionss         = ' + scanOpt)
    //     console.log('Encoding type         = ' + encodingOpt)
    //     //上传之前将信息存到数据库
    //     //联通OSS对象存储
    //     // this.fileList.map((item,index) => {
    //     //   // this.uploadMinIo(item,index);
    //     // })
    //     //  上传之后清空文件列表
    //   }
    //   //
    //
    // },
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
    uploadMinIo() {
      let vm = this
      // const files = fileObj;

      var file = this.fileList[0]
      const canvas2 = this.$refs.canvas
      const imageId = cornerstoneFileImageLoader.fileManager.add(file);
      cornerstone.loadImage(imageId).then(function (image) {
        debugger
        cornerstone.displayImage(canvas2, image);
      })
      // let fileObj=this.fileList[0]

      // if (fileObj) {
      //   let file = fileObj
      //   //判断是否选择了文件
      //   if (file == undefined) {
      //     //未选择
      //     console.log('请上传文件')
      //   } else {
      //选择

      const minioClient = new Minio.Client({
        endPoint: 'westChinaBackend', // 地址
        port: 9000, // 端口号，若地址为类似test.minio.com,就不必写端口号
        useSSL: false, // 是否使用ssl
        accessKey: 'admin', // 登录的accessKey
        secretKey: 'admin123456' // secretKey
      });
      // const minioClient=
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
      minioClient.bucketExists('jmtest', function (err) {
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
            minioClient.putObject('jmtest', fileName, bufferStream, fileSize, metadata, function (err, etag) {
              if (err == null) {
                minioClient.presignedGetObject('jmtest', fileName, 24 * 60 * 60, function (err, presignedUrl) {
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
      // }

      // }
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
    }
    //  endregion

  },
  mounted() {
    var _this = this
    //加载初始化
    this.show()

  },
  watch: {},
  components: {},
}

</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<!--<style scoped>-->
<style lang="scss" scoped>
.minioBox {
  color: #000000;
  padding: 10px;
  width: 90%;

  .uploadFileList {
    width: 100%;

    li {
      height: 22px;
      line-height: 22px;
      margin: 10px 0px;

      span {
        margin-right: 10px;
        vertical-align: top;
      }

      .subString {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        width: 53%;
        display: inline-block;
      }

      i {
        margin: 5px 5px 0 0;
      }

      .el-icon-close,
      .el-icon-upload-success {
        float: right;
      }

      .upload-success {
        color: green;
      }

      .upload-fail {
        color: red;
      }
    }

    li:hover {
      background-color: #f5f7fa;
    }

    li:first-child {
      margin-top: 10px;
    }

    .progress {
      margin-top: 2px;
      width: 200px;
      height: 14px;
      margin-bottom: 10px;
      overflow: hidden;
      background-color: #f5f5f5;
      border-radius: 4px;
      -webkit-box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.1);
      box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.1);
      display: inline-block;

      .progress-bar {
        background-color: rgb(92, 184, 92);
        background-image: linear-gradient(
            45deg,
            rgba(255, 255, 255, 0.14902) 25%,
            transparent 25%,
            transparent 50%,
            rgba(255, 255, 255, 0.14902) 50%,
            rgba(255, 255, 255, 0.14902) 75%,
            transparent 75%,
            transparent
        );
        background-size: 40px 40px;
        box-shadow: rgba(0, 0, 0, 0.14902) 0px -1px 0px 0px inset;
        box-sizing: border-box;
        color: rgb(255, 255, 255);
        display: block;
        float: left;
        font-size: 12px;
        height: 20px;
        line-height: 20px;
        text-align: center;
        transition-delay: 0s;
        transition-duration: 0.6s;
        transition-property: width;
        transition-timing-function: ease;
        width: 266.188px;
      }
    }
  }
}
</style>

