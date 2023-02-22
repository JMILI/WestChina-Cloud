<template>
  <div>
<!--    <el-button type="primary" @click="getAuth">请求token</el-button>-->
<!--    <el-button type="primary" @click="getContainers">获取容器列表</el-button>-->

    <uploader
      :options="options"
      :file-status-text="statusText"
      :auto-start="false"
      class="uploader-example"
      ref="uploader"
      @file-added="onFileAdded"
      @file-success="onFileSuccess"
      @file-error="onFileError"
      @file-removed="fileRemoved"
    >
      <uploader-unsupport></uploader-unsupport>
      <uploader-drop>
        <uploader-btn :attrs="attrs" style="background-color: #67C13B">
          <i class="el-icon-upload"
             style="margin-right: 5px"></i>上传文件
        </uploader-btn>
        <uploader-btn :directory="true" style="background-color: #79BBFF">
          <i class="el-icon-folder-add" style="margin-right: 5px"></i>上传文件夹
        </uploader-btn>
        <el-button type="danger" plain @click="errorDialog=true" v-show="controllerErrorFileDialog">错误信息</el-button>
        <el-button @click="cancelUpload">取消上传</el-button>
        <el-button type="primary" @click="submitUpload">开始上传</el-button>
      </uploader-drop>
      <uploader-list></uploader-list>

    </uploader>
<!--    <div slot="footer" class="dialog-footer">-->
<!--      <span class="filetotal">共计: {{ this.file_total }}</span>-->
<!--      <el-button type="danger" plain @click="errorDialog=true" v-show="controllerErrorFileDialog">错误信息</el-button>-->
<!--      <el-button @click="cancelUpload">取消上传</el-button>-->
<!--      <el-button type="primary" @click="submitUpload">开始上传</el-button>-->
<!--    </div>-->

  </div>
</template>

<script>


const axios = require('axios');


// import {getAuth} from "../../api/ct/ct";

export default {
  name: "swiftUpload",
  mounted() {

  },
  data() {
    return {
      token: '',
      options: {
        target: '//westChinaUI:3000/upload',
        maxChunkRetries: 2,
        testChunks: false,
        fileParameterName: 'contents',
        chunkSize: 1024 * 1024 * 1024,
        simultaneousUploads: 3,
        query: {
          type: '',
          create_time: ''
        },
        headers: {
          'Authorization':'',
        },
      },
      statusText: {
        success: '上传成功',
        error: '上传失败',
        uploading: '上传中',
        paused: '暂停中',
        waiting: '等待中'
      },
      attrs: {
        accept: [],
      },
      file_total: 0, //本次文件上传的总数
      errorfilelist: [], //上传失败信息列表
      controllerErrorFileDialog:false,
    }
  },
  methods: {
    //refion swift文件服务器，使用axios上传
    getAuth() {
      let _this = this
      const config = {
        method: 'get',
        url: '/api-ct/auth/v1.0',
        headers: {
          'X-Storage-User': 'test:tester',
          'X-Storage-Pass': 'testing',
          'Access-Control-Allow-Origin': '*',
        }
      };
      axios(config)
        .then(function (response) {
          console.log(response);
          //因为有-的缘故，使用方括号和’来获取属性的值
          _this.token = response.headers['x-auth-token']
          // this.token=token
          console.log("token:", _this.token)
          //获取token
          const config = {
            method: 'get',
            url: '/api-ct/v1/TMP_test',
            headers: {
              'X-Auth-Token': _this.token,
              'Access-Control-Allow-Origin': '*',
            }
          }
          //  然后请求
          axios(config)
            .then(function (res) {
              console.log(res.data)
              const config = {
                method: 'get',
                url: '/api-ct/v1/TMP_test/' + 'hellow',
                headers: {
                  'X-Auth-Token': _this.token,
                  'Access-Control-Allow-Origin': '*',
                }
              }
              axios(config)
                .then(function (res) {
                  console.log(res)
                })
            })
        })
        .catch(function (error) {
          console.log("error");
          console.log(error);
        });
    },
    getContainers() {
      let _this = this
      let token = _this.token
      const config = {
        method: 'get',
        url: '/api-ct/v1/TMP_test',
        headers: {
          'X-Auth-Token': _this.token,
          'Access-Control-Allow-Origin': '*',
        }
      }
      console.log(config)
      axios(config)
        .then(function (res) {
          console.log(res)
        })
        .catch(function (error) {
          console.log("error");
          console.log(error);
        });
    },
    //endregion

    //region  vue-simple-upload上传
//添加文件到列表还未上传,每添加一个文件，就会调用一次,在这里过滤并收集文件夹中文件格式不正确信息，同时把所有文件的状态设为暂停中
    onFileAdded(file) {
      console.log("onFileAdded")
      let file_type = file.name.substring(file.name.lastIndexOf(".") + 1);
      const extension = file_type === this.uploadType;
      if (!extension) {
        let obj = {
          rootname: '无',
          name: file.name,
          errorinfo: "文件不是 " + this.uploadType + " 格式",
        };
        let arr = file.relativePath.split("/");
        if (arr.length > 1) {
          obj['rootname'] = arr[0]
        }
        this.errorfilelist.push(obj);
        file.ignored = true
      } else {
        file.pause();
      }
      this.$nextTick(() => {
        this.file_total = this.$refs['uploader'].files.length
      });
      if (this.errorfilelist.length !== 0) {
        this.controllerErrorFileDialog = true
      }
    },

//每个文件传输给后端之后，返回的信息
    onFileSuccess(rootFile, file, response, chunk) {
      console.log("onFileSuccess")
      let res = JSON.parse(response)
      if (res.code !== 10000) {
        let obj = {
          rootname: '无',
          name: file.name,
          errorinfo: res.message,
        };
        if (rootFile.isFolder === true) {
          obj['rootname'] = rootFile.name
        }
        this.errorfilelist.push(obj);
        this.controllerErrorFileDialog = true
      }
    },
    // 上传错误触发，文件还未传输到后端
    onFileError(rootFile, file, response, chunk) {
      console.log("onFileError")
      let obj = {
        rootname: '无',
        name: file.name,
        errorinfo: "文件上传失败",
      };
      if (rootFile.isFolder === true) {
        obj['rootname'] = rootFile.name
      }
      this.errorfilelist.push(obj);
      this.controllerErrorFileDialog = true
    },
    // 移除文件
    fileRemoved(file) {
      this.$nextTick(() => {
        this.file_total = this.$refs['uploader'].files.length
      });
    },
//点击开始上传按钮
    submitUpload() {
      this.$nextTick(() => {
        for (var i = 0; i < this.$refs['uploader'].files.length; i++) {
          this.$refs['uploader'].files[i].resume()
        }
      });
    },
    //关闭错误文件提示框口，知道上传对话框被关闭时才会被清空
    closeErrorDialog() {
      this.errorDialog = false;
    },
    // 上传弹框关闭
    handelClose() {
      this.clearcache()
      this.thirdDialog = false
    },
    // 清除缓存
    clearcache() {
      this.file_total = 0;
      this.errorfilelist = []
      this.controllerErrorFileDialog = false
      this.$refs.uploader.uploader.cancel()
      // this.getresourceDetail();
    },
    //取消上传
    cancelUpload() {
      this.thirdDialog = false;
      this.clearcache();
    },
    //endregion

  },

}
</script>

<style scoped>
.uploader-example {
  width: 90%;
  padding: 15px;
  margin: 0 auto 0;
  font-size: 14px;
  box-shadow: 0 0 10px rgba(0, 0, 0, .4);
}

.uploader-example .uploader-btn {
  margin-right: 8px;
  color: #ffffff;
  border: #ffffff;
}

.uploader-example .uploader-list {
  max-height: 300px;
  overflow: auto;
  overflow-x: hidden;
  overflow-y: auto;

}

/*.uploader-file[status="uploading"]> .uploader-file-info{*/
/*> .uploader-file-status > span> i{*/
/*  visibility:hidden;*/
/*}*/
/*> .uploader-file-status > span> em{*/
/*  visibility:hidden;*/
/*}*/
/*}*/
</style>
