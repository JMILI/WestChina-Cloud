package com.westChina.common.datasource.processor;

import cn.hutool.core.util.StrUtil;
import com.baomidou.dynamic.datasource.processor.DsProcessor;
import com.westChina.common.datasource.utils.DSUtils;
import com.westChina.common.security.utils.SecurityUtils;
import org.aopalliance.intercept.MethodInvocation;
import org.springframework.stereotype.Component;

import static com.westChina.common.core.constant.TenantConstants.ISOLATE;

/**
 * 租户库源策略
 *
 * @author westChina
 */
@Component
public class DsIsolateExpressionProcessor extends DsProcessor {

    @Override
    public boolean matches(String key) {
        return key.startsWith(ISOLATE);
    }

    @Override
    public String doDetermineDatasource(MethodInvocation invocation, String key) {
        String sourceName = SecurityUtils.getSourceName();
        return StrUtil.isNotEmpty(sourceName) ? sourceName : DSUtils.getNowDsName();
    }
}