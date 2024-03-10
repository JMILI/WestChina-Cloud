<template>
  <div class="app-container">
    <div class="wrapper-container" v-show="showSearch">
      <el-form :model="queryParams" ref="queryForm" :inline="true" label-width="80px">
        <!--      <el-form-item label="单张图像instanceID" prop="instanceUid">-->
        <!--        <el-input-->
        <!--          v-model="queryParams.instanceUid"-->
        <!--          placeholder="请输入单张图像instanceID"-->
        <!--          clearable-->
        <!--          size="small"-->
        <!--          @keyup.enter.native="handleQuery"/>-->
        <!--      </el-form-item>-->
        <!--      <el-form-item label="研究id" prop="studyUid">-->
        <!--        <el-input-->
        <!--          v-model="queryParams.studyUid"-->
        <!--          placeholder="请输入研究id"-->
        <!--          clearable-->
        <!--          size="small"-->
        <!--          @keyup.enter.native="handleQuery"/>-->
        <!--      </el-form-item>-->
        <!--      <el-form-item label="序列UId" prop="seriesUid">-->
        <!--        <el-input-->
        <!--          v-model="queryParams.seriesUid"-->
        <!--          placeholder="请输入序列UId"-->
        <!--          clearable-->
        <!--          size="small"-->
        <!--          @keyup.enter.native="handleQuery"/>-->
        <!--      </el-form-item>-->
        <el-form-item label="拍摄时间" prop="studyDate">
          <el-input
            v-model="queryParams.studyDate"
            placeholder="请输入ct拍摄时间"
            clearable
            size="small"
            @keyup.enter.native="handleQuery"/>
        </el-form-item>
        <!--      <el-form-item label="身份证号" prop="patCardId">-->
        <!--        <el-input-->
        <!--          v-model="queryParams.patCardId"-->
        <!--          placeholder="请输入身份证号"-->
        <!--          clearable-->
        <!--          size="small"-->
        <!--          @keyup.enter.native="handleQuery"/>-->
        <!--      </el-form-item>-->
        <!--      <el-form-item label="病人姓名" prop="patientName">-->
        <!--        <el-input-->
        <!--          v-model="queryParams.patientName"-->
        <!--          placeholder="请输入病人姓名"-->
        <!--          clearable-->
        <!--          size="small"-->
        <!--          @keyup.enter.native="handleQuery"/>-->
        <!--      </el-form-item>-->
        <el-form-item label="标记医生" prop="makerDoctor">
          <el-input
            v-model="queryParams.makerDoctor"
            placeholder="请输入标记医生"
            clearable
            size="small"
            @keyup.enter.native="handleQuery"/>
        </el-form-item>
        <el-form-item label="医院名" prop="makerEnterpriseName">
          <el-input
            v-model="queryParams.makerEnterpriseName"
            placeholder="请输入医院名"
            clearable
            size="small"
            @keyup.enter.native="handleQuery"/>
        </el-form-item>
        <el-form-item label="标记时间" prop="makerTime">
          <el-input
            v-model="queryParams.makerTime"
            placeholder="请输入标记时间"
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
        <!--      <el-col :span="1.5">-->
        <!--        <el-button-->
        <!--          type="primary"-->
        <!--          plain-->
        <!--          icon="el-icon-plus"-->
        <!--          size="mini"-->
        <!--          @click="handleAdd"-->
        <!--          v-hasPermi="['ct:maker:add']"-->
        <!--        >新增</el-button>-->
        <!--      </el-col>-->
        <el-col :span="1.5">
          <el-button
            type="primary"
            plain
            size="mini"
            @click="returnRoute"
          >返回
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
            v-hasPermi="['ct:maker:edit']"
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
            v-hasPermi="['ct:maker:remove']"
          >删除
          </el-button>
        </el-col>
        <!--        <el-col :span="1.5">-->
        <!--          <el-button-->
        <!--            type="warning"-->
        <!--            plain-->
        <!--            icon="el-icon-download"-->
        <!--            size="mini"-->
        <!--            @click="handleExport"-->
        <!--            v-hasPermi="['ct:maker:export']"-->
        <!--          >导出-->
        <!--          </el-button>-->
        <!--        </el-col>-->

        <el-col :span="1.5">
          <el-button
            type="warning"
            plain
            icon="el-icon-sort"
            size="mini"
            @click="handleSort"
            v-show="sortVisible"
            v-hasPermi="['ct:maker:edit']"
          >保存排序
          </el-button>
        </el-col>


        <right-toolbar :showSearch.sync="showSearch" @controlSortable="handleSortable" @queryTable="getList"
                       :columns="columns"/>
      </el-row>

      <el-table v-loading="loading" :data="makerList" @selection-change="handleSelectionChange" ref="dataTable"
                row-key="dicomMakerId">
        <el-table-column type="selection" width="55" align="center" class-name="allowDrag"/>
        <el-table-column label="序号" align="center" min-width="70" class-name="allowDrag" v-if="columns[0].visible">
          <template slot-scope="scope">
            <span>{{ queryParams.pageSize * (queryParams.pageNum - 1) + scope.$index + 1 }}</span>
          </template>
        </el-table-column>
        <el-table-column label="instanceID" align="center" key="instanceUid" prop="instanceUid" min-width="120"
                         class-name="allowDrag" v-if="columns[1].visible"/>
        <el-table-column label="研究id" align="center" key="studyUid" prop="studyUid" min-width="120"
                         class-name="allowDrag" v-if="columns[2].visible"/>
        <el-table-column label="序列UId" align="center" key="seriesUid" prop="seriesUid" min-width="120"
                         class-name="allowDrag" v-if="columns[3].visible"/>
        <el-table-column label="ct拍摄时间" align="center" key="studyDate" prop="studyDate" min-width="120"
                         class-name="allowDrag" v-if="columns[4].visible"/>
        <el-table-column label="身份证号" align="center" key="patCardId" prop="patCardId" min-width="120"
                         class-name="allowDrag" v-if="columns[5].visible"/>
        <el-table-column label="病人姓名" align="center" key="patientName" prop="patientName" min-width="120"
                         class-name="allowDrag" v-if="columns[6].visible"/>
        <el-table-column label="标记医生" align="center" key="makerDoctor" prop="makerDoctor" min-width="120"
                         class-name="allowDrag" v-if="columns[7].visible"/>
        <el-table-column label="医院名" align="center" key="makerEnterpriseName" prop="makerEnterpriseName"
                         min-width="120" class-name="allowDrag" v-if="columns[8].visible"/>
        <el-table-column label="标记时间" align="center" key="makerTime" prop="makerTime" min-width="120"
                         class-name="allowDrag" v-if="columns[9].visible"/>
        <el-table-column label="标记图像地址" align="center" key="makerImageAddress" prop="makerImageAddress"
                         min-width="120" class-name="allowDrag" v-if="columns[10].visible"/>
        <el-table-column label="备注" align="center" key="makerDescription" prop="makerDescription" min-width="120"
                         class-name="allowDrag" v-if="columns[11].visible"/>
        <el-table-column label="操作" align="center" min-width="160" class-name="small-padding fixed-width allowDrag">
          <template slot-scope="scope">
            <el-button
              size="mini"
              type="text"
              icon="el-icon-edit"
              @click="viewMakerImage(scope.row)"
              v-hasPermi="['ct:maker:edit']"
            >阅片
            </el-button>
            <el-button
              size="mini"
              type="text"
              icon="el-icon-edit"
              @click="handleUpdate(scope.row)"
              v-hasPermi="['ct:maker:edit']"
            >修改
            </el-button>
            <el-button
              size="mini"
              type="text"
              icon="el-icon-delete"
              @click="handleDelete(scope.row)"
              v-hasPermi="['ct:maker:remove']"
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

    <!-- 添加或修改病人标记过的dicom图像对话框 -->
    <el-dialog :title="title" :visible.sync="open" width="600px" append-to-body v-dialogDrag v-dialogDragHeight>
      <el-form ref="form" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="单张图像instanceID" prop="instanceUid">
          <el-input disabled v-model="form.instanceUid" placeholder="请输入单张图像instanceID"/>
        </el-form-item>
        <el-form-item label="研究id" prop="studyUid">
          <el-input disabled v-model="form.studyUid" placeholder="请输入研究id"/>
        </el-form-item>
        <el-form-item label="序列UId" prop="seriesUid">
          <el-input disabled v-model="form.seriesUid" placeholder="请输入序列UId"/>
        </el-form-item>
        <el-form-item label="ct拍摄时间" prop="studyDate">
          <el-input disabled v-model="form.studyDate" placeholder="请输入ct拍摄时间"/>
        </el-form-item>
        <el-form-item label="身份证号" prop="patCardId">
          <el-input disabled v-model="form.patCardId" placeholder="请输入身份证号"/>
        </el-form-item>
        <el-form-item label="病人姓名" prop="patientName">
          <el-input disabled v-model="form.patientName" placeholder="请输入病人姓名"/>
        </el-form-item>
        <el-form-item label="标记医生" prop="makerDoctor">
          <el-input disabled v-model="form.makerDoctor" placeholder="请输入标记医生"/>
        </el-form-item>
        <el-form-item label="医院名" prop="makerEnterpriseName">
          <el-input disabled v-model="form.makerEnterpriseName" placeholder="请输入医院名"/>
        </el-form-item>
        <el-form-item label="标记时间" prop="makerTime">
          <el-input disabled v-model="form.makerTime" placeholder="请输入标记时间"/>
        </el-form-item>
        <el-form-item label="标记图像地址" prop="makerImageAddress">
          <el-input disabled v-model="form.makerImageAddress" type="textarea" placeholder="请输入内容"/>
        </el-form-item>
        <el-form-item label="备注" prop="makerDescription">
          <el-input v-model="form.makerDescription" type="textarea" placeholder="请输入内容"/>
        </el-form-item>
        <!--        <el-form-item  label="用来存储图像元数据，临时用" prop="makerImage">-->
        <!--          <el-input disabled v-model="form.makerImage" placeholder="请输入用来存储图像元数据，临时用" />-->
        <!--        </el-form-item>-->
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button type="primary" :loading="submitLoading" @click="submitForm">确 定</el-button>
        <el-button @click="cancel">取 消</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import {listMaker, getMaker, addMaker, updateMaker, updateMakerSort} from "../../api/ct/maker";
import Sortable from "sortablejs";
import {mapActions} from "vuex";
import {delMakerAndImage} from "./maker";

export default {
  name: "maker",
  data() {
    return {
      // 遮罩层
      loading: true,
      // 提交状态
      submitLoading: false,
      // 选中数组
      ids: [],
      imageAddresses: [],
      // 非单个禁用
      single: true,
      // 非多个禁用
      multiple: true,
      // 显示搜索条件
      showSearch: true,
      // 总条数
      total: 0,
      // 病人标记过的dicom图像表格数据
      makerList: [],


      // 病人标记过的dicom图像表格原始数据
      oldMakerList: [],
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
        pageSize: 10,
        instanceUid: null,

        studyUid: null,

        seriesUid: null,

        studyDate: null,

        patCardId: null,

        patientName: null,

        makerDoctor: null,

        makerEnterpriseName: null,

        makerTime: null,

        makerImageAddress: null,

        makerDescription: null,

      },
      // 列信息
      columns: [
        {key: 0, label: `序号`, visible: true},
        {key: 1, label: `instanceID`, visible: true},

        {key: 2, label: `研究id`, visible: false},

        {key: 3, label: `序列UId`, visible: false},

        {key: 4, label: `ct拍摄时间`, visible: true},

        {key: 5, label: `身份证号`, visible: true},

        {key: 6, label: `病人姓名`, visible: true},

        {key: 7, label: `标记医生`, visible: true},

        {key: 8, label: `医院名`, visible: false},

        {key: 9, label: `标记时间`, visible: false},

        {key: 10, label: `标记图像地址`, visible: false},

        {key: 11, label: `备注`, visible: true},


      ],
      // 表单参数
      form: {},
      // 表单校验
      rules: {
        instanceUid: [
          {required: true, message: "单张图像instanceID不能为空", trigger: "blur"}
        ],

      }
    };
  },
  created() {
    this.getList();
  },
  activated() {
    this.getList();
  },

  methods: {
    ...mapActions(['updateMakerImageList', 'makerImageInitInfo']),
    viewMakerImage(row) {
      //将需要查看的病人patCardId，存储起来
      this.makerImageInitInfo(row)
      console.log(row)
      this.$router.push({name: 'makerImage'})
    },
    /** 删除按钮操作 */
    handleDelete(row) {
      let that = this;
      const dicomMakerIds = row.dicomMakerId || that.ids;
      let dicomMakerImageList = []
      if (that.imageAddresses.length > 0) {
        dicomMakerImageList = that.imageAddresses
      } else {
        dicomMakerImageList.push(row.makerImageAddress)
      }
      this.$modal.confirm('是否确认删除病人标记过的dicom图像,编号为"' + dicomMakerIds + '"的数据项?').then(function () {
        let idsOfMe = that.updateParamIds(dicomMakerIds)
        return delMakerAndImage(idsOfMe, dicomMakerImageList)
      }).then(() => {
        setTimeout(() => {
          this.getList();
          this.$modal.msgSuccess("删除成功");
        }, 300)
      }).catch(() => {
      });
    },
    /** 查询病人标记过的dicom图像列表 */
    getList() {
      let that = this
      that.loading = true;
      that.queryParams.patCardId = this.$store.getters.makerOfPatCardId
      listMaker(this.queryParams).then(response => {
        that.makerList = response.data.items;
        that.total = response.data.total;
        that.loading = false;
        that.updateMakerImageList(this.makerList)
      });
    },
    // 取消按钮
    cancel() {
      this.open = false;
      this.reset();
    },
    returnRoute() {
      this.$router.back()
    },
    // 表单重置
    reset() {
      this.form = {
        dicomMakerId: null,

        instanceUid: null,

        studyUid: null,

        seriesUid: null,

        studyDate: null,

        patCardId: null,

        patientName: null,

        makerDoctor: null,

        makerEnterpriseName: null,

        makerTime: null,

        makerImageAddress: null,

        makerDescription: null,

        makerImage: null,

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
      this.imageAddresses = selection.map(item => item.makerImageAddress)
      this.ids = selection.map(item => item.dicomMakerId)
      this.single = selection.length !== 1
      this.multiple = !selection.length
    },
    /** 新增按钮操作 */
    handleAdd() {
      this.reset();
      this.open = true;
      this.title = "添加病人标记过的dicom图像";
    },
    /** 修改按钮操作 */
    handleUpdate(row) {
      this.reset();
      const dicomMakerId = row.dicomMakerId || this.ids[0]
      getMaker({dicomMakerId: dicomMakerId}).then(response => {
        this.form = response.data;
        this.open = true;
        this.title = "修改病人标记过的dicom图像";
      });
    },
    /** 提交按钮 */
    submitForm() {
      this.submitLoading = true;
      this.$refs["form"].validate(valid => {
        if (valid) {
          if (this.form.dicomMakerId != null) {
            updateMaker(this.form).then(response => {
              this.$modal.msgSuccess("修改成功");
              this.open = false;
              this.getList();
            }).catch(() => {
              this.submitLoading = false
            });
          } else {
            addMaker(this.form).then(response => {
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

    /** 导出按钮操作 */
    handleExport() {
      this.download('ct/maker/export', {
        ...this.queryParams
      }, `病人标记过的dicom图像_${new Date().getTime()}数据.xlsx`)
    }


    ,
    /** 保存排序按钮操作 */
    handleSort() {
      this.$modal.confirm('是否确认保存新排序?').then(() => {
        let params = this.sortOrderListOnlyDynamic(this.makerList, this.oldMakerList, "dicomMakerId");
        if (params.length > 0) {
          return updateMakerSort(this.updateParamIds(params));
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
            const targetRow = this.makerList.splice(evt.oldIndex, 1)[0];
            this.makerList.splice(evt.newIndex, 0, targetRow);
            this.sortVisible = true
          }
        })
      }
    }
  },
  mounted() {
    this.handleSortable(false);
  }


}
</script>


<style lang="scss" scoped>
::v-deep .allowDrag {
  font-size: 10px;
  //background-color: #282c34 !important;
  //color: white !important;
  //border-bottom-color: #ea768b;
}
</style>
