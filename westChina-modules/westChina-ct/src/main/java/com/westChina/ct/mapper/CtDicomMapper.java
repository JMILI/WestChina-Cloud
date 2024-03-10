package com.westChina.ct.mapper;

import java.util.List;
import com.westChina.common.datascope.annotation.DataScope;
import com.westChina.ct.domain.CtDicom;

/**
 * 病人dicom存储记录 数据层
 *
 * @author westChina
 */
public interface CtDicomMapper {

    /**
     * 查询病人dicom存储记录列表
     * 访问控制 e 租户查询
     *
     * @param dicom 病人dicom存储记录
     * @return 病人dicom存储记录集合
     */
    @DataScope( eAlias = "e")
    public List<CtDicom> selectDicomList(CtDicom dicom);

    /**
     * 查询病人dicom存储记录
     * 访问控制 e 租户查询
     *
     * @param dicom 病人dicom存储记录 | dicomId 病人dicom存储记录Id
     * @return 病人dicom存储记录
     */
    @DataScope( eAlias = "e")
    public CtDicom selectDicomByDicomId(CtDicom dicom);

    /**
     * 新增病人dicom存储记录
    * 访问控制 empty 租户更新（无前缀）
     *
     * @param dicom 病人dicom存储记录
     * @return 结果
     */
    @DataScope( ueAlias = "empty" )
    public int insertDicom(CtDicom dicom);

    /**
     * 修改病人dicom存储记录
     * 访问控制 empty 租户更新（无前缀）
     *
     * @param dicom 病人dicom存储记录
     * @return 结果
     */
    @DataScope( ueAlias = "empty" )
    public int updateDicom(CtDicom dicom);

    /**
     * 修改病人dicom存储记录排序
     * 访问控制 empty 租户更新（无前缀）
     *
     * @param dicom 病人dicom存储记录
     * @return 结果
     */
    @DataScope( ueAlias = "empty" )
    public int updateDicomSort(CtDicom dicom);

    /**
     * 删除病人dicom存储记录
     * 访问控制 empty 租户更新（无前缀）
     *
     * @param dicom 病人dicom存储记录 | dicomId 病人dicom存储记录Id
     * @return 结果
     */
    @DataScope( ueAlias = "empty" )
    public int deleteDicomByDicomId(CtDicom dicom);

    /**
     * 批量删除病人dicom存储记录
     * 访问控制 empty 租户更新（无前缀）
     *
     * @param dicom 病人dicom存储记录 | params.Ids 需要删除的病人dicom存储记录Ids组
     * @return 结果
     */
    @DataScope( ueAlias = "empty" )
    public int deleteDicomByDicomIds(CtDicom dicom);

    @DataScope( eAlias = "e" )
    public List<CtDicom> getDicomListByPatCardId(CtDicom ctDicom);

}