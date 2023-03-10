package com.westChina.system.api.feign;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import com.westChina.common.core.constant.SecurityConstants;
import com.westChina.common.core.constant.ServiceConstants;
import com.westChina.common.core.domain.R;
import com.westChina.system.api.domain.monitor.SysLoginInfo;
import com.westChina.system.api.domain.monitor.SysOperLog;
import com.westChina.system.api.feign.factory.RemoteLogFallbackFactory;

/**
 * 日志服务
 *
 * @author westChina
 */
@FeignClient(contextId = "remoteLogService", value = ServiceConstants.SYSTEM_SERVICE, fallbackFactory = RemoteLogFallbackFactory.class)
public interface RemoteLogService {

    /**
     * 保存系统日志
     *
     * @param sysOperLog 日志实体
     * @return 结果
     */
    @PostMapping("/operlog")
    public R<Boolean> saveLog(@RequestBody SysOperLog sysOperLog, @RequestHeader(SecurityConstants.FROM_SOURCE) String source);

    /**
     * 保存访问记录
     *
     * @param loginInfo 访问实体
     * @param source    请求来源
     * @return 结果
     */
    @PostMapping("/loginInfo")
    public R<Boolean> saveLoginInfo(@RequestBody SysLoginInfo loginInfo, @RequestHeader(SecurityConstants.FROM_SOURCE) String source);
}