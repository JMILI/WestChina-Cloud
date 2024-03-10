package com.westChina.tenant.api.feign;

import com.westChina.common.core.constant.SecurityConstants;
import com.westChina.common.core.constant.ServiceConstants;
import com.westChina.common.core.domain.R;
import com.westChina.tenant.api.feign.factory.RemoteTenantFallbackFactory;
import com.westChina.tenant.api.model.TenantRegister;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.*;

/**
 * 用户服务
 *
 * @author westChina
 */
@FeignClient(contextId = "remoteTenantService", value = ServiceConstants.TENANT_SERVICE, fallbackFactory = RemoteTenantFallbackFactory.class)
public interface RemoteTenantService {
    /**
     * 根据租户账号查询，该账号所拥有的minio桶-对象存储空间
     * feign调用只给返回桶名
     * @param enterpriseName 租户账号
     * @return
     */
    @GetMapping(value = "/bucket/getBucketNameByEnterpriseName")
    public R<String> getBucketNameByEnterpriseName(@RequestParam(value = "enterpriseName") String enterpriseName);
    /**
     * 注册租户信息
     *
     * @param register 注册信息
     * @param source   请求来源
     * @return 结果
     */
    @PostMapping("/tenant/register")
    public R<Boolean> registerTenantInfo(@RequestBody TenantRegister register, @RequestHeader(SecurityConstants.FROM_SOURCE) String source);
}