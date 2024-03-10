package com.westChina.ct.mapper;

import java.util.List;
import com.westChina.common.datascope.annotation.DataScope;
import com.westChina.ct.domain.CtPatients;
import com.westChina.ct.domain.FormHit;

/**
 * 病人信息 数据层
 *
 * @author jm
 */
public interface CtPatientsMapper {

    /**
     * 查询病人信息列表
     * 访问控制 e 租户查询
     *
     * @param patients 病人信息
     * @return 病人信息集合
     */
    @DataScope( eAlias = "e")
    public List<CtPatients> selectPatientsList(CtPatients patients);

    /**
     * 查询病人信息
     * 访问控制 e 租户查询
     *
     * @param patients 病人信息 | patId 病人信息Id
     * @return 病人信息
     */
    @DataScope( eAlias = "e")
    public CtPatients selectPatientsByPatId(CtPatients patients);

    /**
     * 新增病人信息
    * 访问控制 empty 租户更新（无前缀）
     *
     * @param patients 病人信息
     * @return 结果
     */
    @DataScope( ueAlias = "empty" )
    public int insertPatients(CtPatients patients);

    /**
     * 修改病人信息
     * 访问控制 empty 租户更新（无前缀）
     *
     * @param patients 病人信息
     * @return 结果
     */
    @DataScope( ueAlias = "empty" )
    public int updatePatients(CtPatients patients);

    /**
     * 修改病人信息排序
     * 访问控制 empty 租户更新（无前缀）
     *
     * @param patients 病人信息
     * @return 结果
     */
    @DataScope( ueAlias = "empty" )
    public int updatePatientsSort(CtPatients patients);

    /**
     * 删除病人信息
     * 访问控制 empty 租户更新（无前缀）
     *
     * @param patients 病人信息 | patId 病人信息Id
     * @return 结果
     */
    @DataScope( ueAlias = "empty" )
    public int deletePatientsByPatId(CtPatients patients);

    /**
     * 批量删除病人信息
     * 访问控制 empty 租户更新（无前缀）
     *
     * @param patients 病人信息 | params.Ids 需要删除的病人信息Ids组
     * @return 结果
     */
    @DataScope( ueAlias = "empty" )
    public int deletePatientsByPatIds(CtPatients patients);

    /**
     * 如果根据手机号或身份证号找到了，就返回列表，优先根据手机号查询
     *
     * @param formHit
     * @return
     */
    public List<CtPatients> searchByFormHit(FormHit formHit);
}