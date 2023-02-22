package com.westChina.ct.service;

import java.util.List;
import com.westChina.ct.domain.CtPatients;
import com.westChina.ct.domain.FormHit;

/**
 * 病人信息 业务层
 * 
 * @author jm
 */
public interface ICtPatientsService {

    /**
     * 查询病人信息列表
     *
     * @param patients 病人信息
     * @return 病人信息集合
     */
    public List<CtPatients> selectPatientsList(CtPatients patients);

    /**
     * 查询病人信息
     *
     * @param patients 病人信息 | patId 病人信息Id
     * @return 病人信息
     */
    public CtPatients selectPatientsByPatId(CtPatients patients);

    /**
     * 新增病人信息
     *
     * @param patients 病人信息
     * @return 结果
     */
    public int insertPatients(CtPatients patients);

    /**
     * 修改病人信息
     *
     * @param patients 病人信息
     * @return 结果
     */
    public int updatePatients(CtPatients patients);

    /**
     * 修改病人信息排序
     *
     * @param patients 病人信息
     * @return 结果
     */
    public int updatePatientsSort(CtPatients patients);

    /**
     * 删除病人信息信息
     *
     * @param patients 病人信息 | patId 病人信息Id
     * @return 结果
     */
    public int deletePatientsByPatId(CtPatients patients);

    /**
     * 批量删除病人信息
     *
     * @param patients 病人信息 | params.Ids 需要删除的病人信息Ids组
     * @return 结果
     */
    public int deletePatientsByPatIds(CtPatients patients);

    /**
     * 根据formHit查询病人列表
     * @param formHit
     * @return
     */
    public List<CtPatients> searchByFormHit(FormHit formHit);
}