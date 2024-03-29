<template>
  <div class="app-container">
    <div class="wrapper-container" v-show="showSearch">
      <el-form :model="queryParams" ref="queryForm" :inline="true" label-width="68px">
        <el-form-item label="租户Id" prop="tenantId">
          <el-input
            v-model="queryParams.tenantId"
            placeholder="请输入租户Id"
            type="number"
            clearable
            size="small"
            @keyup.enter.native="handleQuery"
          />
        </el-form-item>
        <el-form-item label="租户账号" prop="tenantName">
          <el-input
            v-model="queryParams.tenantName"
            placeholder="请输入租户账号"
            clearable
            size="small"
            @keyup.enter.native="handleQuery"
          />
        </el-form-item>
        <el-form-item label="系统名称" prop="tenantSystemName">
          <el-input
            v-model="queryParams.tenantSystemName"
            placeholder="请输入系统名称"
            clearable
            size="small"
            @keyup.enter.native="handleQuery"
          />
        </el-form-item>
        <el-form-item label="租户名称" prop="tenantNick">
          <el-input
            v-model="queryParams.tenantNick"
            placeholder="请输入租户名称"
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
            v-hasPermi="['tenant:tenant:add']"
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
            v-hasPermi="['tenant:tenant:edit']"
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
            v-hasPermi="['tenant:tenant:remove']"
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
            v-hasPermi="['tenant:tenant:export']"
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
            v-hasPermi="['tenant:tenant:edit']"
          >保存排序
          </el-button>
        </el-col>
        <right-toolbar :showSearch.sync="showSearch" @controlSortable="handleSortable"
                       @queryTable="getList"></right-toolbar>
      </el-row>

      <el-table v-loading="loading" :data="tenantList" @selection-change="handleSelectionChange" ref="dataTable"
                row-key="tenantId">
        <el-table-column type="selection" width="55" align="center" class-name="allowDrag"/>
        <el-table-column label="租户Id" align="center" prop="tenantId" class-name="allowDrag" min-width="140">
          <template slot-scope="scope">
            <el-tag type="danger">{{ scope.row.tenantId }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="租户账号" align="center" prop="tenantName" class-name="allowDrag" min-width="120"/>
        <el-table-column label="系统名称" align="center" prop="tenantSystemName" class-name="allowDrag"
                         min-width="120"/>
        <el-table-column label="租户名称" align="center" prop="tenantNick" class-name="allowDrag" min-width="120"/>
        <el-table-column label="数据策略" align="center" prop="strategy.name" class-name="allowDrag" min-width="120">
          <template slot-scope="scope">
            <el-tag type="success">{{ scope.row.strategy.name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="租户logo" align="center" prop="tenantLogo" class-name="allowDrag" min-width="120">
          <template slot-scope="scope">
            <el-image
              style="width: 60px; height: 60px"
              :src="scope.row.tenantLogo"
              fit="contain"
            />
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
              v-hasPermi="['tenant:tenant:edit']"
            >修改
            </el-button>
            <el-button
              size="mini"
              type="text"
              icon="el-icon-circle-check"
              @click="handleMenuScope(scope.row)"
              v-hasPermi="['tenant:tenant:role']"
              v-if="scope.row.isLessor === IS_LESSOR.FALSE"
            >菜单配置
            </el-button>
            <el-button
              size="mini"
              type="text"
              icon="el-icon-delete"
              @click="handleDelete(scope.row)"
              v-hasPermi="['tenant:tenant:remove']"
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

    <!-- 添加或修改租户信息对话框 -->
    <el-dialog :title="title" :visible.sync="open" width="700px" append-to-body v-dialogDrag v-dialogDragHeight>
      <el-form ref="form" :model="form" :rules="rules" label-width="100px">
        <el-row>
          <el-col :span="12">
            <el-form-item label="租户账号" prop="tenantName">
              <el-input v-model="form.tenantName" placeholder="请输入租户账号，只允许英文！"/>
              <span slot="label">
                <el-tooltip content="新租户的企业账号" placement="top">
                <i class="el-icon-question"></i>
                </el-tooltip>
                租户账号
              </span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="策略名称" prop="tenantName">
              <el-select v-model="form.strategyId" placeholder="请选择" :disabled="form.tenantId  != null">
                <el-option
                  v-for="item in strategyList"
                  :key="item.strategyId"
                  :label="item.name"
                  :value="item.strategyId"/>
              </el-select>
              <span slot="label">
                <el-tooltip content="新租户的使用的数据源策略，决定租户的数据存储库" placement="top">
                <i class="el-icon-question"></i>
                </el-tooltip>
                策略名称
              </span>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="12">
            <el-form-item label="租户名称" prop="tenantNick">
              <el-input v-model="form.tenantNick" placeholder="请输入租户名称，中英文皆可！"/>
              <span slot="label">
                <el-tooltip content="新租户的企业名称" placement="top">
                <i class="el-icon-question"></i>
                </el-tooltip>
                租户名称
              </span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="系统名称" prop="tenantSystemName">
              <el-input v-model="form.tenantSystemName" placeholder="请输入系统名称，中英文皆可！"/>
              <span slot="label">
                <el-tooltip content="新租户的系统名称" placement="top">
                <i class="el-icon-question"></i>
                </el-tooltip>
                系统名称
              </span>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="12">
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
          </el-col>
          <el-col :span="12">
            <el-form-item label="可修改次数" prop="tenantNameFrequency">
              <el-input-number v-model="form.tenantNameFrequency" controls-position="right" :min="0" :precision="0"
                               :max="100" size="small"/>
              <span slot="label">
                <el-tooltip content="新租户的企业账号可修改次数" placement="top">
                <i class="el-icon-question"></i>
                </el-tooltip>
                可修改次数
              </span>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="24">
            <el-form-item label="备注" prop="remark">
              <el-input v-model="form.remark" type="textarea" placeholder="请输入内容"/>
            </el-form-item>
          </el-col>
        </el-row>
        <div v-if="form.tenantId === null">
          <el-divider content-position="center">主组织信息</el-divider>
          <el-row>
            <el-col :span="12">
              <el-form-item label="部门名称" prop="remark">
                <el-input v-model="deptForm.deptName" placeholder="请输入部门名称，中英文皆可！" maxlength="20"/>
                <span slot="label">
                <el-tooltip content="新租户的初始部门名称，该部门为顶级部门且与超级管理员绑定，不可删除" placement="top">
                <i class="el-icon-question"></i>
                </el-tooltip>
                部门名称
              </span>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="岗位名称" prop="remark">
                <el-input v-model="postForm.postName" placeholder="请输入岗位名称" maxlength="20"/>
                <span slot="label">
                <el-tooltip content="新租户的初始岗位名称，该岗位归属于顶级部门且与超级管理员绑定，不可删除"
                            placement="top">
                <i class="el-icon-question"></i>
                </el-tooltip>
                岗位名称
              </span>
              </el-form-item>
            </el-col>
          </el-row>
          <el-divider content-position="center">管理员信息</el-divider>
          <el-row>
            <el-col :span="12">
              <el-form-item label="管理员账号" prop="remark">
                <el-input v-model="userForm.userName" placeholder="请输入管理员账号" maxlength="20"/>
                <span slot="label">
                <el-tooltip content="新租户的初始超级管理员账号，默认为‘admin’" placement="top">
                <i class="el-icon-question"></i>
                </el-tooltip>
                管理员账号
              </span>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="管理员昵称" prop="remark">
                <el-input v-model="userForm.nickName" placeholder="请输入管理员昵称" maxlength="20"/>
                <span slot="label">
                <el-tooltip content="新租户的初始超级管理员昵称" placement="top">
                <i class="el-icon-question"></i>
                </el-tooltip>
                管理员昵称
              </span>
              </el-form-item>
            </el-col>
            <el-col :span="24">
              <el-form-item label="管理员密码" prop="remark">
                <el-input v-model="userForm.password" placeholder="请输入管理员密码" maxlength="20" show-password/>
                <span slot="label">
                <el-tooltip content="新租户的初始超级管理员密码，默认为‘admin123’" placement="top">
                <i class="el-icon-question"></i>
                </el-tooltip>
                管理员密码
              </span>
              </el-form-item>
            </el-col>
          </el-row>
        </div>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button type="primary" :loading="submitLoading" @click="submitForm">确 定</el-button>
        <el-button @click="cancel">取 消</el-button>
      </div>
    </el-dialog>

    <!-- 分配角色菜单配置对话框 -->
    <el-dialog :title="title" :visible.sync="openMenuScope" width="500px" append-to-body v-dialogDrag
               v-dialogDragHeight>
      <el-form ref="form" :model="form" label-width="80px">
        <el-row>
          <el-col :span="12">
            <el-form-item label="租户账号" prop="name">
              <el-input v-model="form.tenantName" readonly/>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="菜单权限">
              <el-checkbox v-model="menuExpand" @change="handleCheckedTreeExpand($event)">展开/折叠
              </el-checkbox>
              <el-checkbox v-model="menuNodeAll" @change="handleCheckedTreeNodeAll($event)">全选/全不选
              </el-checkbox>
              <el-tree
                class="tree-border"
                :data="systemMenuOptions"
                show-checkbox
                ref="systemMenu"
                node-key="id"
                :check-strictly="false"
                empty-text="加载中，请稍后"
                :props="defaultProps"
              ></el-tree>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button type="primary" :loading="submitLoading" @click="submitMenuScope">确 定</el-button>
        <el-button @click="cancelMenuScope">取 消</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import {
  addTenant,
  delTenant,
  getTenant,
  listTenant,
  updateTenant,
  updateTenantSort
} from '@/api/tenant/tenant'
import Sortable from 'sortablejs'
import {listStrategyExclude} from '@/api/tenant/strategy'
import {IS_LESSOR, STATUS, STATUS_UPDATE_OPERATION, SYSTEM_DEFAULT} from "@constant/constants"
import {getLessorMenuRange, getLessorMenuScope, setTenantMenuScope} from "@api/common/authority"

export default {
  name: 'Tenant',
  dicts: ['sys_normal_disable'],
  components: {},
  data() {
    return {
      //常量区
      IS_LESSOR: IS_LESSOR,
      SYSTEM_DEFAULT: SYSTEM_DEFAULT,
      STATUS: STATUS,
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
      // 租户信息表格数据
      tenantList: [],
      // 租户信息表格原始数据
      oldTenantList: [],
      // 可用策略集合
      strategyList: [],
      // 排序保存按钮显示
      sortVisible: false,
      // 排序参数
      sortable: null,
      // 弹出层标题
      title: '',
      // 是否显示弹出层
      open: false,
      // 是否显示弹出层（菜单配置）
      openMenuScope: false,
      menuExpand: false,
      menuNodeAll: false,
      // 模块&菜单列表
      systemMenuOptions: [],
      // 查询参数
      queryParams: {
        pageNum: 1,
        pageSize: 10,
        tenantId: null,
        tenantName: null,
        tenantSystemName: null,
        tenantNick: null,
        status: null
      },
      // 表单参数
      form: {},
      deptForm: {},
      postForm: {},
      userForm: {},
      systemMenuForm: {},
      defaultProps: {
        children: "children",
        label: "label"
      },
      // 表单校验
      rules: {
        tenantName: [
          {required: true, message: '租户账号不能为空', trigger: 'blur'},
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
        tenantSystemName: [
          {required: true, message: '系统名称不能为空', trigger: 'blur'}
        ],
        tenantNick: [
          {required: true, message: '租户名称不能为空', trigger: 'blur'}
        ]
      }
    }
  },
  created() {
    this.getList()
  },
  methods: {
    /** 查询租户信息列表 */
    getList() {
      this.loading = true
      listTenant(this.queryParams).then(response => {
        this.tenantList = response.data.items
        this.total = response.data.total
        this.loading = false
      })
    },
    // 取消按钮
    cancel() {
      this.open = false
      this.reset()
    },
    // 取消按钮（菜单权限）
    cancelMenuScope() {
      this.openMenuScope = false
      this.reset()
    },
    // 表单重置
    reset() {
      if (this.$refs.systemMenu !== undefined) {
        this.$refs.systemMenu.setCheckedKeys([])
      }
      this.form = {
        tenantId: null,
        strategyId: null,
        tenantName: null,
        tenantSystemName: null,
        tenantNick: null,
        tenantLogo: null,
        tenantNameFrequency: 1,
        sort: 0,
        status: STATUS.NORMAL,
        remark: null,
        values: [],
        isChange: SYSTEM_DEFAULT.FALSE,
        hasMain: false
      }
      this.deptForm = {
        deptName: '华西科技'
      }
      this.postForm = {
        postName: '董事长'
      }
      this.userForm = {
        userName: 'admin',
        nickName: '超级管理员',
        password: 'admin123'
      }
      this.systemMenuForm = {
        enterpriseId: null,
        params: {}
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
      this.ids = selection.map(item => item.tenantId)
      this.idNames = selection.map(item => item.tenantName)
      this.single = selection.length !== 1
      this.multiple = !selection.length
    },
    // 树权限（展开/折叠）
    handleCheckedTreeExpand(value) {
      let treeList = this.systemMenuOptions
      for (let i = 0; i < treeList.length; i++) {
        this.$refs.systemMenu.store.nodesMap[treeList[i].id].expanded = value
      }
    },
    // 树权限（全选/全不选）
    handleCheckedTreeNodeAll(value) {
      this.$refs.systemMenu.setCheckedNodes(value ? this.systemMenuOptions : [])
    },
    /** 获取可用策略组 */
    getStrategyList() {
      listStrategyExclude().then(response => {
        this.strategyList = response.data
      })
    },
    /** 新增按钮操作 */
    handleAdd() {
      this.reset()
      this.getStrategyList()
      this.open = true
      this.title = '添加租户信息'
    },
    /** 修改按钮操作 */
    handleUpdate(row) {
      this.reset()
      this.getStrategyList()
      const tenantId = row.tenantId || this.ids[0]
      getTenant({tenantId: tenantId}).then(response => {
        this.form = response.data
        this.open = true
        this.title = '修改租户信息'
      })
    },
    /** 修改状态按钮操作 */
    handleStatusChange(row) {

      let msg = row.status === STATUS.NORMAL ? "启用" : "停用"
      updateTenant({
        tenantId: row.tenantId,
        isChange: row.isChange,
        status: row.status,
        updateType: STATUS_UPDATE_OPERATION
      }).then(response => {
        this.$modal.msgSuccess(msg + "成功")
      }).catch(() => {
        row.status = row.status === STATUS.NORMAL ? STATUS.DISABLE : STATUS.NORMAL
      })
    },
    /** 分配菜单权限操作 */
    handleMenuScope(row) {
      this.reset()
      this.getSystemMenuTreeSelect(row.tenantId)
      const menuScope = this.getMenuScope(row.tenantId)
      getTenant({tenantId: row.tenantId}).then(response => {
        this.form = response.data
        menuScope.then(res => {
          this.$refs.systemMenu.setCheckedKeys(Array.from(res.data.wholeIds, x => x.uid))
        })
        this.openMenuScope = true
        this.title = "设置菜单权限"
      })
    },
    /** 查询模块&菜单树结构 */
    getSystemMenuTreeSelect(tenantId) {
      getLessorMenuScope(tenantId).then(response => {
        this.systemMenuOptions = response.data
      })
    },
    /** 根据角色Id查询模块&菜单树结构 */
    getMenuScope(tenantId) {
      return getLessorMenuRange(tenantId).then(response => {
        return response
      })
    },
    // 所有模块&菜单节点数据
    getSystemMenuAllCheckedKeys() {
      // 目前被选中的菜单节点
      return this.$refs.systemMenu.getCheckedKeys()
    },
    /** 提交按钮（菜单权限） */
    submitMenuScope() {
      this.submitLoading = true
      this.systemMenuForm.enterpriseId = this.form.tenantId
      if (this.systemMenuForm.enterpriseId != null) {
        const wholeIds = this.$refs.systemMenu.getCheckedKeys()
        if (wholeIds.length > 0) {
          this.systemMenuForm.params.wholeIds = wholeIds
        }
        const halfIds = this.$refs.systemMenu.getHalfCheckedKeys()
        if (halfIds.length > 0) {
          this.systemMenuForm.params.halfIds = halfIds
        }
        setTenantMenuScope(this.systemMenuForm).then(response => {
          this.$modal.msgSuccess("修改成功")
          this.openMenuScope = false
          this.getList()
        }).catch(() => {
          this.submitLoading = false
        })
      } else {
        this.submitLoading = false
      }
    },
    /** 提交按钮 */
    submitForm() {
      this.submitLoading = true
      this.$refs['form'].validate(valid => {
        if (valid) {
          if (this.form.tenantId != null) {
            if (this.form.isChange === SYSTEM_DEFAULT.FALSE) {
              updateTenant(this.form).then(response => {
                this.$modal.msgSuccess('修改成功')
                this.open = false
                this.getList()
              }).catch(() => {
                this.submitLoading = false
              })
            } else {
              this.submitLoading = false
              this.$message({
                message: '系统租户不允许进行修改操作',
                type: 'warning'
              })
            }
          } else {
            let params = {
              dept: this.deptForm,
              post: this.postForm,
              user: this.userForm,
            }
            this.form.params = params,
              addTenant(this.form).then(response => {
                this.$modal.msgSuccess('新增成功')
                this.open = false
                this.getList()
              }).catch(() => {
                this.submitLoading = false
              })
          }
        } else {
          this.submitLoading = false
        }
      })
    },
    /** 删除按钮操作 */
    handleDelete(row) {
      const tenantIds = row.tenantId || this.ids
      const names = row.tenantName || this.idNames
      let that = this
      this.$modal.confirm('是否确认删除租户"' + names + '"?').then(function () {
        return delTenant(that.updateParamIds(tenantIds))
      }).then(() => {
        this.getList()
        this.$modal.msgSuccess('删除成功')
      }).catch(() => {
      })
    },
    /** 导出按钮操作 */
    handleExport() {
      this.download('tenant/tenant/export', {
        ...this.queryParams
      }, `租户信息数据.xlsx`)
    },
    /** 保存排序按钮操作 */
    handleSort() {
      this.$modal.confirm('是否确认保存新排序?').then(() => {
        let params = this.sortOrderListOnlyDynamic(this.tenantList, this.oldTenantList, 'tenantId')
        if (params.length > 0) {
          return updateTenantSort(this.updateParamIds(params))
        }
      }).then(() => {
        this.getList()
        this.sortVisible = false
        this.$modal.msgSuccess('保存成功')
      }).catch(() => {
      })
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
            const targetRow = this.tenantList.splice(evt.oldIndex, 1)[0]
            this.tenantList.splice(evt.newIndex, 0, targetRow)
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
