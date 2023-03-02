package com.westChina.ct.service;

import java.util.List;
import com.westChina.ct.domain.DicomMaker;

/**
 * 病人标记过的dicom图像 业务层
 * 
 * @author westChina
 */
public interface IDicomMakerService {

    /**
     * 查询病人标记过的dicom图像列表
     *
     * @param dicomMaker 病人标记过的dicom图像
     * @return 病人标记过的dicom图像集合
     */
    public List<DicomMaker> selectDicomMakerList(DicomMaker dicomMaker);

    /**
     * 查询病人标记过的dicom图像
     *
     * @param dicomMaker 病人标记过的dicom图像 | dicomMakerId 病人标记过的dicom图像Id
     * @return 病人标记过的dicom图像
     */
    public DicomMaker selectDicomMakerByDicomMakerId(DicomMaker dicomMaker);

    /**
     * 新增病人标记过的dicom图像
     *
     * @param dicomMaker 病人标记过的dicom图像
     * @return 结果
     */
    public int insertDicomMaker(DicomMaker dicomMaker);

    /**
     * 修改病人标记过的dicom图像
     *
     * @param dicomMaker 病人标记过的dicom图像
     * @return 结果
     */
    public int updateDicomMaker(DicomMaker dicomMaker);

    /**
     * 修改病人标记过的dicom图像排序
     *
     * @param dicomMaker 病人标记过的dicom图像
     * @return 结果
     */
    public int updateDicomMakerSort(DicomMaker dicomMaker);

    /**
     * 删除病人标记过的dicom图像信息
     *
     * @param dicomMaker 病人标记过的dicom图像 | dicomMakerId 病人标记过的dicom图像Id
     * @return 结果
     */
    public int deleteDicomMakerByDicomMakerId(DicomMaker dicomMaker);

    /**
     * 批量删除病人标记过的dicom图像
     *
     * @param dicomMaker 病人标记过的dicom图像 | params.Ids 需要删除的病人标记过的dicom图像Ids组
     * @return 结果
     */
    public int deleteDicomMakerByDicomMakerIds(DicomMaker dicomMaker);

    List<DicomMaker> getDicomMakerByPatCardId(String patCardId);
}