package com.westChina.ct.service;


import com.westChina.ct.domain.CtDicom;

import java.util.List;

/**
 * 病人dicom存储记录 业务层
 * 
 * @author jm
 */
public interface ICtDicomService {

    /**
     * 查询病人dicom存储记录列表
     *
     * @param ctDicom 病人dicom存储记录
     * @return 病人dicom存储记录集合
     */
    public List<CtDicom> selectCtDicomList(CtDicom ctDicom);

    /**
     * 查询病人dicom存储记录
     *
     * @param ctDicom 病人dicom存储记录 | dicomId 病人dicom存储记录Id
     * @return 病人dicom存储记录
     */
    public CtDicom selectCtDicomByDicomId(CtDicom ctDicom);

    /**
     * 新增病人dicom存储记录
     *
     * @param ctDicom 病人dicom存储记录
     * @return 结果
     */
    public int insertCtDicom(CtDicom ctDicom);

    /**
     * 修改病人dicom存储记录
     *
     * @param ctDicom 病人dicom存储记录
     * @return 结果
     */
    public int updateCtDicom(CtDicom ctDicom);

    /**
     * 修改病人dicom存储记录排序
     *
     * @param ctDicom 病人dicom存储记录
     * @return 结果
     */
    public int updateCtDicomSort(CtDicom ctDicom);

    /**
     * 删除病人dicom存储记录信息
     *
     * @param ctDicom 病人dicom存储记录 | dicomId 病人dicom存储记录Id
     * @return 结果
     */
    public int deleteCtDicomByDicomId(CtDicom ctDicom);

    /**
     * 批量删除病人dicom存储记录
     *
     * @param ctDicom 病人dicom存储记录 | params.Ids 需要删除的病人dicom存储记录Ids组
     * @return 结果
     */
    public int deleteCtDicomByDicomIds(CtDicom ctDicom);

    public List<CtDicom> getDicomListByPatCardId(String patCardId);

    public List<CtDicom> getStudyListByPatCardId(String patCardId);
}