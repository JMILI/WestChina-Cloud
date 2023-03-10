package com.westChina.system.monitor.service;

import java.util.List;

import com.westChina.system.api.domain.monitor.SysOperLog;

/**
 * 操作日志 服务层
 *
 * @author westChina
 */
public interface ISysOperLogService {
    /**
     * 新增操作日志
     *
     * @param operLog 操作日志对象
     * @return 结果
     */
    public int insertOperlog(SysOperLog operLog);

    /**
     * 查询系统操作日志集合
     *
     * @param operLog 操作日志对象
     * @return 操作日志集合
     */
    public List<SysOperLog> selectOperLogList(SysOperLog operLog);

    /**
     * 查询操作日志详细
     *
     * @param operLog 操作日志对象 | operId 操作Id
     * @return 操作日志对象
     */
    public SysOperLog selectOperLogById(SysOperLog operLog);

    /**
     * 批量删除系统操作日志
     *
     * @param operLog 操作日志对象 | params.Ids 需要删除的登录日志Ids组
     * @return 结果
     */
    public int deleteOperLogByIds(SysOperLog operLog);

    /**
     * 清空操作日志
     */
    public void cleanOperLog();
}
