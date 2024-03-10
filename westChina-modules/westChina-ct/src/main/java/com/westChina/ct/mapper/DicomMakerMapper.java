package com.westChina.ct.mapper;

import java.util.List;
import com.westChina.common.datascope.annotation.DataScope;
import com.westChina.ct.domain.CtDicom;
import com.westChina.ct.domain.DicomMaker;

/**
 * 病人标记过的dicom图像 数据层
 *
 * @author westChina
 */
public interface DicomMakerMapper {

    /**
     * 查询病人标记过的dicom图像列表
     * 访问控制 e 租户查询
     *
     * @param dicomMaker 病人标记过的dicom图像
     * @return 病人标记过的dicom图像集合
     */
    @DataScope( eAlias = "e" )
    public List<DicomMaker> selectDicomMakerList(DicomMaker dicomMaker);

    /**
     * 查询病人标记过的dicom图像
     * 访问控制 e 租户查询
     *
     * @param dicomMaker 病人标记过的dicom图像 | dicomMakerId 病人标记过的dicom图像Id
     * @return 病人标记过的dicom图像
     */
    @DataScope( eAlias = "e" )
    public DicomMaker selectDicomMakerByDicomMakerId(DicomMaker dicomMaker);

    /**
     * 新增病人标记过的dicom图像
     * 访问控制 empty 租户更新（无前缀）
     *
     * @param dicomMaker 病人标记过的dicom图像
     * @return 结果
     */
    @DataScope( ueAlias = "empty" )
    public int insertDicomMaker(DicomMaker dicomMaker);

    /**
     * 修改病人标记过的dicom图像
     * 访问控制 empty 租户更新（无前缀）
     *
     * @param dicomMaker 病人标记过的dicom图像
     * @return 结果
     */
    @DataScope( ueAlias = "empty" )
    public int updateDicomMaker(DicomMaker dicomMaker);

    /**
     * 修改病人标记过的dicom图像排序
     * 访问控制 empty 租户更新（无前缀）
     *
     * @param dicomMaker 病人标记过的dicom图像
     * @return 结果
     */
    @DataScope( ueAlias = "empty" )
    public int updateDicomMakerSort(DicomMaker dicomMaker);

    /**
     * 删除病人标记过的dicom图像
     * 访问控制 empty 租户更新（无前缀）
     *
     * @param dicomMaker 病人标记过的dicom图像 | dicomMakerId 病人标记过的dicom图像Id
     * @return 结果
     */
    @DataScope( ueAlias = "empty" )
    public int deleteDicomMakerByDicomMakerId(DicomMaker dicomMaker);

    /**
     * 批量删除病人标记过的dicom图像
     * 访问控制 empty 租户更新（无前缀）
     *
     * @param dicomMaker 病人标记过的dicom图像 | params.Ids 需要删除的病人标记过的dicom图像Ids组
     * @return 结果
     */
    @DataScope( ueAlias = "empty" )
    public int deleteDicomMakerByDicomMakerIds(DicomMaker dicomMaker);



    @DataScope( eAlias = "e" )
    public List<DicomMaker> getDicomMakerByPatCardId(DicomMaker dicomMaker);

}