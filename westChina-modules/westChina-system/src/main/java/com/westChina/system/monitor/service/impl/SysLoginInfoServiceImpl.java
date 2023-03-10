package com.westChina.system.monitor.service.impl;

import com.baomidou.dynamic.datasource.annotation.DS;
import com.westChina.system.api.domain.monitor.SysLoginInfo;
import com.westChina.system.monitor.mapper.SysLoginInfoMapper;
import com.westChina.system.monitor.service.ISysLoginInfoService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

import static com.westChina.common.core.constant.TenantConstants.ISOLATE;

/**
 * 系统访问日志情况信息 服务层处理
 *
 * @author westChina
 */
@Service
@DS(ISOLATE)
public class SysLoginInfoServiceImpl implements ISysLoginInfoService {

    @Autowired
    private SysLoginInfoMapper loginInfoMapper;

    /**
     * 新增系统登录日志
     *
     * @param sourceName 数据源名称
     * @param loginInfo  访问日志对象
     */
    @Override
    @DS("#sourceName")
    public int insertLoginInfo(String sourceName, SysLoginInfo loginInfo) {
        return loginInfoMapper.insertLoginInfo(loginInfo);
    }

    /**
     * 查询系统登录日志集合
     *
     * @param loginInfo 访问日志对象
     * @return 登录记录集合
     */
    @Override
    public List<SysLoginInfo> selectLoginInfoList(SysLoginInfo loginInfo) {
        return loginInfoMapper.selectLoginInfoList(loginInfo);
    }

    /**
     * 批量删除系统登录日志
     *
     * @param loginInfo 访问日志对象 | params.Ids 需要删除的登录日志Ids组
     * @return 结果
     */
    @Override
    public int deleteLoginInfoByIds(SysLoginInfo loginInfo) {
        return loginInfoMapper.deleteLoginInfoByIds(loginInfo);
    }

    /**
     * 清空系统登录日志
     */
    @Override
    public void cleanLoginInfo() {
        loginInfoMapper.cleanLoginInfo(new SysLoginInfo());
    }
}
