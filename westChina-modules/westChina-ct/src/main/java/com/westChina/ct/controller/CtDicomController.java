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
import com.westChina.ct.domain.CtDicom;
import com.westChina.ct.service.ICtDicomService;
import com.westChina.common.core.web.controller.BaseController;
import com.westChina.common.core.web.domain.AjaxResult;
import com.westChina.common.core.utils.poi.ExcelUtil;

/**
 * 病人dicom存储记录 业务处理
 * 
 * @author westChina
 */
@RestController
@RequestMapping("/dicom")
public class CtDicomController extends BaseController {

    @Autowired
    private ICtDicomService dicomService;

    /**
     * 查询病人dicom存储记录列表
     */
    @RequiresPermissions("ct:dicom:list")
    @GetMapping("/list")
    public AjaxResult list(CtDicom dicom) {
        startPage();
        List<CtDicom> list = dicomService.selectDicomList(dicom);
        return getDataTable(list);

    }

    /**
     * 导出病人dicom存储记录列表
     */
    @RequiresPermissions("ct:dicom:export")
    @Log(title = "病人dicom存储记录", businessType = BusinessType.EXPORT)
    @PostMapping("/export")
    public void export(HttpServletResponse response, CtDicom dicom) {
        List<CtDicom> list = dicomService.selectDicomList(dicom);
        ExcelUtil<CtDicom> util = new ExcelUtil<CtDicom>(CtDicom.class);
        util.exportExcel(response, list, "病人dicom存储记录数据");
    }

    /**
     * 获取病人dicom存储记录详细信息
     */
    @RequiresPermissions("ct:dicom:query")
    @GetMapping(value = "/byId")
    public AjaxResult getInfo(CtDicom dicom) {
        return AjaxResult.success(dicomService.selectDicomByDicomId(dicom));
    }

    /**
     * 新增病人dicom存储记录
     */
    @RequiresPermissions("ct:dicom:add")
    @Log(title = "病人dicom存储记录", businessType = BusinessType.INSERT)
    @PostMapping("/add")
    public AjaxResult add(@RequestBody CtDicom dicom) {
        return toAjax(dicomService.insertDicom(dicom));
    }

    /**
     * 修改病人dicom存储记录
     */
    @RequiresPermissions("ct:dicom:edit")
    @Log(title = "病人dicom存储记录", businessType = BusinessType.UPDATE)
    @PutMapping
    public AjaxResult edit(@RequestBody CtDicom dicom) {
        return toAjax(dicomService.updateDicom(dicom));
    }

    /**
     * 修改病人dicom存储记录排序
     */
    @RequiresPermissions("ct:dicom:edit")
    @Log(title = "病人dicom存储记录", businessType = BusinessType.UPDATE)
    @PutMapping(value = "/sort")
    public AjaxResult updateSort(@RequestBody CtDicom dicom) {
        return toAjax(dicomService.updateDicomSort(dicom));
    }

    /**
     * 删除病人dicom存储记录
     */
    @RequiresPermissions("ct:dicom:remove")
    @Log(title = "病人dicom存储记录", businessType = BusinessType.DELETE)
    @DeleteMapping
    public AjaxResult remove(@RequestBody CtDicom dicom) {
        return toAjax(dicomService.deleteDicomByDicomIds(dicom));
    }

    /**
     * 获取病人dicom存储记录详细信息
     */
    @GetMapping(value = "/getDicomByPatCardId")
    public AjaxResult getDicomByPatCardId(String patCardId) {
        List<CtDicom> list = dicomService.getDicomListByPatCardId(patCardId);
        getDataTable(list);
        return getDataTable(list);
    }
    /**
     * 根据patCardId获取该病人所有study的series列表信息
     */
    @GetMapping(value = "/getStudyListByPatCardId")
    public AjaxResult getStudyListByPatCardId(String patCardId) {
        List<CtDicom> list = dicomService.getStudyListByPatCardId(patCardId);

        return AjaxResult.success(list);
    }
}