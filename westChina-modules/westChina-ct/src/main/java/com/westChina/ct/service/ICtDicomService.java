package com.westChina.ct.service;

import java.util.List;

import com.westChina.ct.domain.CtDicom;

/**
 * 病人dicom存储记录 业务层
 *
 * @author westChina
 */
public interface ICtDicomService {

    /**
     * 查询病人dicom存储记录列表
     *
     * @param dicom 病人dicom存储记录
     * @return 病人dicom存储记录集合
     */
    public List<CtDicom> selectDicomList(CtDicom dicom);

    /**
     * 查询病人dicom存储记录
     *
     * @param dicom 病人dicom存储记录 | dicomId 病人dicom存储记录Id
     * @return 病人dicom存储记录
     */
    public CtDicom selectDicomByDicomId(CtDicom dicom);

    /**
     * 新增病人dicom存储记录
     *
     * @param dicom 病人dicom存储记录
     * @return 结果
     */
    public int insertDicom(CtDicom dicom);

    /**
     * 修改病人dicom存储记录
     *
     * @param dicom 病人dicom存储记录
     * @return 结果
     */
    public int updateDicom(CtDicom dicom);

    /**
     * 修改病人dicom存储记录排序
     *
     * @param dicom 病人dicom存储记录
     * @return 结果
     */
    public int updateDicomSort(CtDicom dicom);

    /**
     * 删除病人dicom存储记录信息
     *
     * @param dicom 病人dicom存储记录 | dicomId 病人dicom存储记录Id
     * @return 结果
     */
    public int deleteDicomByDicomId(CtDicom dicom);

    /**
     * 批量删除病人dicom存储记录
     *
     * @param dicom 病人dicom存储记录 | params.Ids 需要删除的病人dicom存储记录Ids组
     * @return 结果
     */
    public int deleteDicomByDicomIds(CtDicom dicom);


    //自己写的方法
    public List<CtDicom> getDicomListByPatCardId(String patCardId);

    public List<CtDicom> getStudyListByPatCardId(String patCardId);

}