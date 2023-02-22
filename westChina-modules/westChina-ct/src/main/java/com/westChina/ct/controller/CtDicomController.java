package com.westChina.ct.controller;

import cn.hutool.json.JSONObject;
import com.westChina.common.core.utils.poi.ExcelUtil;
import com.westChina.common.core.utils.StringUtils;
import com.westChina.common.core.web.controller.BaseController;
import com.westChina.common.core.web.domain.AjaxResult;
import com.westChina.common.log.annotation.Log;
import com.westChina.common.log.enums.BusinessType;
import com.westChina.common.security.annotation.RequiresPermissions;
import com.westChina.ct.domain.CtDicom;
import com.westChina.ct.service.ICtDicomService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import javax.servlet.http.HttpServletResponse;
import java.util.Iterator;
import java.util.List;

/**
 * 病人dicom存储记录 业务处理
 *
 * @author jm
 */
@RestController
@RequestMapping("/dicom")
public class CtDicomController extends BaseController {

    @Autowired
    private ICtDicomService ctDicomService;

    /**
     * 查询病人dicom存储记录列表
     */
    @GetMapping("/list")
    public AjaxResult list(CtDicom ctDicom) {
        startPage();
        List<CtDicom> list = ctDicomService.selectCtDicomList(ctDicom);
        return getDataTable(list);
    }

    /**
     * 导出病人dicom存储记录列表
     */
    @Log(title = "病人dicom存储记录", businessType = BusinessType.EXPORT)
    @PostMapping("/export")
    public void export(HttpServletResponse response, CtDicom ctDicom) {
        List<CtDicom> list = ctDicomService.selectCtDicomList(ctDicom);
        ExcelUtil<CtDicom> util = new ExcelUtil<CtDicom>(CtDicom.class);
        util.exportExcel(response, list, "病人dicom存储记录数据");
    }

    /**
     * 获取病人dicom存储记录详细信息
     */
    @GetMapping(value = "/byId")
    public AjaxResult getInfo(CtDicom ctDicom) {
        return AjaxResult.success(ctDicomService.selectCtDicomByDicomId(ctDicom));
    }

    /**
     * 获取病人dicom存储记录详细信息
     */
    @GetMapping(value = "/getDicomListByPatCardId")
    public AjaxResult getDicomListByPatCardId(String patCardId) {
        List<CtDicom> list = ctDicomService.getDicomListByPatCardId(patCardId);
        getDataTable(list);
        return getDataTable(list);
    }

    /**
     * 新增病人dicom存储记录
     */
    @Log(title = "病人dicom存储记录", businessType = BusinessType.INSERT)
    @PostMapping("/add")
    public AjaxResult add(@RequestBody CtDicom ctDicom) {
        return toAjax(ctDicomService.insertCtDicom(ctDicom));
    }

    /**
     * 修改病人dicom存储记录
     */
    @Log(title = "病人dicom存储记录", businessType = BusinessType.UPDATE)
    @PutMapping
    public AjaxResult edit(@RequestBody CtDicom ctDicom) {
        return toAjax(ctDicomService.updateCtDicom(ctDicom));
    }

    /**
     * 修改病人dicom存储记录排序
     */
    @RequiresPermissions("dicom:dicom:edit")
    @Log(title = "病人dicom存储记录", businessType = BusinessType.UPDATE)
    @PutMapping(value = "/sort")
    public AjaxResult updateSort(@RequestBody CtDicom ctDicom) {
        return toAjax(ctDicomService.updateCtDicomSort(ctDicom));
    }

    /**
     * 删除病人dicom存储记录
     */
    @Log(title = "病人dicom存储记录", businessType = BusinessType.DELETE)
    @DeleteMapping
    public AjaxResult remove(@RequestBody CtDicom ctDicom) {
        return toAjax(ctDicomService.deleteCtDicomByDicomIds(ctDicom));
    }


    /**
     * 根据patCardId获取该病人所有study的series列表信息
     */
    @GetMapping(value = "/getStudyListByPatCardId")
    public AjaxResult getStudyListByPatCardId(String patCardId) {
        List<CtDicom> list = ctDicomService.getStudyListByPatCardId(patCardId);
        // if (StringUtils.isEmpty(list)) {
        //     return AjaxResult.error("尚未成功查询到病人study列表");
        // } else {
        //     JSONObject jsonFather = new JSONObject();
        //     for (int i = 0; i < list.size(); i++) {
        //         System.out.printf(list.get(i).getDicomCtStudyUid());
        //         String studyUid = list.get(i).getDicomCtStudyUid();
        //         String seriesUid = list.get(i).getDicomCtSeriesUid();
        //         //包含studyUid
        //         if (jsonFather.containsKey(studyUid)) {
        //
        //             // if (jsonFather.get(studyUid)){
        //             //
        //             // }
        //             if (jsonFather.get()){
        //
        //             }
        //         } else {
        //             //既没有study也没有series
        //             JSONObject jsonStudy = new JSONObject();
        //             JSONObject jsonSeries = new JSONObject();
        //             // jsonSeries.append(list.get(i).getDicomId().toString(),list.get(i).getDicomId());
        //             // jsonSeries.append(list.get(i).getPatCardId(),list.get(i).getPatCardId());
        //             // jsonSeries.append(list.get(i).getDicomCtStudyUid(),list.get(i).getDicomCtStudyUid());
        //             // jsonSeries.append(list.get(i).getDicomCtSeriesUid(),list.get(i).getDicomCtSeriesUid());
        //             // jsonSeries.append(list.get(i).getDicomCtBody(),list.get(i).getDicomCtBody());
        //             // jsonSeries.append(list.get(i).getDicomCtPath(),list.get(i).getDicomCtPath());
        //             //CtSeriesUid:CtDicom(对象）
        //             // jsonSeries.append(list.get(i).getDicomCtSeriesUid(),list.get(i));
        //             //CtSeriesUid:CtDicom(对象）
        //             jsonStudy.append(list.get(i).getDicomCtSeriesUid(), list.get(i));
        //             //
        //             jsonFather.append(list.get(i).getDicomCtStudyUid(), jsonStudy);
        //         }
        //     }
        //     return AjaxResult.success("", jsonFather);
        // }
        return AjaxResult.success(list);
    }
}