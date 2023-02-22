<template>
  <div class="app-container">
    <div class="wrapper-container" v-show="showSearch">
      <el-form :model="queryParams" ref="queryForm" :inline="true" label-width="68px">
        <el-form-item label="身份证号" prop="patCardId">
          <el-input
            v-model="queryParams.patCardId"
            placeholder="请输入身份证号"
            clearable
            size="small"
            @keyup.enter.native="handleQuery"/>
        </el-form-item>
        <el-form-item label="病人姓名" prop="patName">
          <el-input
            v-model="queryParams.patName"
            placeholder="请输入病人姓名"
            clearable
            size="small"
            @keyup.enter.native="handleQuery"/>
        </el-form-item>
        <el-form-item label="手机号" prop="patPhone">
          <el-input
            v-model="queryParams.patPhone"
            placeholder="请输入病人手机号码"
            clearable
            size="small"
            @keyup.enter.native="handleQuery"/>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="el-icon-search" size="mini" @click="handleQuery">搜索</el-button>
          <el-button icon="el-icon-refresh" size="mini" @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>
    </div>
    <div class="wrapper-container">
      <el-row :gutter="10" class="mb8">
        <el-col :span="1.5">
          <el-button
            type="primary"
            plain
            icon="el-icon-plus"
            size="mini"
            @click="handleAdd"
            v-hasPermi="['ct:patient:add']"
          >新增
          </el-button>
        </el-col>
        <el-col :span="1.5">
          <el-button
            type="success"
            plain
            icon="el-icon-edit"
            size="mini"
            :disabled="single"
            @click="handleUpdate"
            v-hasPermi="['ct:patient:edit']"
          >修改
          </el-button>
        </el-col>
        <el-col :span="1.5">
          <el-button
            type="danger"
            plain
            icon="el-icon-delete"
            size="mini"
            :disabled="multiple"
            @click="handleDelete"
            v-hasPermi="['ct:patient:remove']"
          >删除
          </el-button>
        </el-col>
        <el-col :span="1.5">
          <el-button
            type="warning"
            plain
            icon="el-icon-download"
            size="mini"
            @click="handleExport"
            v-hasPermi="['ct:patient:export']"
          >导出
          </el-button>
        </el-col>


        <right-toolbar :showSearch.sync="showSearch" @queryTable="getList" :columns="columns"/>
      </el-row>

      <el-table v-loading="loading" :data="patientList" @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55" align="center"/>
        <el-table-column label="序号" align="center" min-width="70" class-name="allowDrag" v-if="columns[0].visible">
          <template slot-scope="scope">
            <span>{{ queryParams.pageSize * (queryParams.pageNum - 1) + scope.$index + 1 }}</span>
          </template>
        </el-table-column>
        <el-table-column label="身份证号" align="center" key="patCardId" prop="patCardId" min-width="120"/>
        <el-table-column label="病人姓名" align="center" key="patName" prop="patName" min-width="120"/>
        <el-table-column label="手机号" align="center" key="patPhone" prop="patPhone" min-width="120"/>
        <el-table-column label="操作" align="center" min-width="120" class-name="small-padding fixed-width">
          <template slot-scope="scope">
            <el-button
              size="mini"
              type="text"
              icon="el-icon-upload"
              @click="route2Patient(scope.row)"
            >上传文件
            </el-button>
            <el-button
              size="mini"
              type="text"
              icon="el-icon-check"
              @click="route2Patient(scope.row)"
            >阅片
            </el-button>
            <el-button
              size="mini"
              type="text"
              icon="el-icon-update"
              @click="handleUpdate(scope.row)"
              v-hasPermi="['ct:patient:edit']"
            >修改
            </el-button>
            <el-button
              size="mini"
              type="text"
              icon="el-icon-delete"
              @click="handleDelete(scope.row)"
              v-hasPermi="['ct:patient:remove']"
            >删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <pagination
        :total="total"
        :page.sync="queryParams.pageNum"
        :limit.sync="queryParams.pageSize"
        @pagination="getList"
      />
    </div>
    <!-- 添加或修改patientInfo对话框 -->
    <el-dialog :title="title" :visible.sync="open" width="600px" append-to-body v-dialogDrag v-dialogDragHeight>
      <el-form ref="form" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="身份证号" prop="patCardId">
          <el-input v-model="form.patCardId" placeholder="请输入身份证号"/>
        </el-form-item>
        <el-form-item label="病人姓名" prop="patName">
          <el-input v-model="form.patName" placeholder="请输入病人姓名"/>
        </el-form-item>
        <el-form-item label="病人手机号码" prop="patPhone">
          <el-input v-model="form.patPhone" placeholder="请输入病人手机号码"/>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button type="primary" :loading="submitLoading" @click="submitForm">确 定</el-button>
        <el-button @click="cancel">取 消</el-button>
      </div>
    </el-dialog>

    <!--    上传文件-->
    <uploader ref="uploader"
              :options="options"
              class="uploader-example"
              :auto-start="false"
              @file-added="onFileAdded"
              @file-success="onFileSuccess"
              @file-error="onFileError"
              @file-removed="fileRemoved"
    >
      <uploader-unsupport></uploader-unsupport>
      <uploader-drop>
        <p>拖动文件到灰色区域</p>
        <uploader-btn multiple style="background-color: #67C13B">上传文件</uploader-btn>
        <!--        <uploader-btn :attrs="attrs">上传限定文件</uploader-btn>-->
        <uploader-btn style="background-color: #79BBFF" :directory="true">上传文件夹</uploader-btn>
        <!--        <span class="filetotal">共计: {{ this.file_total }}</span>-->
        <el-button class="uploader-btn" style="background-color: #67f13B" @click="cancelUpload">取消上传</el-button>
        <el-button class="uploader-btn" style="background-color: #7fBBFF" @click="submitUpload">开始上传</el-button>
      </uploader-drop>
      <uploader-list
      ></uploader-list>
    </uploader>


  </div>
</template>

<script>
import {listPatient, getPatient, delPatient, addPatient} from "../../api/ct/patient";
import {getToken} from "common/src/utils/auth";
import {updatePatient} from "../../api/ct/ctFileUpload";
import dicomParser from "dicom-parser";


export default {
  name: "Patient",
  data() {
    return {
      //region 病人列表数据
      // 遮罩层
      loading: true,
      // 提交状态
      submitLoading: false,
      // 选中数组
      ids: [],
      // 非单个禁用
      single: true,
      // 非多个禁用
      multiple: true,
      // 显示搜索条件
      showSearch: true,
      // 总条数
      total: 0,
      // patientInfo表格数据
      patientList: [],


      // 弹出层标题
      title: "",
      // 是否显示弹出层
      open: false,
      // 查询参数
      queryParams: {
        pageNum: 1,
        pageSize: 5,
        patCardId: null,

        patName: null,

        patPhone: null,

      },
      // 列信息
      columns: [
        {key: 0, label: `序号`, visible: true},
        {key: 1, label: `身份证号`, visible: true},

        {key: 2, label: `病人姓名`, visible: true},

        {key: 3, label: `病人手机号码`, visible: true}

      ],
      // 表单参数
      form: {},
      // 表单校验
      rules: {
        patCardId: [
          {required: true, message: "身份证号不能为空", trigger: "blur"}
        ],

        patName: [
          {required: true, message: "病人姓名不能为空", trigger: "blur"}
        ],

        patPhone: [
          {required: true, message: "病人手机号码不能为空", trigger: "blur"}
        ],

      },
      //  endregion
      //  region 文件上传数据
      options: {
        target: process.env.VUE_APP_BASE_API + "/ct/upload/ctFile",
        headers: {
          Authorization: "Bearer " + getToken(),
        },
        testChunks: false,
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
      errorFileList: [], //上传失败信息列表
      controllerErrorFileDialog: false,
      reader: new FileReader()
      //  endregion
    };
  },
  created() {
    this.getList();
    // this.options.headers.Authorization = "Bearer " + getToken() // 让每个请求携带自定义token 请根据实际情况自行修改
    // // this.options.target = process.env.VUE_APP_BASE_API + '/system/enterprise/changeLogo'
    // this.options.target = process.env.VUE_APP_BASE_API + '/ct/upload/ctFile'

    console.log('target：', this.options.target)
  },
  methods: {
    //region 展示病人列表并展示
    /** 查询patientInfo列表 */
    getList() {
      this.loading = true;
      listPatient(this.queryParams).then(response => {
        this.patientList = response.data.items;
        this.total = response.data.total;
        this.loading = false;
      });
    },
    // 取消按钮
    cancel() {
      this.open = false;
      this.reset();
    },
    // 表单重置
    reset() {
      this.form = {
        patId: null,

        patCardId: null,

        patName: null,

        patPhone: null,

      };
      this.resetForm("form");
      this.submitLoading = false;
    },
    /** 搜索按钮操作 */
    handleQuery() {
      this.queryParams.pageNum = 1;
      this.getList();
    },
    /** 重置按钮操作 */
    resetQuery() {
      this.resetForm("queryForm");
      this.handleQuery();
    },
    // 多选框选中数据
    handleSelectionChange(selection) {
      this.ids = selection.map(item => item.patId)
      this.single = selection.length !== 1
      this.multiple = !selection.length
    },
    /** 新增按钮操作 */
    handleAdd() {
      this.reset();
      this.open = true;
      this.title = "添加patientInfo";
    },
    route2Patient(row) {
      const patId = row.patId || this.ids[0]
      this.$router.push({name: 'ct2row'})
    },
    /** 修改按钮操作 */
    handleUpdate(row) {
      this.reset();
      const patId = row.patId || this.ids[0]
      getPatient({patId: patId}).then(response => {
        this.form = response.data;
        this.open = true;
        this.title = "修改patientInfo";
      });
    },
    /** 提交按钮 */
    submitForm() {
      this.submitLoading = true;
      this.$refs["form"].validate(valid => {
        if (valid) {
          if (this.form.patId != null) {
            updatePatient(this.form).then(response => {
              this.$modal.msgSuccess("修改成功");
              this.open = false;
              this.getList();
            }).catch(() => {
              this.submitLoading = false
            });
          } else {
            addPatient(this.form).then(response => {
              this.$modal.msgSuccess("新增成功");
              this.open = false;
              this.getList();
            }).catch(() => {
              this.submitLoading = false
            });
          }
        } else {
          this.submitLoading = false;
        }
      });
    },
    /** 删除按钮操作 */
    handleDelete(row) {
      const patIds = row.patId || this.ids;
      let that = this;
      this.$modal.confirm('是否确认删除patientInfo编号为"' + patIds + '"的数据项?').then(function () {
        return delPatient(that.updateParamIds(patIds));
      }).then(() => {
        this.getList();
        this.$modal.msgSuccess("删除成功");
      }).catch(() => {
      });
    },
    /** 导出按钮操作 */
    handleExport() {
      this.download('ct/patient/export', {
        ...this.queryParams
      }, `patientInfo_${new Date().getTime()}数据.xlsx`)
    },
    //endregion
    fileStatusText(status, response) {
      const statusTextMap = {
        uploading: 'uploading',
        paused: 'paused',
        waiting: 'waiting',
        error: 'error',
        success: 'success'
      }
      if (status === 'paused') {
        console.log("response", response.data)
      }
      if (status === 'success' || status === 'error') {
        // 只有status为success或者error的时候可以使用 response

        // eg:
        // return response data ?
        console.log("response", response.data)
      } else {
        return statusTextMap[status]
      }
    },
    //region 文件上传

//添加文件到列表还未上传,每添加一个文件，就会调用一次,在这里过滤并收集文件夹中文件格式不正确信息，同时把所有文件的状态设为暂停中
    onFileAdded(file) {
      let that = this
      console.log("onFileAdded", file)
      // let reader = new FileReader()
      let temp = file.file
      file.fffjm={
        na:'shadow',
        tempJM:'sd',
      }
      console.log("temp", temp)
      this.reader.readAsArrayBuffer(temp)
      this.reader.onloadend = function (temp) {
        let arrayBuffer = that.reader.result;
        let byteArray = new Uint8Array(arrayBuffer)
        let dataSet = dicomParser.parseDicom(byteArray)

        let patientName = dataSet.string('x00100010')
        let patientId = dataSet.string('x00100020')
        let patientDob = dataSet.string('x00100030')
        let patientSex = dataSet.string('x00100040')

        let scanOpt = dataSet.string('x00180022')
        let encodingOpt = dataSet.string('x00080102')
        console.log('Patient Name          = ' + patientName)
        console.log('Patient ID            = ' + patientId)
        console.log('Patient Date of Birth = ' + patientDob)
        console.log('Patient Gender        = ' + patientSex)
        console.log('Scan optionss         = ' + scanOpt)
        console.log('Encoding type         = ' + encodingOpt)
      }


      // console.log("onFileAdded:", this.$refs.uploader)
      // console.log("status", file.uploader.fileStatusText)
      //后缀
      // let file_type = file.name.substring(file.name.lastIndexOf(".") + 1);
      // const extension = file_type === this.uploadType;
      // if (!extension) {
      //   let obj = {
      //     rootname: '无',
      //     name: file.name,
      //     errorinfo: "文件不是 " + this.uploadType + " 格式",
      //   };
      //   let arr = file.relativePath.split("/");
      //   if (arr.length > 1) {
      //     obj['rootname'] = arr[0]
      //   }
      //   this.errorFileList.push(obj);
      //   file.ignored = true
      // } else {
      // file.resume();
      // }
      // this.$nextTick(() => {
      //   this.file_total = this.$refs['uploader'].files.length
      // });
      // if (this.errorFileList.length !== 0) {
      //   this.controllerErrorFileDialog = true
      // }
    },

//每个文件传输给后端之后，返回的信息
    onFileSuccess(rootFile, file, response, chunk) {
      console.log("status", file.uploader.fileStatusText)
      console.log("onFileSuccess:", this.$refs.uploader)
      let res = JSON.parse(response)
      console.log("onFileSuccess", res)
      if (res.code !== 10000) {
        let obj = {
          rootname: '无',
          name: file.name,
          errorinfo: res.message,
        };
        if (rootFile.isFolder === true) {
          obj['rootname'] = rootFile.name
        }
        this.errorFileList.push(obj);
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
      this.errorFileList.push(obj);
      this.controllerErrorFileDialog = true
    },
    // 移除文件
    fileRemoved(file) {
      console.log("fileRemoved", file)
      this.$nextTick(() => {
        this.file_total = this.$refs.uploader.files.length
      });
    },
//点击开始上传按钮
    submitUpload() {
      console.log('提交上传')
      this.$nextTick(() => {
        this.$refs.uploader.files.forEach(item => {
          item.resume()
        })
      })
      ;
    },
//关闭错误文件提示框口，知道上传对话框被关闭时才会被清空
    closeErrorDialog() {
      this.errorDialog = false;
    }
    ,
// 上传弹框关闭
    handelClose() {
      this.clearcache()
      this.thirdDialog = false
    }
    ,
// 清除缓存
    clearcache() {
      this.file_total = 0;
      this.errorFileList = []
      this.controllerErrorFileDialog = false
      this.$refs.uploader.uploader.cancel()
      this.getresourceDetail();
    }
    ,
//取消上传
    cancelUpload() {
      this.thirdDialog = false;
      this.clearcache();
    }
    ,
//  endregion

// changeflie(event) {
//   let files = event.target.files[0]        //获取文件
//   let formData = new FormData();
//   formData.append('file', files);         //file  是你接口参数名
//   updatePatient(formData).then(res => {     	//请求接口
//     console.log(res)
//   })
// },
  }


}
</script>
<style>
.uploader-example {
  width: 100%;
  padding: 15px;
  margin: 0 auto 0;
  font-size: 14px;
  box-shadow: 0 0 10px rgba(0, 0, 0, .4);
  background-color: white;
}

.uploader-example .uploader-btn {
  margin-right: 8px;
}

.uploader-example .uploader-list {
  max-height: 440px;
  overflow: auto;
  overflow-x: hidden;
  overflow-y: auto;

}

.uploader-btn {
  display: inline-block;
  position: relative;
  padding: 4px 8px;
  font-size: 100%;
  line-height: 1.4;
  color: #666;
  border: 1px solid #666;
  cursor: pointer;
  border-radius: 2px;
  background: none;
  outline: none;
}

.uploader-btn:hover {
  background-color: rgba(0, 0, 0, .08);
}

/*.uploader-example .uploader-list .uploader-file[status="uploading"]> .uploader-file-info{*/
/*> .uploader-file-status > span> i{*/
/*  visibility:hidden;*/
/*}*/
/*> .uploader-file-status > span> em{*/
/*  visibility:hidden;*/
/*}*/
/*}*/


</style>
