package com.westChina.ct.controller;

import java.util.Collections;
import java.util.List;
import java.util.Map;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import com.westChina.common.core.web.controller.BaseController;
import com.westChina.common.core.web.domain.AjaxResult;
import com.westChina.common.log.annotation.Log;
import com.westChina.common.log.enums.BusinessType;
import com.westChina.ct.domain.DicomAiLesion;
import com.westChina.ct.service.IDicomAiLesionService;

/**
 * AI识别病灶结果 业务处理
 */
@RestController
@RequestMapping("/aiLesion")
public class DicomAiLesionController extends BaseController {

    @Autowired
    private IDicomAiLesionService dicomAiLesionService;

    @GetMapping("/list")
    public AjaxResult list(DicomAiLesion dicomAiLesion) {
        startPage();
        List<DicomAiLesion> list = dicomAiLesionService.selectDicomAiLesionList(dicomAiLesion);
        return getDataTable(list);
    }

    @GetMapping("/byId")
    public AjaxResult getInfo(DicomAiLesion dicomAiLesion) {
        return AjaxResult.success(dicomAiLesionService.selectDicomAiLesionById(dicomAiLesion));
    }

    @GetMapping("/getByPatCardId")
    public AjaxResult getByPatCardId(String patCardId) {
        List<DicomAiLesion> list = dicomAiLesionService.getDicomAiLesionByPatCardId(patCardId);
        return AjaxResult.success(list == null ? Collections.emptyList() : list);
    }

    @Log(title = "保存AI识别病灶结果", businessType = BusinessType.INSERT)
    @PostMapping("/save")
    public AjaxResult save(@RequestBody Map<String, Object> body) {
        try {
            DicomAiLesion saved = dicomAiLesionService.saveLesionResult(body);
            return AjaxResult.success(saved);
        } catch (IllegalArgumentException ex) {
            return AjaxResult.error(ex.getMessage());
        } catch (IllegalStateException ex) {
            return AjaxResult.error(ex.getMessage());
        } catch (Exception ex) {
            return AjaxResult.error("保存 AI 识别结果失败：" + ex.getMessage());
        }
    }

    @Log(title = "修改AI识别病灶结果", businessType = BusinessType.UPDATE)
    @PutMapping
    public AjaxResult edit(@RequestBody DicomAiLesion dicomAiLesion) {
        return toAjax(dicomAiLesionService.updateDicomAiLesion(dicomAiLesion));
    }

    @Log(title = "删除AI识别病灶结果", businessType = BusinessType.DELETE)
    @DeleteMapping
    public AjaxResult remove(@RequestBody DicomAiLesion dicomAiLesion) {
        return toAjax(dicomAiLesionService.deleteDicomAiLesionByIds(dicomAiLesion));
    }
}
