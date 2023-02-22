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
        <el-form-item label="ct拍摄时间" prop="dicomCtTime">
          <el-input
            v-model="queryParams.dicomCtTime"
            placeholder="请输入ct拍摄时间"
            clearable
            size="small"
            @keyup.enter.native="handleQuery"/>
        </el-form-item>
        <el-form-item label="研究UId" prop="dicomCtStudyUid">
          <el-input
            v-model="queryParams.dicomCtStudyUid"
            placeholder="请输入研究UId"
            clearable
            size="small"
            @keyup.enter.native="handleQuery"/>
        </el-form-item>
        <el-form-item label="序列UId" prop="dicomCtSeriesUid">
          <el-input
            v-model="queryParams.dicomCtSeriesUid"
            placeholder="请输入序列UId"
            clearable
            size="small"
            @keyup.enter.native="handleQuery"/>
        </el-form-item>
        <el-form-item label="检查的身体部位" prop="dicomCtBody">
          <el-input
            v-model="queryParams.dicomCtBody"
            placeholder="请输入检查的身体部位"
            clearable
            size="small"
            @keyup.enter.native="handleQuery"/>
        </el-form-item>
        <el-form-item label="序列第一张的存储地址" prop="dicomCtPath">
          <el-input
            v-model="queryParams.dicomCtPath"
            placeholder="请输入序列第一张的存储地址"
            clearable
            size="small"
            @keyup.enter.native="handleQuery"/>
        </el-form-item>
        <el-form-item label="一个序列的dicom数量" prop="dicomCtCount">
          <el-input
            v-model="queryParams.dicomCtCount"
            placeholder="请输入一个序列的dicom数量"
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
            v-hasPermi="['dicom:dicom:add']"
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
            v-hasPermi="['dicom:dicom:edit']"
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
            v-hasPermi="['dicom:dicom:remove']"
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
            v-hasPermi="['dicom:dicom:export']"
          >导出
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
            v-hasPermi="['dicom:dicom:edit']"
          >保存排序
          </el-button>
        </el-col>


        <right-toolbar :showSearch.sync="showSearch" @controlSortable="handleSortable" @queryTable="getList"
                       :columns="columns"/>
      </el-row>

      <el-table v-loading="loading" :data="dicomList" @selection-change="handleSelectionChange" ref="dataTable"
                row-key="dicomId">
        <el-table-column type="selection" width="55" align="center" class-name="allowDrag"/>
        <el-table-column label="序号" align="center" min-width="70" class-name="allowDrag" v-if="columns[0].visible">
          <template slot-scope="scope">
            <span>{{ queryParams.pageSize * (queryParams.pageNum - 1) + scope.$index + 1 }}</span>
          </template>
        </el-table-column>
        <el-table-column label="身份证号" align="center" key="patCardId" prop="patCardId" min-width="120"
                         class-name="allowDrag" v-if="columns[1].visible"/>
        <el-table-column label="ct拍摄时间" align="center" key="dicomCtTime" prop="dicomCtTime" min-width="120"
                         class-name="allowDrag" v-if="columns[2].visible"/>
        <el-table-column label="研究UId" align="center" key="dicomCtStudyUid" prop="dicomCtStudyUid" min-width="120"
                         class-name="allowDrag" v-if="columns[3].visible"/>
        <el-table-column label="序列UId" align="center" key="dicomCtSeriesUid" prop="dicomCtSeriesUid" min-width="120"
                         class-name="allowDrag" v-if="columns[4].visible"/>
        <el-table-column label="检查的身体部位" align="center" key="dicomCtBody" prop="dicomCtBody" min-width="120"
                         class-name="allowDrag" v-if="columns[5].visible"/>
        <el-table-column label="序列第一张的存储地址" align="center" key="dicomCtPath" prop="dicomCtPath" min-width="120"
                         class-name="allowDrag" v-if="columns[6].visible"/>
        <el-table-column label="一个序列的dicom数量" align="center" key="dicomCtCount" prop="dicomCtCount" min-width="120"
                         class-name="allowDrag" v-if="columns[7].visible"/>
        <el-table-column label="操作" align="center" min-width="120" class-name="small-padding fixed-width allowDrag">
          <template slot-scope="scope">
            <el-button
              size="mini"
              type="text"
              icon="el-icon-edit"
              @click="handleUpdate(scope.row)"
              v-hasPermi="['dicom:dicom:edit']"
            >修改
            </el-button>
            <el-button
              size="mini"
              type="text"
              icon="el-icon-delete"
              @click="handleDelete(scope.row)"
              v-hasPermi="['dicom:dicom:remove']"
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

    <!-- 添加或修改病人dicom存储记录对话框 -->
    <el-dialog :title="title" :visible.sync="open" width="600px" append-to-body v-dialogDrag v-dialogDragHeight>
      <el-form ref="form" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="身份证号" prop="patCardId">
          <el-input v-model="form.patCardId" placeholder="请输入身份证号"/>
        </el-form-item>
        <el-form-item label="ct拍摄时间" prop="dicomCtTime">
          <el-input v-model="form.dicomCtTime" placeholder="请输入ct拍摄时间"/>
        </el-form-item>
        <el-form-item label="研究UId" prop="dicomCtStudyUid">
          <el-input v-model="form.dicomCtStudyUid" placeholder="请输入研究UId"/>
        </el-form-item>
        <el-form-item label="序列UId" prop="dicomCtSeriesUid">
          <el-input v-model="form.dicomCtSeriesUid" placeholder="请输入序列UId"/>
        </el-form-item>
        <el-form-item label="检查的身体部位" prop="dicomCtBody">
          <el-input v-model="form.dicomCtBody" placeholder="请输入检查的身体部位"/>
        </el-form-item>
        <el-form-item label="序列第一张的存储地址" prop="dicomCtPath">
          <el-input v-model="form.dicomCtPath" placeholder="请输入序列第一张的存储地址"/>
        </el-form-item>
        <el-form-item label="一个序列的dicom数量" prop="dicomCtCount">
          <el-input v-model="form.dicomCtCount" placeholder="请输入一个序列的dicom数量"/>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button type="primary" :loading="submitLoading" @click="submitForm">确 定</el-button>
        <el-button @click="cancel">取 消</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import {listDicom, getDicom, delDicom, addDicom, updateDicom, updateDicomSort} from "@/api/ct/dicom";
import Sortable from "sortablejs";

export default {
  name: "Dicom",
  data() {
    return {
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
      // 病人dicom存储记录表格数据
      dicomList: [],


      // 病人dicom存储记录表格原始数据
      oldDicomList: [],
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
        patCardId: null,

        dicomCtTime: null,

        dicomCtStudyUid: null,

        dicomCtSeriesUid: null,

        dicomCtBody: null,

        dicomCtPath: null,

        dicomCtCount: null,

      },
      // 列信息
      columns: [
        {key: 0, label: `序号`, visible: true},
        {key: 1, label: `身份证号`, visible: true},

        {key: 2, label: `ct拍摄时间`, visible: true},

        {key: 3, label: `研究UId`, visible: true},

        {key: 4, label: `序列UId`, visible: true},

        {key: 5, label: `检查的身体部位`, visible: true},

        {key: 6, label: `序列第一张的存储地址`, visible: true},

        {key: 7, label: `一个序列的dicom数量`, visible: true},


      ],
      // 表单参数
      form: {},
      // 表单校验
      rules: {
        patCardId: [
          {required: true, message: "身份证号不能为空", trigger: "blur"}
        ],

      }
    };
  },
  created() {
    this.getList();
  },
  methods: {
    /** 查询病人dicom存储记录列表 */
    getList() {
      this.loading = true;
      listDicom(this.queryParams).then(response => {
        this.dicomList = response.data.items;
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
        dicomId: null,

        patCardId: null,

        dicomCtTime: null,

        dicomCtStudyUid: null,

        dicomCtSeriesUid: null,

        dicomCtBody: null,

        dicomCtPath: null,

        dicomCtCount: null,

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
      this.ids = selection.map(item => item.dicomId)
      this.single = selection.length !== 1
      this.multiple = !selection.length
    },
    /** 新增按钮操作 */
    handleAdd() {
      this.reset();
      this.open = true;
      this.title = "添加病人dicom存储记录";
    },
    /** 修改按钮操作 */
    handleUpdate(row) {
      this.reset();
      const dicomId = row.dicomId || this.ids[0]
      getDicom({dicomId: dicomId}).then(response => {
        this.form = response.data;
        this.open = true;
        this.title = "修改病人dicom存储记录";
      });
    },
    /** 提交按钮 */
    submitForm() {
      this.submitLoading = true;
      this.$refs["form"].validate(valid => {
        if (valid) {
          if (this.form.dicomId != null) {
            updateDicom(this.form).then(response => {
              this.$modal.msgSuccess("修改成功");
              this.open = false;
              this.getList();
            }).catch(() => {
              this.submitLoading = false
            });
          } else {
            addDicom(this.form).then(response => {
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
      const dicomIds = row.dicomId || this.ids;
      let that = this;
      this.$modal.confirm('是否确认删除病人dicom存储记录编号为"' + dicomIds + '"的数据项?').then(function () {
        return delDicom(that.updateParamIds(dicomIds));
      }).then(() => {
        this.getList();
        this.$modal.msgSuccess("删除成功");
      }).catch(() => {
      });
    },
    /** 导出按钮操作 */
    handleExport() {
      this.download('dicom/dicom/export', {
        ...this.queryParams
      }, `病人dicom存储记录_${new Date().getTime()}数据.xlsx`)
    }


    ,
    /** 保存排序按钮操作 */
    handleSort() {
      this.$modal.confirm('是否确认保存新排序?').then(() => {
        let params = this.sortOrderListOnlyDynamic(this.dicomList, this.oldDicomList, "dicomId");
        if (params.length > 0) {
          return updateDicomSort(this.updateParamIds(params));
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
            const targetRow = this.dicomList.splice(evt.oldIndex, 1)[0];
            this.dicomList.splice(evt.newIndex, 0, targetRow);
            this.sortVisible = true
          }
        })
      }
    }


  }


  ,
  mounted() {
    this.handleSortable(false);
  }


}
</script>
