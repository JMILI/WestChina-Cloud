package com.westChina.system.monitor.controller;

import com.westChina.common.core.utils.poi.ExcelUtil;
import com.westChina.common.core.web.controller.BaseController;
import com.westChina.common.core.web.domain.AjaxResult;
import com.westChina.common.log.annotation.Log;
import com.westChina.common.log.enums.BusinessType;
import com.westChina.common.security.annotation.InnerAuth;
import com.westChina.common.security.annotation.RequiresPermissions;
import com.westChina.system.api.domain.monitor.SysLoginInfo;
import com.westChina.system.monitor.service.ISysLoginInfoService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import javax.servlet.http.HttpServletResponse;
import java.util.List;

/**
 * 系统访问记录
 *
 * @author westChina
 */
@RestController
@RequestMapping("/loginInfo")
public class SysLoginInfoController extends BaseController {

    @Autowired
    private ISysLoginInfoService loginInfoService;

    @RequiresPermissions("system:loginInfo:list")
    @GetMapping("/list")
    public AjaxResult list(SysLoginInfo loginInfo) {
        startPage();
        List<SysLoginInfo> list = loginInfoService.selectLoginInfoList(loginInfo);
        return getDataTable(list);
    }

    @Log(title = "登录日志", businessType = BusinessType.EXPORT)
    @RequiresPermissions("system:loginInfo:export")
    @PostMapping("/export")
    public void export(HttpServletResponse response, SysLoginInfo loginInfo) {
        List<SysLoginInfo> list = loginInfoService.selectLoginInfoList(loginInfo);
        ExcelUtil<SysLoginInfo> util = new ExcelUtil<SysLoginInfo>(SysLoginInfo.class);
        util.exportExcel(response, list, "登录日志");
    }

    @RequiresPermissions("system:loginInfo:remove")
    @Log(title = "登录日志", businessType = BusinessType.DELETE)
    @DeleteMapping
    public AjaxResult remove(@RequestBody SysLoginInfo loginInfo) {
        return toAjax(loginInfoService.deleteLoginInfoByIds(loginInfo));
    }

    @RequiresPermissions("system:loginInfo:remove")
    @Log(title = "登录日志", businessType = BusinessType.DELETE)
    @DeleteMapping("/clean")
    public AjaxResult clean() {
        loginInfoService.cleanLoginInfo();
        return AjaxResult.success();
    }

    @InnerAuth
    @PostMapping
    public AjaxResult add(@RequestBody SysLoginInfo loginInfo) {
        return toAjax(loginInfoService.insertLoginInfo(loginInfo.getSourceName(), loginInfo));
    }
}
