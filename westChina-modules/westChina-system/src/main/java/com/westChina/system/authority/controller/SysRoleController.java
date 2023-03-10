package com.westChina.system.authority.controller;

import com.westChina.common.core.constant.BaseConstants;
import com.westChina.common.core.utils.StringUtils;
import com.westChina.common.core.utils.poi.ExcelUtil;
import com.westChina.common.core.web.controller.BaseController;
import com.westChina.common.core.web.domain.AjaxResult;
import com.westChina.common.log.annotation.Log;
import com.westChina.common.log.enums.BusinessType;
import com.westChina.common.security.annotation.RequiresPermissions;
import com.westChina.system.api.domain.authority.SysRole;
import com.westChina.system.authority.service.ISysRoleService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import javax.servlet.http.HttpServletResponse;
import java.util.List;

/**
 * 角色信息
 *
 * @author westChina
 */
@RestController
@RequestMapping("/role")
public class SysRoleController extends BaseController {

    @Autowired
    private ISysRoleService roleService;

    /**
     * 获取角色列表
     */
    @RequiresPermissions("system:role:list")
    @GetMapping("/list")
    public AjaxResult list(SysRole role) {
        startPage();
        List<SysRole> list = roleService.selectRoleList(role);
        return getDataTable(list);
    }

    /**
     * 根据角色Id获取详细信息
     */
    @RequiresPermissions("system:role:query")
    @GetMapping(value = "/byId")
    public AjaxResult getInfo(SysRole role) {
        return AjaxResult.success(roleService.selectRoleById(role));
    }

    /**
     * 新增角色
     */
    @RequiresPermissions("system:role:add")
    @Log(title = "角色管理", businessType = BusinessType.INSERT)
    @PostMapping
    public AjaxResult add(@Validated @RequestBody SysRole role) {
        if (StringUtils.equals(BaseConstants.Check.NOT_UNIQUE.getCode(), roleService.checkRoleCodeUnique(role))) {
            return AjaxResult.error("新增角色'" + role.getName() + "'失败，角色编码已存在");
        } else if (StringUtils.equals(BaseConstants.Check.NOT_UNIQUE.getCode(), roleService.checkRoleNameUnique(role))) {
            return AjaxResult.error("新增角色'" + role.getName() + "'失败，角色名称已存在");
        } else if (StringUtils.equals(BaseConstants.Check.NOT_UNIQUE.getCode(), roleService.checkRoleKeyUnique(role))) {
            return AjaxResult.error("修改角色'" + role.getName() + "'失败，角色权限已存在");
        }
        return toAjax(roleService.insertRole(role));
    }

    /**
     * 修改保存角色
     */
    @RequiresPermissions("system:role:edit")
    @Log(title = "角色管理", businessType = BusinessType.UPDATE)
    @PutMapping
    public AjaxResult edit(@Validated @RequestBody SysRole role) {
        if (StringUtils.equals(BaseConstants.Check.NOT_UNIQUE.getCode(), roleService.checkRoleCodeUnique(role))) {
            return AjaxResult.error("修改角色'" + role.getName() + "'失败，角色编码已存在");
        } else if (StringUtils.equals(BaseConstants.Check.NOT_UNIQUE.getCode(), roleService.checkRoleNameUnique(role))) {
            return AjaxResult.error("修改角色'" + role.getName() + "'失败，角色名称已存在");
        } else if (StringUtils.equals(BaseConstants.Check.NOT_UNIQUE.getCode(), roleService.checkRoleKeyUnique(role))) {
            return AjaxResult.error("修改角色'" + role.getName() + "'失败，角色权限已存在");
        }
        return toAjax(roleService.updateRole(role));
    }

    /**
     * 状态修改
     */
    @RequiresPermissions("system:role:edit")
    @Log(title = "角色管理", businessType = BusinessType.UPDATE)
    @PutMapping("/changeStatus")
    public AjaxResult changeStatus(@RequestBody SysRole role) {
        return toAjax(roleService.updateRoleStatus(role));
    }

    /**
     * 修改保存数据权限
     */
    @RequiresPermissions("system:role:edit")
    @Log(title = "角色管理", businessType = BusinessType.UPDATE)
    @PutMapping("/dataScope/save")
    public AjaxResult dataScope(@RequestBody SysRole role) {
        return toAjax(roleService.authDataScope(role));
    }

    /**
     * 删除角色
     */
    @RequiresPermissions("system:role:remove")
    @Log(title = "角色管理", businessType = BusinessType.DELETE)
    @DeleteMapping
    public AjaxResult remove(@RequestBody SysRole role) {
        return toAjax(roleService.deleteRoleByIds(role));
    }

    /**
     * 导出角色列表
     */
    @Log(title = "角色管理", businessType = BusinessType.EXPORT)
    @RequiresPermissions("system:role:export")
    @PostMapping("/export")
    public void export(HttpServletResponse response, SysRole role) {
        List<SysRole> list = roleService.selectRoleList(role);
        ExcelUtil<SysRole> util = new ExcelUtil<SysRole>(SysRole.class);
        util.exportExcel(response, list, "角色数据");
    }

    /**
     * 获取角色选择框列表
     */
    @RequiresPermissions("system:role:query")
    @GetMapping("/optionSelect")
    public AjaxResult optionSelect() {
        return AjaxResult.success(roleService.selectRoleAll());
    }
}
