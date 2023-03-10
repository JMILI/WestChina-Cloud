<template>
  <div class="app-container">
    <div class="wrapper-container" v-show="showSearch">
      <el-form :model="queryParams" ref="queryForm" :inline="true" label-width="68px">
        <el-form-item label="策略名称" prop="name">
          <el-input
            v-model="queryParams.name"
            placeholder="请输入策略名称"
            clearable
            size="small"
            @keyup.enter.native="handleQuery"
          />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="queryParams.status" placeholder="请选择状态" clearable size="small">
            <el-option
              v-for="dict in dict.type.sys_normal_disable"
              :key="dict.value"
              :label="dict.label"
              :value="dict.value"
            />
          </el-select>
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
            v-hasPermi="['tenant:strategy:add']"
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
            v-hasPermi="['tenant:strategy:edit']"
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
            v-hasPermi="['tenant:strategy:remove']"
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
            v-hasPermi="['tenant:strategy:export']"
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
            v-hasPermi="['tenant:strategy:edit']"
          >保存排序
          </el-button>
        </el-col>
        <right-toolbar :showSearch.sync="showSearch" @controlSortable="handleSortable" @queryTable="getList"/>
      </el-row>

      <el-table v-loading="loading" :data="strategyList" @selection-change="handleSelectionChange" ref="dataTable"
                row-key="strategyId">
        <el-table-column type="selection" width="55" align="center" class-name="allowDrag"/>
        <el-table-column label="序号" align="center" class-name="allowDrag" min-width="120">
          <template slot-scope="scope">
            <span>{{ queryParams.pageSize * (queryParams.pageNum - 1) + scope.$index + 1 }}</span>
          </template>
        </el-table-column>
        <el-table-column label="策略名称" align="center" prop="name" class-name="allowDrag" min-width="120"/>
        <el-table-column label="数据源数量" align="center" prop="sourceAmount" class-name="allowDrag" min-width="120">
          <template slot-scope="scope">
            <el-tag>{{ scope.row.sourceAmount }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" align="center" prop="status" class-name="allowDrag" min-width="120">
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
        <el-table-column label="操作" align="center" class-name="small-padding fixed-width allowDrag" min-width="120">
          <template slot-scope="scope">
            <el-button
              size="mini"
              type="text"
              icon="el-icon-edit"
              @click="handleUpdate(scope.row)"
              v-hasPermi="['tenant:strategy:edit']"
            >修改
            </el-button>
            <el-button
              size="mini"
              type="text"
              icon="el-icon-delete"
              @click="handleDelete(scope.row)"
              v-hasPermi="['tenant:strategy:remove']"
              v-if="scope.row.isChange === SYSTEM_DEFAULT.FALSE"
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

    <!-- 添加或修改数据源策略对话框 -->
    <el-dialog :title="title" :visible.sync="open" width="600px" append-to-body v-dialogDrag v-dialogDragHeight>
      <el-form ref="form" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="策略名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入内容"/>
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio
              v-for="dict in dict.type.sys_normal_disable"
              :key="dict.value"
              :label="dict.value"
            >{{ dict.label }}
            </el-radio>
          </el-radio-group>
        </el-form-item>
        <el-divider content-position="center">数据源信息</el-divider>
        <div class="value-set">
          <div class="value-title">数据源：</div>
          <div class="value-add">
            <el-button type="primary" plain @click="valueAdd">添加数据源</el-button>
          </div>
          <el-table :data="form.values">
            <el-table-column label="数据源名称" min-width="40%" align="center">
              <template slot-scope="scope">
                <el-select v-model="scope.row.sourceId" placeholder="请选择" @change="valueChange(scope.row.sourceId)">
                  <el-option
                    v-for="item in containWriteList"
                    :key="item.sourceId"
                    :label="item.name"
                    :value="item.sourceId"
                  >
                  </el-option>
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="主数据源" align="center" min-width="20%" prop="isMain">
              <template slot-scope="scope">
                <el-switch
                  v-model="scope.row.isMain"
                  :active-value="IS_MAIN.TRUE"
                  :inactive-value="IS_MAIN.FALSE"
                  :disabled="form.hasMain === true && scope.row.isMain === IS_MAIN.FALSE"
                  @change="valueMainChange(scope.row.isMain)"
                ></el-switch>
              </template>
            </el-table-column>
            <el-table-column label="数据源状态" align="center" min-width="20%" prop="status">
              <template slot-scope="scope">
                <el-switch
                  v-model="scope.row.status"
                  active-value="0"
                  inactive-value="1"
                  disabled
                ></el-switch>
              </template>
            </el-table-column>
            <el-table-column label="操作" min-width="20%" align="center">
              <template slot-scope="scope">
                <el-button
                  size="mini"
                  type="text"
                  icon="el-icon-delete"
                  @click="valueDelete(scope.row)"
                  v-hasPermi="['tenant:strategy:edit']"
                >删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button type="primary" :loading="submitLoading" @click="submitForm">确 定</el-button>
        <el-button @click="cancel">取 消</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import {
  listStrategy,
  getStrategy,
  delStrategy,
  addStrategy,
  updateStrategy,
  updateStrategySort
} from '@/api/tenant/strategy'
import Sortable from 'sortablejs'
import {writeSeparation} from '@/api/tenant/separation'
import {STATUS, STATUS_UPDATE_OPERATION, SYSTEM_DEFAULT} from "@constant/constants"
import {IS_MAIN} from "@constant/tenantConstants"

export default {
  name: 'Strategy',
  dicts: ['sys_normal_disable'],
  components: {},
  data() {
    return {
      //常量区
      SYSTEM_DEFAULT: SYSTEM_DEFAULT,
      STATUS: STATUS,
      IS_MAIN:IS_MAIN,
      STATUS_UPDATE_OPERATION: STATUS_UPDATE_OPERATION,
      // 遮罩层
      loading: true,
      // 提交状态
      submitLoading: false,
      // 选中数组
      ids: [],
      idNames: [],
      // 非单个禁用
      single: true,
      // 非多个禁用
      multiple: true,
      // 显示搜索条件
      showSearch: true,
      // 总条数
      total: 0,
      // 数据源策略表格数据
      strategyList: [],
      // 数据源策略表格原始数据
      oldStrategyList: [],
      // 排序保存按钮显示
      sortVisible: false,
      // 排序参数
      sortable:null,
      // 具备写 数据源集合
      containWriteList: [],
      // 弹出层标题
      title: '',
      // 是否显示弹出层
      open: false,
      // 查询参数
      queryParams: {
        pageNum: 1,
        pageSize: 10,
        name: null,
        status: null
      },
      // 表单参数
      form: {},
      // 表单校验
      rules: {
        name: [
          {required: true, message: '策略名称不能为空', trigger: 'blur'}
        ]
      }
    }
  },
  created() {
    this.getList()
  },
  methods: {
    /** 查询数据源策略列表 */
    getList() {
      this.loading = true
      listStrategy(this.queryParams).then(response => {
        this.strategyList = response.data.items
        this.total = response.data.total
        this.loading = false
      })
    },
    // 取消按钮
    cancel() {
      this.open = false
      this.reset()
    },
    // 表单重置
    reset() {
      this.form = {
        strategyId: null,
        name: null,
        sourceAmount: 0,
        sort: 0,
        status: STATUS.NORMAL,
        values: [],
        isChange: SYSTEM_DEFAULT.FALSE,
        hasMain: false
      }
      this.resetForm('form')
      this.submitLoading = false
    },
    /** 搜索按钮操作 */
    handleQuery() {
      this.queryParams.pageNum = 1
      this.getList()
    },
    /** 重置按钮操作 */
    resetQuery() {
      this.resetForm('queryForm')
      this.handleQuery()
    },
    // 多选框选中数据
    handleSelectionChange(selection) {
      this.ids = selection.map(item => item.strategyId)
      this.idNames = selection.map(item => item.name)
      this.single = selection.length !== 1
      this.multiple = !selection.length
    },
    getWriteSeparation() {
      writeSeparation().then(response => {
        this.containWriteList = response.data
      })
    },
    /** 新增按钮操作 */
    handleAdd() {
      this.reset()
      this.getWriteSeparation()
      this.open = true
      this.title = '添加数据源策略'
    },
    /** 修改按钮操作 */
    handleUpdate(row) {
      this.reset()
      this.getWriteSeparation()
      const strategyId = row.strategyId || this.ids[0]
      getStrategy({strategyId: strategyId}).then(response => {
        this.form = response.data
        for (let i = 0; i < this.form.values.length; i++) {
          if (this.form.values[i].isMain === IS_MAIN.TRUE) {
            this.form.hasMain = true
          }
        }
        this.open = true
        this.title = '修改数据源策略'
      })
    },
    /** 修改状态按钮操作 */
    handleStatusChange(row) {
      let msg = row.status === STATUS.NORMAL ? "启用" : "停用"
      updateStrategy({strategyId: row.strategyId, isChange: row.isChange, status: row.status, updateType: STATUS_UPDATE_OPERATION}).then(response => {
        this.$modal.msgSuccess(msg + "成功")
      }).catch(() => {
        row.status = row.status === STATUS.NORMAL ? STATUS.DISABLE : STATUS.NORMAL
      })
    },
    /** 提交按钮 */
    submitForm() {
      this.submitLoading = true
      this.$refs['form'].validate(valid => {
        if (valid) {
          if (this.valueCheck()) {
            if (this.form.strategyId != null) {
              if (this.form.isChange === SYSTEM_DEFAULT.FALSE) {
                updateStrategy(this.form).then(response => {
                  this.$modal.msgSuccess('修改成功')
                  this.open = false
                  this.getList()
                }).catch(() => {
                  this.submitLoading = false
                })
              } else {
                this.submitLoading = false
                this.$message({
                  message: '默认数据源不允许进行修改操作',
                  type: 'warning'
                })
              }
            } else {
              addStrategy(this.form).then(response => {
                this.$modal.msgSuccess('新增成功')
                this.open = false
                this.getList()
              }).catch(() => {
                this.submitLoading = false
              })
            }
          }else{
            this.submitLoading = false
          }
        }else{
          this.submitLoading = false
        }
      })
    },
    /** 删除按钮操作 */
    handleDelete(row) {
      const strategyIds = row.strategyId || this.ids
      const names = row.name || this.idNames
      let that = this
      this.$modal.confirm('是否确认删除数据源策略"' + names + '"?').then(function () {
        return delStrategy(that.updateParamIds(strategyIds))
      }).then(() => {
        this.getList()
        this.$modal.msgSuccess('删除成功')
      }).catch(() => {
      })
    },
    /** 导出按钮操作 */
    handleExport() {
      this.download('tenant/strategy/export', {
        ...this.queryParams
      }, `数据源策略数据.xlsx`)
    },
    /** 保存排序按钮操作 */
    handleSort() {
      this.$modal.confirm('是否确认保存新排序?').then(() => {
        let params = this.sortOrderListOnlyDynamic(this.strategyList, this.oldStrategyList, 'strategyId')
        if (params.length > 0) {
          return updateStrategySort(this.updateParamIds(params))
        }
      }).then(() => {
        this.getList()
        this.sortVisible = false
        this.$modal.msgSuccess('保存成功')
      }).catch(() => {
      })
    },
    valueAdd() {
      const newData = {
        sourceId: '',
        isMain: IS_MAIN.FALSE,
        status: STATUS.DISABLE
      }
      this.form.values.push(newData)
    },
    valueChange(id) {
      const writeData = this.containWriteList.filter(function (item) {
        return item.sourceId === id
      })
      let data = this.form.values.filter(function (item) {
        return item.sourceId === id
      })
      data[0].status = writeData[0].status
    },
    valueMainChange(isMain) {
      this.form.hasMain = isMain !== IS_MAIN.FALSE
    },
    valueDelete(row) {
      if (row !== undefined) {
        const index = this.form.values.indexOf(row)
        this.form.values.splice(index, 1)
      }
    },
    valueCheck() {
      let key = 0
      for (let i = 0; i < this.form.values.length; i++) {
        let increase = 0
        if (this.form.values[i].isMain === IS_MAIN.TRUE) {
          key++
          increase = 1
        }
        for (let j = 0; j < this.form.values.length; j++) {
          if (this.form.values[i].sourceId == null || this.form.values[i].sourceId === '') {
            if (this.form.values[i].isMain === IS_MAIN.TRUE) {
              this.form.hasMain = false
            }
            this.form.values.splice(i--, 1)
            if (increase === 1) {
              key--
            }
            break
          } else if (i !== j && this.form.values[i].sourceId === this.form.values[j].sourceId) {
            if (this.form.values[j].isMain === IS_MAIN.TRUE) {
              this.form.hasMain = false
            }
            this.form.values.splice(j--, 1)
          }
        }
      }
      if (this.form.values.length === 0) {
        this.$message({
          message: '有效数据源数量为0，请添加',
          type: 'warning'
        })
        return false
      } else if (key !== 1) {
        this.$message({
          message: '主数据源有且只能有一个，请检查',
          type: 'warning'
        })
        return false
      }
      this.form.amount = this.form.values.length
      return true
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
            const targetRow = this.strategyList.splice(evt.oldIndex, 1)[0]
            this.strategyList.splice(evt.newIndex, 0, targetRow)
            this.sortVisible = true
          }
        })
      }
    }
  },
  mounted() {
    this.handleSortable(false)
  }
}
</script>

<style lang="scss" scoped>
.value-set {
  .value-title {
    float: left;
    line-height: 40px;
  }

  .value-add {
    float: right;
    margin-bottom: 10px;
  }
}

.value-input {
  text-align: center
}
</style>
