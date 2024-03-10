package com.westChina.ct.service.impl;

import java.util.List;
import org.springframework.beans.factory.annotation.Autowired;
import com.baomidou.dynamic.datasource.annotation.DS;
import org.springframework.stereotype.Service;
import com.westChina.ct.mapper.DicomMakerMapper;
import com.westChina.ct.domain.DicomMaker;
import com.westChina.ct.service.IDicomMakerService;
import static com.westChina.common.core.constant.TenantConstants.ISOLATE;

/**
 * 病人标记过的dicom图像 业务层处理
 *
 * @author westChina
 */
@Service
@DS(ISOLATE)
public class DicomMakerServiceImpl implements IDicomMakerService {

    @Autowired
    private DicomMakerMapper dicomMakerMapper;

    /**
     * 查询病人标记过的dicom图像列表
     *
     * @param dicomMaker 病人标记过的dicom图像
     * @return 病人标记过的dicom图像
     */
    @Override
    public List<DicomMaker> selectDicomMakerList(DicomMaker dicomMaker)
    {
        return dicomMakerMapper.selectDicomMakerList(dicomMaker);
    }

    /**
     * 查询病人标记过的dicom图像
     *
     * @param dicomMaker 病人标记过的dicom图像 | dicomMakerId 病人标记过的dicom图像Id
     * @return 病人标记过的dicom图像
     */
    @Override
    public DicomMaker selectDicomMakerByDicomMakerId(DicomMaker dicomMaker)
    {
        return dicomMakerMapper.selectDicomMakerByDicomMakerId(dicomMaker);
    }

    /**
     * 新增病人标记过的dicom图像
     *
     * @param dicomMaker 病人标记过的dicom图像
     * @return 结果
     */
    @Override
    public int insertDicomMaker(DicomMaker dicomMaker)
    {
        return dicomMakerMapper.insertDicomMaker(dicomMaker);
    }

    /**
     * 修改病人标记过的dicom图像
     *
     * @param dicomMaker 病人标记过的dicom图像
     * @return 结果
     */
    @Override
    public int updateDicomMaker(DicomMaker dicomMaker)
    {
        return dicomMakerMapper.updateDicomMaker(dicomMaker);
    }

    /**
     * 修改病人标记过的dicom图像排序
     *
     * @param dicomMaker 病人标记过的dicom图像
     * @return 结果
     */
    @Override
    public int updateDicomMakerSort(DicomMaker dicomMaker){
        return dicomMakerMapper.updateDicomMakerSort(dicomMaker);
    }

    /**
     * 删除病人标记过的dicom图像信息
     *
     * @param dicomMaker 病人标记过的dicom图像 | dicomMakerId 病人标记过的dicom图像Id
     * @return 结果
     */
    @Override
    public int deleteDicomMakerByDicomMakerId(DicomMaker dicomMaker)
    {
        return dicomMakerMapper.deleteDicomMakerByDicomMakerId(dicomMaker);
    }

    /**
     * 批量删除病人标记过的dicom图像
     *
     * @param dicomMaker 病人标记过的dicom图像 | params.Ids 需要删除的病人标记过的dicom图像Ids组
     * @return 结果
     */
    @Override
    public int deleteDicomMakerByDicomMakerIds(DicomMaker dicomMaker)
    {
        System.out.println("-----"+dicomMaker.toString());
        return dicomMakerMapper.deleteDicomMakerByDicomMakerIds(dicomMaker);
    }

    @Override
    public List<DicomMaker> getDicomMakerByPatCardId(String patCardId) {
        DicomMaker dicomMaker = new DicomMaker();
        dicomMaker.setPatCardId(patCardId);
        return dicomMakerMapper.getDicomMakerByPatCardId(dicomMaker);
    }
}