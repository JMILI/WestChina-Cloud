package com.westChina.tenant.api.feign.factory;

import com.westChina.common.core.domain.R;
import com.westChina.tenant.api.feign.RemoteTenantService;
import com.westChina.tenant.api.model.TenantRegister;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.cloud.openfeign.FallbackFactory;
import org.springframework.stereotype.Component;


/**
 * 租户服务降级处理
 *
 * @author westChina
 */
@Component
public class RemoteTenantFallbackFactory implements FallbackFactory<RemoteTenantService> {
    private static final Logger log = LoggerFactory.getLogger(RemoteTenantFallbackFactory.class);

    @Override
    public RemoteTenantService create(Throwable throwable) {
        log.error("租户服务调用失败:{}", throwable.getMessage());
        return new RemoteTenantService() {
            @Override
            public R<Boolean> registerTenantInfo(TenantRegister register, String source)
            {
                return R.fail("注册租户失败:" + throwable.getMessage());
            }
            @Override
            public R<String> getBucketNameByEnterpriseName(String bucketName) {
                return R.fail("查询失败:" + throwable.getMessage());
            }
        };
    }
}