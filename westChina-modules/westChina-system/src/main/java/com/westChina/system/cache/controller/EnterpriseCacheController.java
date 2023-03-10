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
 * 企业缓存
 *
 * @author westChina
 */
@RestController
@RequestMapping("/enterpriseCache")
public class EnterpriseCacheController extends BaseController {

    @Autowired
    private ISysCacheInitService cacheInitService;

    /**
     * 根据企业Id刷新企业全部缓存
     */
    @InnerAuth
    @GetMapping("/refreshEnterpriseAllCache/{enterpriseId}")
    public R<Boolean> refreshEnterpriseAllCache(@PathVariable("enterpriseId") Long enterpriseId) {
        cacheInitService.loadingEnterpriseAllCacheByEnterpriseId(enterpriseId);
        return R.ok(true);
    }
}