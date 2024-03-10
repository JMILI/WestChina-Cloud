<template>
  <div class="app-container">
    <div class="wrapper-container" v-show="showSearch">
      <el-form :model="queryParams" ref="queryForm" :inline="true" label-width="68px">
        <el-form-item label="桶名" prop="bucketName">
          <el-input
            v-model="queryParams.bucketName"
            placeholder="请输入桶名"
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
            v-hasPermi="['tenant:bucket:add']"
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
            v-hasPermi="['tenant:bucket:edit']"
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
            v-hasPermi="['tenant:bucket:remove']"
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
            v-hasPermi="['tenant:bucket:export']"
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
            v-hasPermi="['tenant:bucket:edit']"
          >保存排序
          </el-button>
        </el-col>


        <right-toolbar :showSearch.sync="showSearch" @controlSortable="handleSortable" @queryTable="getList"
                       :columns="columns"/>
      </el-row>

      <el-table v-loading="loading" :data="bucketList" @selection-change="handleSelectionChange" ref="dataTable"
                row-key="bucketId">
        <el-table-column type="selection" width="55" align="center" class-name="allowDrag"/>
        <el-table-column label="序号" align="center" min-width="70" class-name="allowDrag" v-if="columns[0].visible">
          <template slot-scope="scope">
            <span>{{ queryParams.pageSize * (queryParams.pageNum - 1) + scope.$index + 1 }}</span>
          </template>
        </el-table-column>
        <el-table-column label="桶名" align="center" key="bucketName" prop="bucketName" min-width="120"
                         class-name="allowDrag" v-if="columns[1].visible"/>
        <el-table-column label="桶所属的租户" align="center" key="bucketTenantId" prop="bucketTenantId" min-width="120"
                         class-name="allowDrag" v-if="columns[2].visible"/>
        <el-table-column label="桶所属的租户名" align="center" key="bucketTenantName" prop="bucketTenantName" min-width="120"
                         class-name="allowDrag" v-if="columns[3].visible"/>
        <el-table-column label="状态"
                         align="center"
                         prop="status"
                         class-name="allowDrag"
                         min-width="120"
                         v-if="columns[4].visible"
        >
          <template slot-scope="scope">
            <el-switch
              v-model="scope.row.status"
              :active-value="STATUS.NORMAL"
              :inactive-value="STATUS.DISABLE"
              @change="handleStatusChange(scope.row)"
              :disabled="scope.row.isChange === SYSTEM_DEFAULT.TRUE"
            ></el-switch>
          </template>
        </el-table-column>

<!--        <el-table-column label="状态" align="center" key="status" prop="status"-->
<!--                         min-width="120" class-name="allowDrag"-->
<!--                         v-if="columns[4].visible"/>-->

        <el-table-column label="操作" align="center" min-width="120" class-name="small-padding fixed-width allowDrag">
          <template slot-scope="scope">
            <el-button
              size="mini"
              type="text"
              icon="el-icon-edit"
              @click="handleUpdate(scope.row)"
              v-hasPermi="['tenant:bucket:edit']"
            >修改
            </el-button>
            <el-button
              size="mini"
              type="text"
              icon="el-icon-delete"
              @click="handleDelete(scope.row)"
              v-hasPermi="['tenant:bucket:remove']"
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

    <!-- 添加或修改对象存储，存储租户的桶信息对话框 -->
    <el-dialog :title="title" :visible.sync="open" width="600px" append-to-body v-dialogDrag v-dialogDragHeight>
      <el-form ref="form" :model="form" :rules="rules" label-width="80px">

        <el-form-item label="桶名" prop="bucketName">
          <el-input v-model="form.bucketName" placeholder="请输入桶名"/>
        </el-form-item>
        <el-form-item label="租户名" prop="bucketTenantName">
          <el-select v-model="form.bucketTenantName" placeholder="请选择租户名" :style="{width: '100%'}"
                     @change='getNameValue(form.bucketTenantName)'>
            <el-option v-for="(item, index) in bucketTenantNameOptions" :key="index" :label="item.label"
                       :value="item.value" :disabled="item.disabled"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="租户id" prop="bucketTenantId">
          <el-select v-model="form.bucketTenantId" placeholder="请选择租户id" :style="{width: '100%'}"
                     @change='getIdValue(form.bucketTenantId)'>
            <el-option v-for="(item, index) in bucketTenantIdOptions" :key="index" :label="item.label"
                       :value="item.value" :disabled="item.disabled"></el-option>
          </el-select>
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
import {listBucket, getBucket, delBucket, addBucket, updateBucket, updateBucketSort} from "@/api/tenant/bucket";
import Sortable from "sortablejs";
import {listTenant, updateTenant} from "@/api/tenant/tenant";
import {STATUS, STATUS_UPDATE_OPERATION, SYSTEM_DEFAULT} from "common/src/constant/constants";

export default {
  name: "Bucket",
  data() {
    return {
      SYSTEM_DEFAULT: SYSTEM_DEFAULT,
      STATUS: STATUS,
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
      // 对象存储，存储租户的桶信息表格数据
      bucketList: [],
      tenantList: [],

      // 对象存储，存储租户的桶信息表格原始数据
      oldBucketList: [],
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
        bucketName: null,

        bucketTenantId: null,

        bucketTenantName: null,

        status: null,

      },
      queryParamsTenant: {
        pageNum: 1,
        pageSize: 1000,
        tenantId: null,
        tenantName: null,
        tenantSystemName: null,
        tenantNick: null,
        status: null
      },
      // 列信息
      columns: [
        {key: 0, label: `序号`, visible: true},
        {key: 1, label: `桶名`, visible: true},

        {key: 2, label: `桶所属的租户`, visible: true},

        {key: 3, label: `桶所属的租户名`, visible: true},

        {key: 4, label: `状态`, visible: true},


      ],
      // 表单参数
      form: {
        bucketName: null,
        bucketTenantId: null,
        bucketTenantName: null,
      },
      // 表单校验
      rules: {
        bucketName: [
          {required: true, message: "桶名不能为空", trigger: "blur"},
          {
            validator: function (rule, value, callback) {
              if (/[a-zA-z]$/.test(value) == false) {
                callback(new Error("请输入英文"));
              } else {
                //校验通过
                callback();
              }
            },
            trigger: "blur"
          }
        ],
        bucketTenantName: [{
          required: true,
          message: '请选择租户名',
          trigger: 'change'
        }],
        bucketTenantId: [{
          required: true,
          message: '请选择租户id',
          trigger: 'change'
        }],
      },
      bucketTenantNameOptions: [],
      bucketTenantIdOptions: [],
    };
  },
  created() {
    this.getList();
    //监视窗口，如果窗口关闭了，就清空数据
    this.$watch("open", function (newValue, oldValue) {
      if (this.open == false) {
        this.reset();
        this.bucketTenantNameOptions = []
        this.bucketTenantIdOptions = []
      }
    })

  },
  methods: {
    /** 查询对象存储，存储租户的桶信息列表 */
    getList() {
      this.loading = true;
      listBucket(this.queryParams).then(response => {
        this.bucketList = response.data.items;
        this.total = response.data.total;
        this.loading = false;
      });
    },
    getIdValue(bucketTenantId) {
      let that = this;
      this.bucketTenantIdOptions.forEach(item => {
        if (item.value === bucketTenantId) {
          that.form.bucketTenantName = item.idName;
        }
      })

    },
    getNameValue(bucketTenantName) {
      let that = this;
      that.bucketTenantNameOptions.forEach(item => {
        if (item.value === bucketTenantName) {
          that.form.bucketTenantId = item.idName;
        }
      })
    },
    /** 修改状态按钮操作 */
    handleStatusChange(row) {
      console.log("row",row)
      let msg = row.status === STATUS.NORMAL ? "启用" : "停用"
      updateBucket({
        bucketId: row.bucketId,
        bucketName: row.bucketName,
        bucketTenantId: row.bucketTenantId,
        bucketTenantName: row.bucketTenantName,
        status: row.status,
        updateType: STATUS_UPDATE_OPERATION
      }).then(response => {
        this.$modal.msgSuccess(msg + "状态修改成功")
      }).catch(() => {
        this.$modal.msgSuccess(msg + "失败")
        row.status = row.status === STATUS.NORMAL ? STATUS.DISABLE : STATUS.NORMAL
      })
    },
    // 取消按钮
    cancel() {
      this.open = false;
      this.reset();
    },
    // 表单重置
    reset() {
      this.form = {
        bucketId: null,

        bucketName: null,

        bucketTenantId: null,

        bucketTenantName: null,

        status: "0",

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
      this.ids = selection.map(item => item.bucketId)
      this.single = selection.length !== 1
      this.multiple = !selection.length
    },
    /** 新增按钮操作 */
    handleAdd() {
      listTenant(this.queryParamsTenant).then(response => {
        this.tenantList = response.data.items
        this.tenantList.forEach(item => {
          let temp = {}
          temp.label = item.tenantName
          temp.value = item.tenantName
          temp.idName = item.tenantId
          temp.id = item.tenantId
          this.bucketTenantNameOptions.push(temp)
          let tempId = {}
          tempId.label = item.tenantId
          tempId.value = item.tenantId
          tempId.idName = item.tenantName
          this.bucketTenantIdOptions.push(tempId)
        })
        this.loading = false
      })
      this.reset();
      this.open = true;
      this.title = "添加对象存储，存储租户的桶信息";
      //查询现有的租户，必须现有租户，才能创建minio桶
    },
    /** 修改按钮操作 */
    handleUpdate(row) {
      this.reset();
      const bucketId = row.bucketId || this.ids[0]
      getBucket({bucketId: bucketId}).then(response => {
        this.form = response.data;
        this.open = true;
        this.title = "修改对象存储，存储租户的桶信息";
      });
    },
    /** 提交按钮 */
    submitForm() {
      this.submitLoading = true;
      this.$refs["form"].validate(valid => {
        if (valid) {
          if (this.form.bucketId != null) {
            updateBucket(this.form).then(response => {
              this.$modal.msgSuccess("修改成功");
              this.open = false;
              this.getList();
            }).catch(() => {
              this.submitLoading = false
            });
          } else {
            addBucket(this.form).then(response => {
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
      const bucketIds = row.bucketId || this.ids;
      let that = this;
      this.$modal.confirm('是否确认删除对象存储，存储租户的桶信息编号为"' + bucketIds + '"的数据项?').then(function () {
        return delBucket(that.updateParamIds(bucketIds));
      }).then(() => {
        this.getList();
        this.$modal.msgSuccess("删除成功");
      }).catch(() => {
      });
    },
    /** 导出按钮操作 */
    handleExport() {
      this.download('tenant/bucket/export', {
        ...this.queryParams
      }, `对象存储，存储租户的桶信息_${new Date().getTime()}数据.xlsx`)
    }


    ,
    /** 保存排序按钮操作 */
    handleSort() {
      this.$modal.confirm('是否确认保存新排序?').then(() => {
        let params = this.sortOrderListOnlyDynamic(this.bucketList, this.oldBucketList, "bucketId");
        if (params.length > 0) {
          return updateBucketSort(this.updateParamIds(params));
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
            const targetRow = this.bucketList.splice(evt.oldIndex, 1)[0];
            this.bucketList.splice(evt.newIndex, 0, targetRow);
            this.sortVisible = true
          }
        })
      }
    }
  },
  mounted() {
    this.handleSortable(false);
  },


}
</script>
