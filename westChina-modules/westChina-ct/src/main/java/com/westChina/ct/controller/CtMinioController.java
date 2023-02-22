package com.westChina.ct.controller;

import com.westChina.common.core.domain.R;
import com.westChina.common.core.web.controller.BaseController;
import com.westChina.common.core.web.domain.AjaxResult;
import com.westChina.tenant.api.feign.RemoteTenantService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Objects;

/**
 * 病人信息 业务处理
 *
 * @author jm
 */
@RestController
@RequestMapping("/minio")
public class CtMinioController extends BaseController {

    @Autowired
    private RemoteTenantService remoteTenantService;

    /**
     * 获取租户的对象存储桶：minio里面的桶
     */
    @GetMapping(value = "/getBucketName")
    public AjaxResult getBucketName(String enterpriseName) {
        // feign本地调用 tenant的服务，请求minio桶名称
        R<String> data =new R<String>();
        data.setData("");
        data.setMsg("失败");
        data = remoteTenantService.getBucketNameByEnterpriseName(enterpriseName);
        if (!Objects.equals(data.getData(), null)) {
            return AjaxResult.success(data.getMsg(),data.getData());
        } else {
            return AjaxResult.error(data.getMsg(),"");
        }
    }

}