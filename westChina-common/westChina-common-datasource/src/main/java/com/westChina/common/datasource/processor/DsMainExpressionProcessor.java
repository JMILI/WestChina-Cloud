package com.westChina.common.datasource.processor;

import com.baomidou.dynamic.datasource.processor.DsProcessor;
import com.westChina.common.core.constant.TenantConstants;
import org.aopalliance.intercept.MethodInvocation;
import org.springframework.stereotype.Component;

import static com.westChina.common.core.constant.TenantConstants.MASTER;

/**
 * 主库源策略
 *
 * @author westChina
 */
@Component
public class DsMainExpressionProcessor extends DsProcessor {

    @Override
    public boolean matches(String key) {
        return key.startsWith(MASTER);
    }

    @Override
    public String doDetermineDatasource(MethodInvocation invocation, String key) {
        return TenantConstants.Source.MAIN.getCode();
    }
}