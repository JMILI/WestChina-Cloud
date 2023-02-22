package com.westChina.ct.mapper;

import com.westChina.common.datascope.annotation.DataScope;
import com.westChina.ct.domain.CtDicom;

import java.util.List;

/**
 * 病人dicom存储记录 数据层
 *
 * @author jm
 */
public interface CtDicomMapper {

    /**
     * 查询病人dicom存储记录列表
     * 访问控制 e 租户查询
     *
     * @param ctDicom 病人dicom存储记录
     * @return 病人dicom存储记录集合
     */
    @DataScope( eAlias = "e" )
    public List<CtDicom> selectCtDicomList(CtDicom ctDicom);

    /**
     * 查询病人dicom存储记录
     * 访问控制 e 租户查询
     *
     * @param ctDicom 病人dicom存储记录 | dicomId 病人dicom存储记录Id
     * @return 病人dicom存储记录
     */
    @DataScope( eAlias = "e" )
    public CtDicom selectCtDicomByDicomId(CtDicom ctDicom);

    /**
     * 新增病人dicom存储记录
    * 访问控制 empty 租户更新（无前缀）
     *
     * @param ctDicom 病人dicom存储记录
     * @return 结果
     */
    @DataScope( ueAlias = "empty" )
    public int insertCtDicom(CtDicom ctDicom);

    /**
     * 修改病人dicom存储记录
     * 访问控制 empty 租户更新（无前缀）
     *
     * @param ctDicom 病人dicom存储记录
     * @return 结果
     */
    @DataScope( ueAlias = "empty" )
    public int updateCtDicom(CtDicom ctDicom);

    /**
     * 修改病人dicom存储记录排序
     * 访问控制 empty 租户更新（无前缀）
     *
     * @param ctDicom 病人dicom存储记录
     * @return 结果
     */
    @DataScope( ueAlias = "empty" )
    public int updateCtDicomSort(CtDicom ctDicom);

    /**
     * 删除病人dicom存储记录
     * 访问控制 empty 租户更新（无前缀）
     *
     * @param ctDicom 病人dicom存储记录 | dicomId 病人dicom存储记录Id
     * @return 结果
     */
    @DataScope( ueAlias = "empty" )
    public int deleteCtDicomByDicomId(CtDicom ctDicom);

    /**
     * 批量删除病人dicom存储记录
     * 访问控制 empty 租户更新（无前缀）
     *
     * @param ctDicom 病人dicom存储记录 | params.Ids 需要删除的病人dicom存储记录Ids组
     * @return 结果
     */
    @DataScope( ueAlias = "empty" )
    public int deleteCtDicomByDicomIds(CtDicom ctDicom);

    @DataScope( eAlias = "e" )
    public List<CtDicom> getDicomListByPatCardId(CtDicom ctDicom);
}