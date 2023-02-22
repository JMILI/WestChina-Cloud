package com.westChina.ct.service.impl;

import com.baomidou.dynamic.datasource.annotation.DS;
import com.westChina.ct.domain.CtDicom;
import com.westChina.ct.mapper.CtDicomMapper;
import com.westChina.ct.service.ICtDicomService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

import static com.westChina.common.core.constant.TenantConstants.ISOLATE;

/**
 * 病人dicom存储记录 业务层处理
 *
 * @author jm
 */
@Service
@DS(ISOLATE)
public class CtDicomServiceImpl implements ICtDicomService {

    @Autowired
    private CtDicomMapper ctDicomMapper;

    /**
     * 查询病人dicom存储记录列表
     *
     * @param ctDicom 病人dicom存储记录
     * @return 病人dicom存储记录
     */
    @Override
    public List<CtDicom> selectCtDicomList(CtDicom ctDicom)
    {
        return ctDicomMapper.selectCtDicomList(ctDicom);
    }

    /**
     * 查询病人dicom存储记录
     *
     * @param ctDicom 病人dicom存储记录 | dicomId 病人dicom存储记录Id
     * @return 病人dicom存储记录
     */
    @Override
    public CtDicom selectCtDicomByDicomId(CtDicom ctDicom)
    {
        return ctDicomMapper.selectCtDicomByDicomId(ctDicom);
    }

    /**
     * 新增病人dicom存储记录
     *
     * @param ctDicom 病人dicom存储记录
     * @return 结果
     */
    @Override
    public int insertCtDicom(CtDicom ctDicom)
    {
        return ctDicomMapper.insertCtDicom(ctDicom);
    }

    /**
     * 修改病人dicom存储记录
     *
     * @param ctDicom 病人dicom存储记录
     * @return 结果
     */
    @Override
    public int updateCtDicom(CtDicom ctDicom)
    {
        return ctDicomMapper.updateCtDicom(ctDicom);
    }

    /**
     * 修改病人dicom存储记录排序
     *
     * @param ctDicom 病人dicom存储记录
     * @return 结果
     */
    @Override
    public int updateCtDicomSort(CtDicom ctDicom){
        return ctDicomMapper.updateCtDicomSort(ctDicom);
    }

    /**
     * 删除病人dicom存储记录信息
     *
     * @param ctDicom 病人dicom存储记录 | dicomId 病人dicom存储记录Id
     * @return 结果
     */
    @Override
    public int deleteCtDicomByDicomId(CtDicom ctDicom)
    {
        return ctDicomMapper.deleteCtDicomByDicomId(ctDicom);
    }

    /**
     * 批量删除病人dicom存储记录
     *
     * @param ctDicom 病人dicom存储记录 | params.Ids 需要删除的病人dicom存储记录Ids组
     * @return 结果
     */
    @Override
    public int deleteCtDicomByDicomIds(CtDicom ctDicom)
    {
        return ctDicomMapper.deleteCtDicomByDicomIds(ctDicom);
    }

    @Override
    public List<CtDicom> getDicomListByPatCardId(String patCardId) {
        CtDicom ctDicom = new CtDicom();
        ctDicom.setPatCardId(patCardId);
        return ctDicomMapper.getDicomListByPatCardId(ctDicom);
    }

    @Override
    public List<CtDicom> getStudyListByPatCardId(String patCardId) {
        CtDicom ctDicom = new CtDicom();
        ctDicom.setPatCardId(patCardId);
        return ctDicomMapper.getDicomListByPatCardId(ctDicom);
    }
}