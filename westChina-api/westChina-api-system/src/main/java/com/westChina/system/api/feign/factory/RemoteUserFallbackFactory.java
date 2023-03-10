package com.westChina.system.api.feign.factory;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.cloud.openfeign.FallbackFactory;
import org.springframework.stereotype.Component;
import com.westChina.common.core.domain.R;
import com.westChina.system.api.feign.RemoteUserService;
import com.westChina.system.api.model.LoginUser;

/**
 * 用户服务降级处理
 *
 * @author westChina
 */
@Component
public class RemoteUserFallbackFactory implements FallbackFactory<RemoteUserService> {

    private static final Logger log = LoggerFactory.getLogger(RemoteUserFallbackFactory.class);

    @Override
    public RemoteUserService create(Throwable throwable) {
        log.error("用户服务调用失败:{}", throwable.getMessage());
        return new RemoteUserService() {
            @Override
            public R<LoginUser> getUserInfo(String enterpriseName, String userName, String source) {
                return R.fail("获取用户失败:" + throwable.getMessage());
            }
        };
    }
}