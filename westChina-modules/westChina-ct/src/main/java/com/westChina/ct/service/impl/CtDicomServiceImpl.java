package com.westChina.ct.service.impl;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import com.baomidou.dynamic.datasource.annotation.DS;
import org.springframework.stereotype.Service;
import com.westChina.ct.mapper.CtDicomMapper;
import com.westChina.ct.domain.CtDicom;
import com.westChina.ct.service.ICtDicomService;

import static com.westChina.common.core.constant.TenantConstants.ISOLATE;

/**
 * 病人dicom存储记录 业务层处理
 *
 * @author westChina
 */
@Service
@DS(ISOLATE)
public class CtDicomServiceImpl implements ICtDicomService {

    @Autowired
    private CtDicomMapper dicomMapper;

    /**
     * 查询病人dicom存储记录列表
     *
     * @param dicom 病人dicom存储记录
     * @return 病人dicom存储记录
     */
    @Override
    public List<CtDicom> selectDicomList(CtDicom dicom) {
        return dicomMapper.selectDicomList(dicom);
    }

    /**
     * 查询病人dicom存储记录
     *
     * @param dicom 病人dicom存储记录 | dicomId 病人dicom存储记录Id
     * @return 病人dicom存储记录
     */
    @Override
    public CtDicom selectDicomByDicomId(CtDicom dicom) {
        return dicomMapper.selectDicomByDicomId(dicom);
    }

    /**
     * 新增病人dicom存储记录
     *
     * @param dicom 病人dicom存储记录
     * @return 结果
     */
    @Override
    public int insertDicom(CtDicom dicom) {
        return dicomMapper.insertDicom(dicom);
    }

    /**
     * 修改病人dicom存储记录
     *
     * @param dicom 病人dicom存储记录
     * @return 结果
     */
    @Override
    public int updateDicom(CtDicom dicom) {
        return dicomMapper.updateDicom(dicom);
    }

    /**
     * 修改病人dicom存储记录排序
     *
     * @param dicom 病人dicom存储记录
     * @return 结果
     */
    @Override
    public int updateDicomSort(CtDicom dicom) {
        return dicomMapper.updateDicomSort(dicom);
    }

    /**
     * 删除病人dicom存储记录信息
     *
     * @param dicom 病人dicom存储记录 | dicomId 病人dicom存储记录Id
     * @return 结果
     */
    @Override
    public int deleteDicomByDicomId(CtDicom dicom) {
        return dicomMapper.deleteDicomByDicomId(dicom);
    }

    /**
     * 批量删除病人dicom存储记录
     *
     * @param dicom 病人dicom存储记录 | params.Ids 需要删除的病人dicom存储记录Ids组
     * @return 结果
     */
    @Override
    public int deleteDicomByDicomIds(CtDicom dicom) {
        return dicomMapper.deleteDicomByDicomIds(dicom);
    }


    //    自己写的
    @Override
    public List<CtDicom> getDicomListByPatCardId(String patCardId) {
        CtDicom ctDicom = new CtDicom();
        ctDicom.setPatCardId(patCardId);
        return dicomMapper.getDicomListByPatCardId(ctDicom);
    }

    @Override
    public List<CtDicom> getStudyListByPatCardId(String patCardId) {
        CtDicom ctDicom = new CtDicom();
        ctDicom.setPatCardId(patCardId);
        return dicomMapper.getDicomListByPatCardId(ctDicom);
    }
}