package com.westChina.ct.controller;

import java.util.List;
import java.io.IOException;
import javax.servlet.http.HttpServletResponse;

import com.westChina.ct.domain.CtDicom;
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
import com.westChina.ct.domain.DicomMaker;
import com.westChina.ct.service.IDicomMakerService;
import com.westChina.common.core.web.controller.BaseController;
import com.westChina.common.core.web.domain.AjaxResult;
import com.westChina.common.core.utils.poi.ExcelUtil;

/**
 * 病人标记过的dicom图像 业务处理
 * 
 * @author westChina
 */
@RestController
@RequestMapping("/maker")
public class DicomMakerController extends BaseController {

    @Autowired
    private IDicomMakerService dicomMakerService;

    /**
     * 查询病人标记过的dicom图像列表
     */
    @RequiresPermissions("ct:maker:list")
    @GetMapping("/list")
    public AjaxResult list(DicomMaker dicomMaker) {
        startPage();
        List<DicomMaker> list = dicomMakerService.selectDicomMakerList(dicomMaker);
        return getDataTable(list);
    }

    /**
     * 导出病人标记过的dicom图像列表
     */
    @RequiresPermissions("ct:maker:export")
    @Log(title = "病人标记过的dicom图像", businessType = BusinessType.EXPORT)
    @PostMapping("/export")
    public void export(HttpServletResponse response, DicomMaker dicomMaker) {
        List<DicomMaker> list = dicomMakerService.selectDicomMakerList(dicomMaker);
        ExcelUtil<DicomMaker> util = new ExcelUtil<DicomMaker>(DicomMaker.class);
        util.exportExcel(response, list, "病人标记过的dicom图像数据");
    }

    /**
     * 获取病人标记过的dicom图像详细信息
     */
    @RequiresPermissions("ct:maker:query")
    @GetMapping(value = "/byId")
    public AjaxResult getInfo(DicomMaker dicomMaker) {
        return AjaxResult.success(dicomMakerService.selectDicomMakerByDicomMakerId(dicomMaker));
    }

    /**
     * 新增病人标记过的dicom图像
     */
    @RequiresPermissions("ct:maker:add")
    @Log(title = "病人标记过的dicom图像", businessType = BusinessType.INSERT)
    @PostMapping
    public AjaxResult add(@RequestBody DicomMaker dicomMaker) {
        return toAjax(dicomMakerService.insertDicomMaker(dicomMaker));
    }

    /**
     * 修改病人标记过的dicom图像
     */
    @RequiresPermissions("ct:maker:edit")
    @Log(title = "病人标记过的dicom图像", businessType = BusinessType.UPDATE)
    @PutMapping
    public AjaxResult edit(@RequestBody DicomMaker dicomMaker) {
        return toAjax(dicomMakerService.updateDicomMaker(dicomMaker));
    }

    /**
     * 修改病人标记过的dicom图像排序
     */
    @RequiresPermissions("ct:maker:edit")
    @Log(title = "病人标记过的dicom图像", businessType = BusinessType.UPDATE)
    @PutMapping(value = "/sort")
    public AjaxResult updateSort(@RequestBody DicomMaker dicomMaker) {
        return toAjax(dicomMakerService.updateDicomMakerSort(dicomMaker));
    }

    /**
     * 删除病人标记过的dicom图像
     */
    @RequiresPermissions("ct:maker:remove")
    @Log(title = "病人标记过的dicom图像", businessType = BusinessType.DELETE)
    @DeleteMapping
    public AjaxResult remove(@RequestBody DicomMaker dicomMaker) {
        return toAjax(dicomMakerService.deleteDicomMakerByDicomMakerIds(dicomMaker));
    }

    /**
     * 获取病人dicom存储记录详细信息
     */
    @GetMapping(value = "/getDicomMakerByPatCardId")
    public AjaxResult getDicomMakerByPatCardId(String patCardId) {
        System.out.println(patCardId);
        List<DicomMaker> list = dicomMakerService.getDicomMakerByPatCardId(patCardId);
        getDataTable(list);
        return getDataTable(list);
    }


}