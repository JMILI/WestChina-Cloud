package com.westChina.system.cache.controller;

import com.westChina.common.core.domain.R;
import com.westChina.common.core.web.controller.BaseController;
import com.westChina.common.security.annotation.InnerAuth;
import com.westChina.system.cache.service.ISysCacheInitService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 数据源缓存信息
 *
 * @author westChina
 */
@RestController
@RequestMapping("/sourceCache")
public class SourceCacheController extends BaseController {

    @Autowired
    private ISysCacheInitService cacheInitService;

    /**
     * 根据策略Id刷新策略缓存
     */
    @InnerAuth
    @GetMapping("/refreshSourceCache/{strategyId}")
    public R<Boolean> refreshSourceCache(@PathVariable("strategyId") Long strategyId) {
        cacheInitService.refreshSourceCacheByStrategyId(strategyId);
        return R.ok(true);
    }
}