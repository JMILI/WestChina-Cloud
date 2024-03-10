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
            v-hasPermi="['ct:patients:add']"
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
            v-hasPermi="['ct:patients:edit']"
          >修改
          </el-button>
        </el-col>
        <el-col :span="1.5">
        </el-col>
        <!--        <el-col :span="1.5">-->
        <!--          <download-excel-->
        <!--            class="export-excel-wrapper"-->
        <!--            :data="patientsList"-->
        <!--            :fields="json_fields"-->
        <!--            header="病人信息表"-->
        <!--            name="请命名"-->
        <!--          >-->
        <!--            <el-button-->
        <!--              type="warning"-->
        <!--              plain-->
        <!--              icon="el-icon-download"-->
        <!--              size="mini"-->
        <!--              v-hasPermi="['ct:patients:export']"-->
        <!--            >导出-->
        <!--            </el-button>-->
        <!--          </download-excel>-->
        <!--        </el-col>-->

        <el-col :span="1.5">

          <el-button
            type="warning"
            plain
            icon="el-icon-download"
            size="mini"
            @click="bn_openExport()"
          >批量导出
          </el-button>
        </el-col>

        <el-col :span="1.5">
          <el-button
            type="warning"
            plain
            icon="el-icon-sort"
            size="mini"
            @click="handleSort"
            v-show="sortVisible"
            v-hasPermi="['ct:patients:edit']"
          >保存排序
          </el-button>
        </el-col>


        <right-toolbar :showSearch.sync="showSearch" @controlSortable="handleSortable" @queryTable="getList"
                       :columns="columns"/>
      </el-row>

      <el-table v-loading="loading" :data="patientsList" @selection-change="handleSelectionChange" ref="dataTable"
                row-key="patId">
        <el-table-column type="selection" width="55" align="center" class-name="allowDrag"/>
        <el-table-column label="序号" align="center" min-width="50" class-name="allowDrag" v-if="columns[0].visible">
          <template slot-scope="scope">
            <span>{{ queryParams.pageSize * (queryParams.pageNum - 1) + scope.$index + 1 }}</span>
          </template>
        </el-table-column>
        <el-table-column label="身份证号" align="center" key="patCardId" prop="patCardId" min-width="120"
                         class-name="allowDrag" v-if="columns[1].visible"/>
        <el-table-column label="病人姓名" align="center" key="patName" prop="patName" min-width="50"
                         class-name="allowDrag"
                         v-if="columns[2].visible"/>
        <el-table-column label="病人手机号码" align="center" key="patPhone" prop="patPhone" min-width="50"
                         class-name="allowDrag" v-if="columns[3].visible"/>
        <el-table-column label="操作" align="right" min-width="150" class-name="small-padding fixed-width allowDrag">
          <template slot-scope="scope">
            <el-button
              size="mini"
              type="text"
              icon="el-icon-check"
              @click="route2Patient(scope.row)"
              v-hasPermi="['ct:patients:edit']"
            >阅片
            </el-button>
            <el-button
              size="mini"
              type="text"
              icon="el-icon-check"
              @click="manageMaker(scope.row)"
            >标记图像管理
            </el-button>
            <el-button
              size="mini"
              type="text"
              icon="el-icon-check"
              @click="manage(scope.row)"
            >CT图像管理
            </el-button>
            <!--            这里使用v-hasPermi="['ct:patients:edit']" 让只有这个权限的用户可以看到-->
            <el-button
              size="mini"
              type="text"
              icon="el-icon-edit"
              @click="handleUpdate(scope.row)"
              v-hasPermi="['ct:patients:edit']"
            >修改
            </el-button>
            <el-button
              size="mini"
              type="text"
              icon="el-icon-delete"
              @click="handleDelete(scope.row)"
              v-hasPermi="['ct:patients:remove']"
            >删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <pagination
        :total="total"
        :page.sync="queryParams.pageNum"
        :limit.sync="queryParams.pageSize"
        :page-sizes="[3, 5, 10,20,30,40,50]"
        layout="prev, pager, next, jumper,->,sizes,total"
        @pagination="getList"
      />
    </div>

    <!-- 添加或修改病人信息对话框 -->
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

    <el-dialog v-bind="$attrs" :visible.sync="openHit" @close="onCloseHit" title="上传dicom文件---查询病人档案">
      <el-form ref="elFormPatient" :model="formHit" :rules="rules" size="medium" label-width="100px">
        <el-form-item label="手机号" prop="patPhone">
          <el-input v-model="formHit.patPhone" placeholder="请输入手机号" clearable prefix-icon='el-icon-phone'
                    :style="{width: '100%'}"></el-input>
        </el-form-item>
        <el-form-item label="身份证号" prop="patCardId">
          <el-input v-model="formHit.patCardId" placeholder="请输入身份证号" show-word-limit clearable
                    prefix-icon='el-icon-user-solid' :style="{width: '100%'}"></el-input>
        </el-form-item>
        <el-form-item label="">
          <el-button type="primary" icon="el-icon-search" size="medium" @click="searchHit"> 搜索</el-button>
        </el-form-item>
        <el-form-item label="选择病人" prop="patCardId">
          <el-select v-model="formHitSelect" placeholder="选中病人才能成功,选框中默认显示身份证号" filterable clearable
                     :style="{width: '100%'}">
            <el-option v-for="item in patientsList" :key="item.patCardId" :label="item.patName" :value="item.patCardId"
                       :disabled="item.disabled"></el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <div slot="footer">
        <el-button @click="closeHit">取消</el-button>
        <el-button type="primary" @click="okHit">确定</el-button>
      </div>
    </el-dialog>

    <!--    上传文件-->
    <uploader ref="uploader"
              v-if="haveBucket"
              :options="options"
              class="uploader-example"
              :auto-start="false"
              @file-error="onFileError"
              @file-added="onFileAdded"
              @files-added="onFilesAdded"
              @files-removed="onFilesRemoved"
              v-hasPermi="['ct:patients:add']"
    >
      <uploader-unsupport></uploader-unsupport>
      <uploader-drop>
        <p>拖动文件到灰色区域</p>
        <!--        <uploader-btn multiple style="background-color: #67C13B">上传文件</uploader-btn>-->
        <uploader-btn style="background-color: #79BBFF"
                      :directory="true"
                      :single="true" :attrs="attrs"
                      @click="uploadFolder">上传文件夹
        </uploader-btn>

        <el-button class="uploader-btn" style="background-color: #67f13B" @click="cancelUpload">取消上传</el-button>
        <el-button class="uploader-btn" style="background-color: #7fBBFF" @click="submitUpload">开始上传</el-button>
      </uploader-drop>
      <!--      <span class="filetotal">共计: {{ this.file_total }}</span>-->
      <uploader-list>
      </uploader-list>
    </uploader>
    <el-dialog title="上传文件信息展示---括号内为StudyUID和seriesUID" :visible.sync="openTree"
               width="900px"
               append-to-body
               v-dialogDrag
               v-dialogDragHeight>
      <pre>{{ JSON.stringify(studyUidList, null, 4) }}</pre>
      <!--      <el-tree :data="openTreeData"-->
      <!--               :props="defaultProps"-->
      <!--               highlight-current-->
      <!--               default-expand-all-->
      <!--               @node-click="handleNodeClick">-->
      <!--      </el-tree>-->
      <div slot="footer" class="dialog-footer">
        <el-button type="primary" :loading="submitLoading" @click="canUp">确 定</el-button>
        <el-button @click="cancelUp">取 消</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
//region import
import {
  addPatients,
  delPatients,
  getPatients,
  listPatients,
  updatePatients,
  updatePatientsSort
} from "../../api/ct/patients";
import Sortable from "sortablejs";
import {getToken} from "common/src/utils/auth";
import dicomParser from "dicom-parser";
import {getBucketName} from "../../api/ct/ctFileUpload";
import Cookies from "~../../js-cookie";
import {addDicom, getDicomByPatCardId, getStudyListByPatCardId} from "../../api/ct/dicom";
import {mapActions} from "vuex"
import {getDicomMakerByPatCardId} from "../../api/ct/maker";
import {export_json_to_excel} from "../../utils/generator/Export2Excel";
import {minioUrl} from "../../settings";
//endregion

export default {
  name: "Patients",
  data() {
    // 身份证验证
    var validatorIdCard = (rule, value, callback) => {
      // 地区
      var aCity = {
        11: "北京", 12: "天津", 13: "河北", 14: "山西", 15: "内蒙古",
        21: "辽宁", 22: "吉林", 23: "黑龙江",
        31: "上海", 32: "江苏", 33: "浙江", 34: "安徽", 35: "福建", 36: "江西", 37: "山东",
        41: "河南", 42: "湖北", 43: "湖南", 44: "广东", 45: "广西", 46: "海南", 50: "重庆",
        51: "四川", 52: "贵州", 53: "云南", 54: "西藏",
        61: "陕西", 62: "甘肃", 63: "青海", 64: "宁夏", 65: "新疆",
        71: "台湾", 81: "香港", 82: "澳门", 91: "国外"
      };
      // 验证长度
      if (!/^\d{17}(\d|x)$/i.test(value)) {
        callback(new Error('您输入的身份证号长度或格式错误，请输入正确的身份证号'));
        return;
      }
      // 验证前两位是否为省份代码
      value = value.replace(/x$/i, "a");
      if (aCity[parseInt(value.substr(0, 2))] == null) {
        callback(new Error('您输入的身份证号长度或格式错误，请输入正确的身份证号'));
        return;
      }
      // 身份证上的出生年月校验
      var sBirthday = value.substr(6, 4) + "-" + Number(value.substr(10, 2)) + "-" + Number(value.substr(12, 2));
      var d = new Date(sBirthday.replace(/-/g, "/"));
      if (sBirthday != (d.getFullYear() + "-" + (d.getMonth() + 1) + "-" + d.getDate())) {
        callback(new Error('您输入的身份证号不合法，请输入正确的身份证号'));
        return;
      }
      // 身份证校验位判断
      var iSum = 0;
      for (var i = 17; i >= 0; i--) {
        iSum += (Math.pow(2, i) % 11) * parseInt(value.charAt(17 - i), 11);
      }
      if (iSum % 11 != 1) {
        callback(new Error('您输入的身份证号不合法，请输入正确的身份证号'));
        return;
      }
      callback()
    };
    return {
      //region 获取该账号所对应的BucketName
      enterpriseName: '',
      bucketNameOfMe: '',
      haveBucket: false,
      //endregion
      //region 病人数据
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
      // 病人信息表格数据
      patientsList: [],


      // 病人信息表格原始数据
      oldPatientsList: [],
      // 排序保存按钮显示
      sortVisible: false,
      // 排序参数
      sortable: null,


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

        {key: 3, label: `病人手机号码`, visible: true},
      ],
      // 表单参数
      form: {},
      // 表单校验
      rules: {
        patCardId: [
          {required: true, validator: validatorIdCard, trigger: "blur"}
        ],

        patName: [
          {required: true, message: "病人姓名不能为空", trigger: "blur"}
        ],

        patPhone: [
          {
            required: true,
            pattern: /^1(3[0-9]|4[01456879]|5[0-35-9]|6[2567]|7[0-8]|8[0-9]|9[0-35-9])\d{8}$/,
            message: '请输入正确的手机号码',
            trigger: "blur"
          }
        ],
      },
      //  endregion
      // region 导出excel
      // 第一种方法导出excel
      json_fields: {
        "身份证号": 'patCardId',
        "病人姓名": 'patName',
        "手机号": 'patPhone',
      },
      json_meta: [
        [{
          " key ": " charset ",
          " value ": " utf- 8 "
        }]
      ],
      patientExcel: '病人信息_' + new Date().getTime(),
      // 第二种方法导出excel
      json_data: [],
      // endregion
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
        accept: ['.dcm', '.png', '.jpeg']
      },
      file_total: 0, //本次文件上传的总数
      errorFileList: [], //上传失败信息列表
      controllerErrorFileDialog: false,
      //  endregion
      //  region 查询病人选中遮罩层
      openHit: false,
      formHit: {
        patPhone: '',
        patCardId: '',
        patName: '',
      },

      // patPhoneOptions: [],
      formHitSelect: '',
      uploadToPatient: {
        upload: false,
        patCardId: '',
      },
      //  endregion
      //  region 文件信息统计
      studyUidList: {},
      isFinishAnalysis: false,
      //  endregion
      //  region 上传提示
      openTree: false,
      openTreeData: [],
      defaultProps: {
        children: 'children',
        label: 'label'
      },
      treeInfoIsTrue: false,
      ctDicom: {
        patCardId: '',
        dicomCtTime: '',
        dicomCtStudyUid: '',
        dicomCtSeriesUid: '',
        dicomCtBody: '',
        dicomCtPath: '',
        dicomCtCount: 0,
        dicomCtDescription: '',
      },
      ctDicomList: [],
      dicomPrefix: 'wadouri:'
      //  endregion
    };
  },
  created() {
    this.getBucketName()
    this.getList();
  },

  beforeRouteLeave(to, from, next) {
    // console.log("---------patient-----from----", from)
    // console.log("---------patient------to-----", to)
    if ((to.name === null) || (to.name === undefined)) {
      this.$router.replace({name: 'maker'})
    } else {
      next();
    }
  },
  methods: {
    //region 导出所选内容
    //导出功能
    bn_openExport() {
      let that = this
      //1.如果用勾选了内容，那就导出用户勾选那些，如果用户什么都没有勾选，那就导出当前表格里的全部内容
      that.$confirm("此操作将按照所选数据导出为excel, 是否继续?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning"
      }).then(() => {
        //调用表格导出的方法
        that.export2Excel();
      }).then(() => {
        that.json_data = []
      }).catch(() => {
        that.$message({
          message: "已取消导出",
          type: "info",
        });
      });
    },
    export2Excel() {//导出方法
      let that = this
      //用户是否勾选，如勾选，则默认导出当前的，勾选仅导出勾选那些
      if (that.json_data === undefined || that.json_data.length === 0) {
        that.json_data = that.patientsList
      }
      //这里必须使用绝对路径，根据自己的命名和路径，之前下载的插件存放路径
      const tHeader = [
        "身份证号",
        "病人姓名",
        "手机号",
      ]; // 导出的表头名
      const filterVal = [
        'patCardId',
        'patName',
        'patPhone',
      ]; // 导出的表头字段名,要插入内容数据需要一一对应
      const data = that.formatJson(filterVal, that.json_data);
      let excelName = '病人信息表_' + new Date().getTime()
      // tHeader为导出Excel表头名称，that.excelName即为导出Excel名称
      export_json_to_excel(tHeader, data, excelName, "病人信息表"); //tHeader为表头，data为表内容，that.excelName导出的表格名称
    },

    formatJson(filterVal, jsonData) {//数据插入表中
      return jsonData.map(v => filterVal.map(j => v[j]));
    },
    //endregion
    //region 文件上传
    fileStatusText(status, response) {
      const statusTextMap = {
        uploading: 'uploading',
        paused: 'paused',
        waiting: 'waiting',
        error: 'error',
        success: 'success'
      }
      if (status === 'paused') {
        status = 'waiting'
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
    uploadFolder() {
      this.loading = true
    },
    onFileAdded(file) {
      console.log("file：", file.name)
      let that = this
      if (file.isFolder !== true) {
        let file_type = file.name.substring(file.name.lastIndexOf("."));
        console.log("文件类型：", file_type)
        if (file_type === '.dcm') {
          let reader = new FileReader()
          let temp = file.file
          reader.readAsArrayBuffer(temp)
          reader.onloadend = function (temp) {
            let arrayBuffer = reader.result;
            let byteArray = new Uint8Array(arrayBuffer)
            let dataSet = dicomParser.parseDicom(byteArray)
            let seriesDate = dataSet.string('x00080021')
            let studyUID = dataSet.string('x0020000d')
            let seriesUID = dataSet.string('x0020000e')
            let imageNumber = dataSet.string('x00200013')
            let bodyPart = dataSet.string('x00180015')
            //前缀得从后端获取
            let path = studyUID + '/' + seriesUID + '/' + imageNumber + '.dcm'
            file.name = path
            //统计信息，study,series信息
            if (that.studyUidList.hasOwnProperty(studyUID)) {
              if (that.studyUidList[studyUID].hasOwnProperty(seriesUID)) {
                that.isFinishAnalysis = false
                ++that.studyUidList[studyUID][seriesUID]
              } else {
                that.studyUidList[studyUID][seriesUID] = 1
              }
              //没出现过得study序列
            } else {
              that.studyUidList[studyUID] = {}
              that.studyUidList[studyUID][seriesUID] = 1
            }
            //将第一张图像记录存入数据库
            if (imageNumber === '1') {
              let ctDicomTemp = {}
              ctDicomTemp.dicomCtTime = seriesDate
              ctDicomTemp.dicomCtStudyUid = studyUID
              ctDicomTemp.dicomCtSeriesUid = seriesUID
              ctDicomTemp.dicomCtBody = bodyPart
              ctDicomTemp.dicomCtPath = path
              //后面要填写
              ctDicomTemp.patCardId = ''
              ctDicomTemp.dicomCtCount = 0
              ctDicomTemp.dicomCtDescription = ''
              that.ctDicomList.push(ctDicomTemp)
            }
            //region 数组的
            //假设没找到
            // studyUID = '研究ID：（' + studyUID + ')'
            // seriesUID = '序列ID以及对应dicom文件数:(' + seriesUID + ')'
            // let flagStudy = false
            // that.openTreeData.forEach(study => {
            //   if (study.label === studyUID) {
            //     //找到了studyUID
            //     flagStudy = true
            //     let flagSeries = false
            //     study.children.forEach(series => {
            //       if (series.label === seriesUID) {
            //         flagSeries = true
            //         series.children[0]++
            //       }
            //     })
            //     //没找到seriesUID
            //     if (flagSeries === false) {
            //       let seriesTemp = {}
            //       seriesTemp.label = seriesUID
            //       seriesTemp.children = []
            //       seriesTemp.children.push(1)
            //       study.children.push(seriesTemp)
            //     }
            //   }
            // })
            // //没找到
            // if (flagStudy === false) {
            //   let temp = {}
            //   temp.label = studyUID
            //   temp.children = []
            //   //加进来
            //   that.openTreeData.push(temp)
            // }
            //  endregion
          }
        }
        // else {
        //   let reader = new FileReader()
        //   let temp = file.file
        //   reader.readAsArrayBuffer(temp)
        //   reader.onloadend = function (temp) {
        //     let arrayBuffer = reader.result;
        //     let byteArray = new Uint8Array(arrayBuffer)
        //     let dataSet = dicomParser.parseDicom(byteArray)
        //     let seriesDate = dataSet.string('x00080021')
        //     let studyUID = dataSet.string('x0020000d')
        //     let seriesUID = dataSet.string('x0020000e')
        //     let imageNumber = dataSet.string('x00200013')
        //     let bodyPart = dataSet.string('x00080015')
        //     //前缀得从后端获取
        //     let path = studyUID + '/' + seriesUID + '/' + imageNumber + '.dcm'
        //     file.name = path
        //     console.log("-----------------------", path)
        //     //统计信息，study,series信息
        //     if (that.studyUidList.hasOwnProperty(studyUID)) {
        //       if (that.studyUidList[studyUID].hasOwnProperty(seriesUID)) {
        //         that.isFinishAnalysis = false
        //         ++that.studyUidList[studyUID][seriesUID]
        //       } else {
        //         that.studyUidList[studyUID][seriesUID] = 1
        //       }
        //       //没出现过得study序列
        //     } else {
        //       that.studyUidList[studyUID] = {}
        //       that.studyUidList[studyUID][seriesUID] = 1
        //     }
        //     //将第一张图像记录存入数据库,有些不一定是从1开始的
        //     if (imageNumber === '1') {
        //       let ctDicomTemp = {}
        //       ctDicomTemp.dicomCtTime = seriesDate
        //       ctDicomTemp.dicomCtStudyUid = studyUID
        //       ctDicomTemp.dicomCtSeriesUid = seriesUID
        //       ctDicomTemp.dicomCtBody = bodyPart
        //       ctDicomTemp.dicomCtPath = process.env.VUE_APP_MINIO_API + that.bucketNameOfMe + '/' + path
        //       //后面要填写
        //       ctDicomTemp.patCardId = ''
        //       ctDicomTemp.dicomCtCount = 0
        //       ctDicomTemp.dicomCtDescription=''
        //       that.ctDicomList.push(ctDicomTemp)
        //     }
        //   }
        // }
      }
    },
    onFilesAdded(files, fileList) {
    },
    // 上传错误触发，文件还未传输到后端
    onFileError(rootFile, file, response, chunk) {
      this.$modal.msgWarning("不能通过小箭头上传，因为还没有填写文件关联的病人信息")
    },
    onFilesRemoved(file) {
      this.$nextTick(() => {
        this.file_total = this.$refs['uploader'].files.length
      });
    },
    //点击开始上传按钮
    submitUpload() {
      let that = this
      // 上传禁止操作
      if (that.uploadToPatient.patCardId !== '') {
        const isFinishUpload = new Promise((resolve, reject) => {
          //已经有了要上传的病人信息
          //生成数据库字段,
          if (that.ctDicomList.length > 0) {
            that.ctDicomList.forEach(item => {
              if (item.dicomCtBody === undefined) {
                item.dicomCtBody = ''
              }
              item.patCardId = that.uploadToPatient.patCardId
              item.dicomCtCount = that.studyUidList[item.dicomCtStudyUid][item.dicomCtSeriesUid]
            })
            resolve(that.ctDicomList)
          } else {
            reject("没有上传文件")
          }
        })
        //数据库写入记录
        isFinishUpload.then(ctDicomList => {
          return new Promise((resolve, reject) => {
            ctDicomList.forEach(item => {
              debugger
              addDicom(item).then(response => {
                //  成功
              }).catch(error => {
                reject("数据库增加记录失败")
              })
            })
            resolve(true)
          })
        }).then(isRecord => {
          return new Promise((resolve, reject) => {
            if (isRecord === true) {
              that.$nextTick(() => {
                that.$refs.uploader.files.forEach(item => {
                  item.resume()
                })
              });
              resolve(true)
            }
          })
        }).then(isRecordAndResume => {
          if (isRecordAndResume === true) {
            that.uploadToPatient.patCardId = ''
            //清理上传文件的记录信息
            that.ctDicomList = []
            //清除上传文件的统计信息
            that.studyUidList = {}
          }
        }).catch(err => {
          this.model.msgError(err)
        })

      } else {
        this.openHit = true
      }


    },

//关闭错误文件提示框口，知道上传对话框被关闭时才会被清空
    closeErrorDialog() {
      this.errorDialog = false;
    }
    ,
// 上传弹框关闭
    handleClose() {
      this.clearCache()
      this.thirdDialog = false
    }
    ,
// 清除缓存
    clearCache() {
      this.file_total = 0;
      this.errorFileList = []
      this.controllerErrorFileDialog = false
      this.$refs.uploader.uploader.cancel()
    }
    ,
//取消上传
    cancelUpload() {
      this.thirdDialog = false;
      this.clearCache();
      //清楚绑定的标记
      this.resetHit();
    }
    ,
//  endregion
    //region 上传提示
    handleNodeClick(openTreeData) {
      console.log(openTreeData);
    },
    canUp() {
      this.treeInfoIsTrue = true;
      this.openTree = false;
    },
    cancelUp() {
      this.openTree = false;
      this.treeInfoIsTrue = false;
    },
    //endregion
    //region 搜索病人，选中
    onCloseHit() {
      let that = this
      this.$nextTick(() => {
        that.$refs['elFormPatient'].resetForm()
      })
    },
    closeHit() {
      this.openHit = false
    },
    okHit() {
      let that = this
      this.$modal.msgSuccess("您可以为该病人添加dicom文件了！或者上传了");
      const aa = new Promise(resolve => {
        that.uploadToPatient.patCardId = this.formHitSelect
        resolve()
      })
      aa.then(res => {
        that.openHit = false
      })
    },
    searchHit() {
      // 1.后台查找该病人数据，
      // 临时使用页面顶部的搜身功能，借用的搜索一下
      //设置搜索参数，准备搜索
      let that = this
      that.queryParams.pageNum = 1
      that.queryParams.pageSize = 10
      that.queryParams.patCardId = this.formHit.patCardId
      that.queryParams.patName = this.formHit.patName
      that.queryParams.patPhone = this.formHit.patPhone
      // 2.加载数据后
      let waitData = new Promise(() => {
        listPatients(this.queryParams).then(response => {
          that.patientsList = response.data.items;
          that.total = response.data.total;
        });
      })
    },
    //endregion
    //region 病人列表
    /** 查询病人信息列表 */
    getList() {
      this.loading = true;
      listPatients(this.queryParams).then(response => {
        this.patientsList = response.data.items;
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
      this.json_data = selection.map(item => item)
      this.single = selection.length !== 1
      this.multiple = !selection.length
    },
    /** 新增按钮操作 */
    handleAdd() {
      this.reset();
      this.open = true;
      this.title = "添加病人信息";
    },
    /** 修改按钮操作 */
    handleUpdate(row) {
      this.reset();
      const patId = row.patId || this.ids[0]
      getPatients({patId: patId}).then(response => {
        this.form = response.data;
        this.open = true;
        this.title = "修改病人信息";
      });
    },

    /** 提交按钮 */
    submitForm() {
      this.submitLoading = true;
      this.$refs["form"].validate(valid => {
        if (valid) {
          if (this.form.patId != null) {
            updatePatients(this.form).then(response => {
              this.$modal.msgSuccess("修改成功");
              this.open = false;
              this.getList();
            }).catch(() => {
              this.submitLoading = false
            });
          } else {
            addPatients(this.form).then(response => {
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
      const patIds = row.patId
      const patCardId = row.patCardId
      let that = this;
      that.$modal.confirm('是否确认删除病人"' + row.patName + '"的数据项?').then(function () {
        //判断是否有minio存储的文件，如果有，那么不能删除
        let flag = new Promise((resolve, reject) => {
          getDicomMakerByPatCardId({patCardId: patCardId}).then(response => {
            let total = response.data.total
            if (total > 0) {
              reject("1：该病人还有dicom文件或者标记图像，请先删除这些图像，再删除该病人信息！！！")
            } else {
              resolve("删除成功")
            }
          });
        })
        flag.then((value) => {
          return new Promise((resolve, reject) => {
            getDicomByPatCardId({patCardId: patCardId}).then(response => {
              let total = response.data.total
              if (total > 0) {
                reject("2：该病人还有dicom文件或者标记图像，请先删除这些图像，再删除该病人信息！！！")
              } else {
                resolve("删除成功")
              }
            });
          })
        }).then((value) => {
          that.$modal.msgSuccess(value);
          delPatients(that.updateParamIds(patIds));
        }).catch((err) => {
          that.$modal.msgWarning(err);
        })
      }).then(() => {
        setTimeout(() => {
          this.getList();
        }, 200)
      }).catch(() => {

      });
    },

    /** 保存排序按钮操作 */
    handleSort() {
      this.$modal.confirm('是否确认保存新排序?').then(() => {
        let params = this.sortOrderListOnlyDynamic(this.patientsList, this.oldPatientsList, "patId");
        if (params.length > 0) {
          return updatePatientsSort(this.updateParamIds(params));
        }
      }).then(() => {
        this.getList();
        this.sortVisible = false;
        this.$modal.msgSuccess("保存成功");
      }).catch(() => {
      });
    },
    /** 排序开关 */
    handleSortable(sortable) {
      if (!this.isMobile()) {
        this.sortable != null && this.sortable.destroy()
        const el = this.$refs.dataTable.$el.querySelectorAll(".el-table__body-wrapper > table > tbody")[0]
        this.sortable = Sortable.create(el, {
          disabled: sortable,
          handle: ".allowDrag",
          onEnd: evt => {
            const targetRow = this.patientsList.splice(evt.oldIndex, 1)[0];
            this.patientsList.splice(evt.newIndex, 0, targetRow);
            this.sortVisible = true
          }
        })
      }
    },
    //  endregion
    //region 跳转到阅片界面
    ...mapActions(['changePatientInfo', 'updatePatientsStudySeries', 'dicomOfPatCardId', 'makerOfPatCardId', 'setBucketName']),
    manageMaker(row) {
      //将需要查看的病人patCardId，存储起来
      new Promise(resolve => {
        console.log("标记：", row)
        let patient = {
          patCardId: row.patCardId,
          patName: row.patName,
          patPhone: row.patPhone,
        }
        this.changePatientInfo(patient)
        this.dicomOfPatCardId(row.patCardId)
        this.makerOfPatCardId(row.patCardId)
        resolve()
      }).then(resolve => {
        this.$router.push({name: 'maker'})
      }).catch(reject => {
        console.log("出现错误")
      })
    },
    manage(row) {
      //将需要查看的病人patCardId，存储起来
      new Promise(resolve => {
        console.log("dicom：", row)
        let patient = {
          patCardId: row.patCardId,
          patName: row.patName,
          patPhone: row.patPhone,
        }
        this.changePatientInfo(patient)
        this.dicomOfPatCardId(row.patCardId)
        this.makerOfPatCardId(row.patCardId)
        resolve()
      }).then(resolve => {
        this.$router.push({name: 'dicom'})
      }).catch(reject => {
        console.log("出现错误")
      })
    },
    /**
     * 跳转到阅片界面，并携带病人信息
     * @param row
     */
    route2Patient(row) {
      let that = this
      const temp1 = new Promise(resolve => {

        let patient = {
          patCardId: row.patCardId,
          patName: row.patName,
          patPhone: row.patPhone,
        }
        that.changePatientInfo(patient)
        this.dicomOfPatCardId(row.patCardId)
        this.makerOfPatCardId(row.patCardId)
        resolve()
      })

      const temp12 = new Promise((resolve, reject) => {
        getStudyListByPatCardId({patCardId: row.patCardId}).then(result => {
          let studySeriesList = {}
          if (result.data.length > 0) {
            result.data.forEach(item => {
              //归类
              if (studySeriesList.hasOwnProperty(item.dicomCtStudyUid)) {
                if (studySeriesList[item.dicomCtStudyUid].hasOwnProperty(item.dicomCtSeriesUid)) {
                  //  无需任何操作
                } else {
                  studySeriesList[item.dicomCtStudyUid][item.dicomCtSeriesUid] = item
                }
              } else {
                studySeriesList[item.dicomCtStudyUid] = {}
                studySeriesList[item.dicomCtStudyUid][item.dicomCtSeriesUid] = item
              }
              //  重写路径
              item.imageIds = []
              for (let i = 1; i <= item.dicomCtCount; i++) {
                let path = item.dicomCtPath.substring(0, item.dicomCtPath.lastIndexOf("/"));
                let dicomPrefix = that.dicomPrefix
                let newPath = dicomPrefix + minioUrl + that.bucketNameOfMe + '/' + path + '/' + i.toString() + '.dcm'
                item.imageIds.push(newPath)
              }
            })

            that.updatePatientsStudySeries(studySeriesList)
            resolve()
          } else {
            this.$modal.alertWarning("该病人可能没有ct影像，请先上传！")
            reject()
          }
        })
      })
      Promise
        .all([temp1, temp12])
        .then(() => {
          that.$router.push({name: 'ct2'})
        })
    },
    //endregion
    //region 获取该账号所对应的bucketNameOfMe
    getBucketName() {
      let that = this
      that.enterpriseName = Cookies.get("enterpriseName")
      // console.log("enterpriseName", this.enterpriseName)
      getBucketName({enterpriseName: this.enterpriseName}).then(result => {
        // console.log(result)
        if (result.data === '') {
          //没有桶，不能上传文件
          that.$modal.alertWarning(result.msg)
        } else {
          that.bucketNameOfMe = result.data;
          that.haveBucket = true;
          //vuex中存储
          that.setBucketName(result.data)
        }
      }).catch(err => {
        console.log("get bucket name caused error: " + err)
      })
    }
    ,
    //endregion
  }
  ,
  mounted() {
    this.handleSortable(false);
    // let bucketFileNamesList=[
    //   '1.3.12.2.1107.5.1.4.77426.30000021081723585752900180143_1677848657587.png',
    // ]
    // console.log(delFile(bucketFileNamesList))
    // console.log(delFolderFiles({folderName:'20210611004551'}))
  }
  ,
  watch: {}
  ,
  computed: {
    // options: function (value) {
    //   console.log("value:",value)
    //   options.target=value
    // }
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
</style>
