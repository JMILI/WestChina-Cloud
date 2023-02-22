package com.westChina.ct.service.impl;

import java.util.List;

import com.westChina.ct.domain.FormHit;
import org.springframework.beans.factory.annotation.Autowired;
import com.baomidou.dynamic.datasource.annotation.DS;
import org.springframework.stereotype.Service;
import com.westChina.ct.mapper.CtPatientsMapper;
import com.westChina.ct.domain.CtPatients;
import com.westChina.ct.service.ICtPatientsService;

import static com.westChina.common.core.constant.TenantConstants.ISOLATE;

/**
 * 病人信息 业务层处理
 *
 * @author jm
 */
@Service
@DS(ISOLATE)
public class CtPatientsServiceImpl implements ICtPatientsService {

    @Autowired
    private CtPatientsMapper patientsMapper;

    /**
     * 查询病人信息列表
     *
     * @param patients 病人信息
     * @return 病人信息
     */
    @Override
    public List<CtPatients> selectPatientsList(CtPatients patients) {
        return patientsMapper.selectPatientsList(patients);
    }

    /**
     * 查询病人信息
     *
     * @param patients 病人信息 | patId 病人信息Id
     * @return 病人信息
     */
    @Override
    public CtPatients selectPatientsByPatId(CtPatients patients) {
        return patientsMapper.selectPatientsByPatId(patients);
    }

    /**
     * 新增病人信息
     *
     * @param patients 病人信息
     * @return 结果
     */
    @Override
    public int insertPatients(CtPatients patients) {
        return patientsMapper.insertPatients(patients);
    }

    /**
     * 修改病人信息
     *
     * @param patients 病人信息
     * @return 结果
     */
    @Override
    public int updatePatients(CtPatients patients) {
        return patientsMapper.updatePatients(patients);
    }

    /**
     * 修改病人信息排序
     *
     * @param patients 病人信息
     * @return 结果
     */
    @Override
    public int updatePatientsSort(CtPatients patients) {
        return patientsMapper.updatePatientsSort(patients);
    }

    /**
     * 删除病人信息信息
     *
     * @param patients 病人信息 | patId 病人信息Id
     * @return 结果
     */
    @Override
    public int deletePatientsByPatId(CtPatients patients) {
        return patientsMapper.deletePatientsByPatId(patients);
    }

    /**
     * 批量删除病人信息
     *
     * @param patients 病人信息 | params.Ids 需要删除的病人信息Ids组
     * @return 结果
     */
    @Override
    public int deletePatientsByPatIds(CtPatients patients) {
        return patientsMapper.deletePatientsByPatIds(patients);
    }

    /**
     * 如果根据手机号或身份证号找到了，就返回列表，优先根据手机号查询
     *
     * @param formHit
     * @return
     */
    @Override
    public List<CtPatients> searchByFormHit(FormHit formHit) {
        // 根据手机号查询or根据身份证号查询
        return patientsMapper.searchByFormHit(formHit);
    }
}