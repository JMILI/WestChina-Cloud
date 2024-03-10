package com.westChina.ct.controller;

import java.util.List;
import java.io.IOException;
import javax.servlet.http.HttpServletResponse;


import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import com.westChina.common.log.annotation.Log;
import com.westChina.common.log.enums.BusinessType;
import com.westChina.common.security.annotation.RequiresPermissions;
import com.westChina.ct.domain.CtPatients;
import com.westChina.ct.domain.FormHit;
import com.westChina.ct.service.ICtPatientsService;
import com.westChina.common.core.web.controller.BaseController;
import com.westChina.common.core.web.domain.AjaxResult;
import com.westChina.common.core.utils.poi.ExcelUtil;

/**
 * 病人信息 业务处理
 *
 * @author jm
 */
@RestController
@RequestMapping("/patients")
public class CtPatientsController extends BaseController {

    @Autowired
    private ICtPatientsService patientsService;

    /**
     * 根据搜索关键字（身份证号码OR手机号）查找 formHit和前端对应便于记忆
     *
     * @param formHit {}
     * @return
     */
    @RequiresPermissions("ct:patients:query")
    @GetMapping(value = "/byFormHit")
    public AjaxResult searchByFormHit(FormHit formHit) {
        List<CtPatients> list = patientsService.searchByFormHit(formHit);
        return AjaxResult.success(list);
    }

    /**
     * 查询病人信息列表
     */
    @RequiresPermissions("ct:patients:list")
    @GetMapping("/list")
    public AjaxResult list(CtPatients patients) {
        startPage();
        List<CtPatients> list = patientsService.selectPatientsList(patients);
        return getDataTable(list);
    }

    /**
     * 导出病人信息列表
     */
    @RequiresPermissions("ct:patients:export")
    @Log(title = "病人信息", businessType = BusinessType.EXPORT)
    @PostMapping("/export")
    public void export(HttpServletResponse response, CtPatients patients) throws IOException {
        List<CtPatients> list = patientsService.selectPatientsList(patients);
        ExcelUtil<CtPatients> util = new ExcelUtil<CtPatients>(CtPatients.class);
        util.exportExcel(response, list, "病人信息数据");
    }

    /**
     * 获取病人信息详细信息
     */
    @RequiresPermissions("ct:patients:query")
    @GetMapping(value = "/byId")
    public AjaxResult getInfo(CtPatients patients) {
        return AjaxResult.success(patientsService.selectPatientsByPatId(patients));
    }

    /**
     * 新增病人信息
     */
    @RequiresPermissions("ct:patients:add")
    @Log(title = "病人信息", businessType = BusinessType.INSERT)
    @PostMapping
    public AjaxResult add(@RequestBody CtPatients patients) {
        return toAjax(patientsService.insertPatients(patients));
    }

    /**
     * 修改病人信息
     */
    @RequiresPermissions("ct:patients:edit")
    @Log(title = "病人信息", businessType = BusinessType.UPDATE)
    @PutMapping
    public AjaxResult edit(@RequestBody CtPatients patients) {
        return toAjax(patientsService.updatePatients(patients));
    }

    /**
     * 修改病人信息排序
     */
    @RequiresPermissions("ct:patients:edit")
    @Log(title = "病人信息", businessType = BusinessType.UPDATE)
    @PutMapping(value = "/sort")
    public AjaxResult updateSort(@RequestBody CtPatients patients) {
        return toAjax(patientsService.updatePatientsSort(patients));
    }

    /**
     * 删除病人信息
     */
    @RequiresPermissions("ct:patients:remove")
    @Log(title = "病人信息", businessType = BusinessType.DELETE)
    @DeleteMapping
    public AjaxResult remove(@RequestBody CtPatients patients) {
        return toAjax(patientsService.deletePatientsByPatIds(patients));
    }


}