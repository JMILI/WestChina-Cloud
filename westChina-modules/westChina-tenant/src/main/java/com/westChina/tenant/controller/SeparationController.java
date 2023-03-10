package com.westChina.tenant.controller;

import com.westChina.common.core.web.controller.BaseController;
import com.westChina.common.core.web.domain.AjaxResult;
import com.westChina.common.log.annotation.Log;
import com.westChina.common.log.enums.BusinessType;
import com.westChina.common.security.annotation.RequiresPermissions;
import com.westChina.tenant.api.domain.source.Source;
import com.westChina.tenant.service.ISeparationService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

/**
 * 数据源 业务处理
 *
 * @author westChina
 */
@RestController
@RequestMapping("/separation")
public class SeparationController extends BaseController {

    @Autowired
    private ISeparationService separationService;

    /**
     * 查询 只读 数据源集合
     */
    @GetMapping("/containRead")
    public AjaxResult containRead(Source source) {
        return AjaxResult.success(separationService.mainSelectContainReadList(source));
    }

    /**
     * 查询 含写 数据源集合
     */
    @GetMapping("/containWrite")
    public AjaxResult containWrite(Source source) {
        return AjaxResult.success(separationService.mainSelectContainWriteList(source));
    }

    /**
     * 获取数据源及其分离策略详细信息
     */
    @RequiresPermissions("tenant:separation:edit")
    @GetMapping(value = "/byId")
    public AjaxResult getInfo(Source source) {
        return AjaxResult.success(separationService.mainSelectSeparationById(source));
    }

    /**
     * 修改数据源
     */
    @RequiresPermissions("tenant:separation:edit")
    @Log(title = "数据源读写分离", businessType = BusinessType.UPDATE)
    @PutMapping
    public AjaxResult edit(@RequestBody Source source) {
        return toAjax(separationService.mainUpdateSeparation(source));
    }
}