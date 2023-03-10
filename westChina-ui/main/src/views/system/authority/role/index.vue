<template>
  <div class="app-container">
    <div class="wrapper-container" v-show="showSearch">
      <el-form :model="queryParams" ref="queryForm" :inline="true">
        <el-form-item label="角色编码" prop="roleCode">
          <el-input
            v-model="queryParams.roleCode"
            placeholder="请输入角色编码"
            clearable
            size="small"
            style="width: 240px"
            @keyup.enter.native="handleQuery"
          />
        </el-form-item>
        <el-form-item label="角色名称" prop="name">
          <el-input
            v-model="queryParams.name"
            placeholder="请输入角色名称"
            clearable
            size="small"
            style="width: 240px"
            @keyup.enter.native="handleQuery"
          />
        </el-form-item>
        <el-form-item label="权限字符" prop="roleKey">
          <el-input
            v-model="queryParams.roleKey"
            placeholder="请输入权限字符"
            clearable
            size="small"
            style="width: 240px"
            @keyup.enter.native="handleQuery"
          />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select
            v-model="queryParams.status"
            placeholder="角色状态"
            clearable
            size="small"
            style="width: 240px"
          >
            <el-option
              v-for="dict in dict.type.sys_normal_disable"
              :key="dict.value"
              :label="dict.label"
              :value="dict.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="创建时间">
          <el-date-picker
            v-model="dateRange"
            size="small"
            style="width: 240px"
            value-format="yyyy-MM-dd"
            type="daterange"
            range-separator="-"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
          ></el-date-picker>
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
            v-hasPermi="['system:role:add']"
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
            v-hasPermi="['system:role:edit']"
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
            v-hasPermi="['system:role:remove']"
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
            v-hasPermi="['system:role:export']"
          >导出
          </el-button>
        </el-col>
        <right-toolbar :showSearch.sync="showSearch" :sortVisible="false" @queryTable="getList"/>
      </el-row>

      <el-table v-loading="loading" :data="roleList" @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55" align="center"/>
        <el-table-column label="角色编码" prop="roleCode" min-width="120" align="center"/>
        <el-table-column label="角色名称" prop="name" :show-overflow-tooltip="true" min-width="120" align="center"/>
        <el-table-column label="权限字符" prop="roleKey" :show-overflow-tooltip="true" min-width="120" align="center"/>
        <el-table-column label="状态" align="center" min-width="120">
          <template slot-scope="scope">
            <el-switch
              v-model="scope.row.status"
              :active-value="STATUS.NORMAL"
              :inactive-value="STATUS.DISABLE"
              @change="handleStatusChange(scope.row)"
            ></el-switch>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" align="center" prop="createTime" min-width="180">
          <template slot-scope="scope">
            <span>{{ parseTime(scope.row.createTime) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" align="center" min-width="120" class-name="small-padding fixed-width">
          <template slot-scope="scope">
            <el-button
              size="mini"
              type="text"
              icon="el-icon-edit"
              @click="handleUpdate(scope.row)"
              v-hasPermi="['system:role:edit']"
            >修改
            </el-button>
            <el-button
              size="mini"
              type="text"
              icon="el-icon-circle-check"
              @click="handleMenuScope(scope.row)"
              v-hasPermi="['system:role:edit']"
            >菜单配置
            </el-button>
            <el-button
              size="mini"
              type="text"
              icon="el-icon-circle-check"
              @click="handleDataScope(scope.row)"
              v-hasPermi="['system:role:edit']"
            >数据权限
            </el-button>
            <el-button
              size="mini"
              type="text"
              icon="el-icon-delete"
              @click="handleDelete(scope.row)"
              v-hasPermi="['system:role:remove']"
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

    <!-- 添加或修改角色配置对话框 -->
    <el-dialog :title="title" :visible.sync="open" width="600px" append-to-body v-dialogDrag v-dialogDragHeight>
      <el-form ref="form" :model="form" :rules="rules" label-width="100px">
        <el-row>
          <el-col :span="24">
            <el-form-item label="角色编码" prop="roleCode">
              <el-input v-model="form.roleCode" placeholder="请输入角色编码"/>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="角色名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入角色名称"/>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item prop="roleKey">
          <span slot="label">
            <el-tooltip content="控制器中定义的权限字符，如：@PreAuthorize(`@ss.hasRole('admin')`)" placement="top">
              <i class="el-icon-question"></i>
            </el-tooltip>
            权限字符
          </span>
              <el-input v-model="form.roleKey" placeholder="请输入权限字符" :readonly="form.roleId !== undefined"/>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="显示顺序" prop="sort">
              <el-input-number v-model="form.sort" controls-position="right" :min="0"/>
            </el-form-item>
          </el-col>
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
          <el-col :span="24">
            <el-form-item label="备注">
              <el-input v-model="form.remark" type="textarea" placeholder="请输入内容"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
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
          <el-col :span="24">
            <el-form-item label="角色编码" prop="roleCode">
              <el-input v-model="form.roleCode" placeholder="请输入角色编码" readonly/>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="角色名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入角色名称" readonly/>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="菜单权限">
              <el-checkbox v-model="menuExpand" @change="handleCheckedTreeExpand($event, 'systemMenu')">展开/折叠
              </el-checkbox>
              <el-checkbox v-model="menuNodeAll" @change="handleCheckedTreeNodeAll($event, 'systemMenu')">全选/全不选
              </el-checkbox>
              <el-tree
                class="tree-border"
                :data="systemMenuOptions"
                show-checkbox
                ref="systemMenu"
                node-key="id"
                empty-text="加载中，请稍候"
                :props="defaultProps"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button type="primary" :loading="submitLoading" @click="submitMenuScope">确 定</el-button>
        <el-button @click="cancelMenuScope">取 消</el-button>
      </div>
    </el-dialog>

    <!-- 分配角色数据权限对话框 -->
    <el-dialog :title="title" :visible.sync="openDataScope" width="500px" append-to-body v-dialogDrag
               v-dialogDragHeight>
      <el-form :model="form" label-width="80px">
        <el-form-item label="角色名称">
          <el-input v-model="form.name" :disabled="true"/>
        </el-form-item>
        <el-form-item label="权限字符">
          <el-input v-model="form.roleKey" :disabled="true"/>
        </el-form-item>
        <el-form-item label="权限范围">
          <el-select v-model="form.dataScope" @change="dataScopeSelectChange">
            <el-option
              v-for="dict in dict.type.sys_data_scope"
              :key="dict.value"
              :label="dict.label"
              :value="dict.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="数据权限" v-show="form.dataScope === DATA_SCOPE.CUSTOM">
          <el-checkbox v-model="deptExpand" @change="handleCheckedTreeExpand($event, 'deptPost')">展开/折叠</el-checkbox>
          <el-checkbox v-model="deptNodeAll" @change="handleCheckedTreeNodeAll($event, 'deptPost')">全选/全不选</el-checkbox>
          <el-tree
            class="tree-border"
            :data="deptPostOptions"
            show-checkbox
            default-expand-all
            ref="deptPost"
            node-key="id"
            empty-text="加载中，请稍候"
            :props="defaultProps"
          />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button type="primary" :loading="submitLoading" @click="submitDataScope">确 定</el-button>
        <el-button @click="cancelDataScope">取 消</el-button>
      </div>
    </el-dialog>
  </div>

</template>

<script>
import {
  listRole,
  getRole,
  delRole,
  addRole,
  updateRole,
  dataScope,
  changeRoleStatus,
} from "@/api/system/role"
import {treeSelect as roleDeptTreeSelect} from "@/api/system/post"
import {STATUS} from "@constant/constants"
import {DATA_SCOPE} from "@constant/authorityContants"
import {getEnterpriseMenuScope, getRoleMenuRange, setRoleMenuScope, getRoleDataRange} from "@api/common/authority"

export default {
  name: "Role",
  dicts: ['sys_normal_disable', 'sys_data_scope'],
  data() {
    return {
      //常量区
      STATUS: STATUS,
      DATA_SCOPE: DATA_SCOPE,
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
      // 角色表格数据
      roleList: [],
      // 弹出层标题
      title: "",
      // 是否显示弹出层
      open: false,
      // 是否显示弹出层（菜单配置）
      openMenuScope: false,
      // 是否显示弹出层（数据权限）
      openDataScope: false,
      menuExpand: false,
      menuNodeAll: false,
      deptExpand: true,
      deptNodeAll: false,
      // 日期范围
      dateRange: [],
      // 模块&菜单列表
      systemMenuOptions: [],
      // 部门-岗位列表
      deptPostOptions: [],
      deptOptions: [],
      // 查询参数
      queryParams: {
        pageNum: 1,
        pageSize: 10,
        roleCode: undefined,
        name: undefined,
        roleKey: undefined,
        status: undefined
      },
      // 表单参数
      form: {},
      defaultProps: {
        children: "children",
        label: "label"
      },
      // 表单校验
      rules: {
        roleCode: [
          {required: true, message: "角色编码不能为空", trigger: "blur"}
        ],
        name: [
          {required: true, message: "角色名称不能为空", trigger: "blur"}
        ],
        roleKey: [
          {required: true, message: "权限字符不能为空", trigger: "blur"}
        ]
      }
    }
  },
  created() {
    this.getList()
  },
  methods: {
    /** 查询角色列表 */
    getList() {
      this.loading = true
      listRole(this.addDateRange(this.queryParams, this.dateRange)).then(
        response => {
          this.roleList = response.data.items
          this.total = response.data.total
          this.loading = false
        }
      )
    },
    /** 查询模块&菜单树结构 */
    getSystemMenuTreeSelect() {
      getEnterpriseMenuScope().then(response => {
        this.systemMenuOptions = response.data
      })
    },
    /** 查询部门-岗位树结构 */
    getDeptPostTreeSelect() {
      roleDeptTreeSelect().then(response => {
        this.deptPostOptions = response.data
      })
    },
    /** 根据角色Id查询模块&菜单树结构 */
    getMenuScope(roleId) {
      return getRoleMenuRange({roleId: roleId}).then(response => {
        return response
      })
    },
    /** 根据角色Id查询部门-岗位树结构 */
    getDataScope(roleId) {
      return getRoleDataRange({roleId: roleId}).then(response => {
        return response
      })
    },
    // 角色状态修改
    handleStatusChange(row) {
      let text = row.status === STATUS.NORMAL ? "启用" : "停用"
      this.$modal.confirm('确认要"' + text + '""' + row.name + '"角色吗?').then(function () {
        return changeRoleStatus({roleId: row.roleId, status: row.status})
      }).then(() => {
        this.$modal.msgSuccess(text + "成功")
      }).catch(function () {
        row.status = row.status === STATUS.NORMAL ? STATUS.DISABLE : STATUS.NORMAL
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
    // 取消按钮（数据权限）
    cancelDataScope() {
      this.openDataScope = false
      this.reset()
    },
    // 表单重置
    reset() {
      if (this.$refs.systemMenu !== undefined) {
        this.$refs.systemMenu.setCheckedKeys([])
      }
      this.menuExpand = false
      this.menuNodeAll = false
      this.deptExpand = true
      this.deptNodeAll = false
      this.form = {
        roleId: undefined,
        roleCode: undefined,
        name: undefined,
        roleKey: undefined,
        dataScope: DATA_SCOPE.ALL,
        sort: 0,
        status: STATUS.NORMAL,
        deptPostIds: [],
        remark: undefined
      }
      this.resetForm("form")
      this.submitLoading = false
    },
    /** 搜索按钮操作 */
    handleQuery() {
      this.queryParams.pageNum = 1
      this.getList()
    },
    /** 重置按钮操作 */
    resetQuery() {
      this.dateRange = []
      this.resetForm("queryForm")
      this.handleQuery()
    },
    // 多选框选中数据
    handleSelectionChange(selection) {
      this.ids = selection.map(item => item.roleId)
      this.idNames = selection.map(item => item.name)
      this.single = selection.length !== 1
      this.multiple = !selection.length
    },
    // 树权限（展开/折叠）
    handleCheckedTreeExpand(value, type) {
      if (type === 'systemMenu') {
        let treeList = this.systemMenuOptions
        for (let i = 0; i < treeList.length; i++) {
          this.$refs.systemMenu.store.nodesMap[treeList[i].id].expanded = value
        }
      } else if (type === 'deptPost') {
        let treeList = this.deptPostOptions
        for (let i = 0; i < treeList.length; i++) {
          this.$refs.deptPost.store.nodesMap[treeList[i].id].expanded = value
        }
      }
    },
    // 树权限（全选/全不选）
    handleCheckedTreeNodeAll(value, type) {
      if (type === 'systemMenu') {
        this.$refs.systemMenu.setCheckedNodes(value ? this.systemMenuOptions : [])
      } else if (type === 'deptPost') {
        this.$refs.deptPost.setCheckedNodes(value ? this.deptPostOptions : [])
      }
    },
    /** 新增按钮操作 */
    handleAdd() {
      this.reset()
      this.open = true
      this.title = "添加角色"
    },
    /** 修改按钮操作 */
    handleUpdate(row) {
      this.reset()
      const roleId = row.roleId || this.ids[0]
      getRole({roleId: roleId}).then(response => {
        this.form = response.data
        this.open = true
        this.title = "修改角色"
      })
    },
    /** 选择角色权限范围触发 */
    dataScopeSelectChange(value) {
      if (value !== DATA_SCOPE.CUSTOM) {
        this.$refs.deptPost.setCheckedKeys([])
      }
    },
    /** 分配菜单权限操作 */
    handleMenuScope(row) {
      this.reset()
      this.getSystemMenuTreeSelect()
      const menuScope = this.getMenuScope(row.roleId)
      getRole({roleId: row.roleId}).then(response => {
        this.form = response.data
        menuScope.then(res => {
          this.$refs.systemMenu.setCheckedKeys(Array.from(res.data.wholeIds, x => x.uid))
        })
        this.openMenuScope = true
        this.title = "分配菜单权限"
      })
    },
    /** 分配数据权限操作 */
    handleDataScope(row) {
      this.reset()
      this.getDeptPostTreeSelect()
      const dataScope = this.getDataScope(row.roleId)
      getRole({roleId: row.roleId}).then(response => {
        this.form = response.data
        this.openDataScope = true
          dataScope.then(res => {
            this.$refs.deptPost.setCheckedKeys(Array.from(res.data.deptPostIds, x => x))
          })
        this.title = "分配数据权限"
      })
    },
    /** 提交按钮 */
    submitForm() {
      this.submitLoading = true
      this.$refs["form"].validate(valid => {
        if (valid) {
          if (this.form.roleId !== undefined) {
            updateRole(this.form).then(response => {
              this.$modal.msgSuccess("修改成功")
              this.open = false
              this.getList()
            }).catch(() => {
              this.submitLoading = false
            })
          } else {
            addRole(this.form).then(response => {
              this.$modal.msgSuccess("新增成功")
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
    /** 提交按钮（菜单权限） */
    submitMenuScope() {
      this.submitLoading = true
      const wholeIds = this.$refs.systemMenu.getCheckedKeys()
      if (wholeIds.length > 0) {
        this.form.params.wholeIds = wholeIds
      }
      const halfIds = this.$refs.systemMenu.getHalfCheckedKeys()
      if (halfIds.length > 0) {
        this.form.params.halfIds = halfIds
      }
      setRoleMenuScope(this.form).then(response => {
        this.$modal.msgSuccess("修改成功")
        this.openMenuScope = false
        this.getList()
      }).catch(() => {
        this.submitLoading = false
      })
    },
    /** 提交按钮（数据权限） */
    submitDataScope: function () {
      this.submitLoading = true
      if (this.form.roleId !== undefined) {
        this.form.deptPostIds = this.$refs.deptPost.getCheckedKeys()
        dataScope(this.form).then(response => {
          this.$modal.msgSuccess("修改成功")
          this.openDataScope = false
          this.getList()
        }).catch(() => {
          this.submitLoading = false
        })
      } else {
        this.submitLoading = false
      }
    },
    /** 删除按钮操作 */
    handleDelete(row) {
      const roleIds = row.roleId || this.ids
      const name = row.name || this.idNames
      let $this = this
      this.$modal.confirm('是否确认删除角色"' + name + '"?').then(function () {
        return delRole($this.updateParamIds(roleIds))
      }).then(() => {
        this.getList()
        this.$modal.msgSuccess("删除成功")
      }).catch((err) => {
      })
    },
    /** 导出按钮操作 */
    handleExport() {
      this.download('system/role/export', {
        ...this.queryParams
      }, `role_${new Date().getTime()}.xlsx`)
    }
  }
}
</script>
