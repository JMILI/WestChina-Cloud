package com.westChina.ct.controller;

import com.westChina.common.core.domain.R;
import com.westChina.common.core.utils.ServletUtils;
import com.westChina.common.core.utils.StringUtils;
import com.westChina.common.core.web.controller.BaseController;
import com.westChina.common.core.web.domain.AjaxResult;
import com.westChina.common.log.annotation.Log;
import com.westChina.common.log.enums.BusinessType;
import com.westChina.common.redis.service.RedisService;
import com.westChina.common.security.service.TokenService;
import com.westChina.system.api.domain.material.SysFile;
import com.westChina.system.api.feign.RemoteFileService;
import com.westChina.system.api.model.LoginUser;
import com.westChina.tenant.api.feign.RemoteTenantService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;


import java.io.File;
import java.io.IOException;
import java.util.List;
import java.util.Objects;

@RestController
@RequestMapping("/upload")
public class ctUploadController extends BaseController {
    @Autowired
    private TokenService tokenService;

    @Autowired
    private RedisService redisService;

    @Autowired
    private RemoteFileService remoteFileService;

    @Autowired
    private RemoteTenantService remoteTenantService;
    private static final Logger log = LoggerFactory.getLogger(ctUploadController.class);

    /**
     * 获取租户的对象存储桶：minio里面的桶
     * @param enterpriseName 企业账号
     * @return
     */
    @GetMapping(value = "/getBucketName")
    public AjaxResult getBucketName(String enterpriseName) {
        // feign本地调用 tenant的服务，请求minio桶名称
        R<String> data = new R<String>();
        data.setData("");
        data.setMsg("失败");
        data = remoteTenantService.getBucketNameByEnterpriseName(enterpriseName);
        if (!Objects.equals(data.getData(), null)) {
            return AjaxResult.success(data.getMsg(), data.getData());
        } else {
            return AjaxResult.error(data.getMsg(), "");
        }
    }

    /**
     * 上传病人ct图像,
     *
     * @param file
     * @return
     * @throws IOException
     */
    @Log(title = "上传病人ct图像", businessType = BusinessType.UPDATE)
    @PostMapping("/ctFile")
    public AjaxResult ctFile(MultipartFile file) throws IOException {
        LoginUser loginUser = tokenService.getLoginUser(ServletUtils.getRequest());
        String bucketName = remoteTenantService.getBucketNameByEnterpriseName(loginUser.getEnterpriseName()).getData();
        R<SysFile> fileResult = remoteFileService.directUploadOfMinio(file, bucketName);
        if (StringUtils.isNull(fileResult) || StringUtils.isNull(fileResult.getData())) {
            return AjaxResult.error("文件服务异常，请稍后再试");
        }
        String url = fileResult.getData().getUrl();
        AjaxResult ajax = AjaxResult.success("成功");
        ajax.put("url", url);
        return ajax;
    }


    /**
     * 从minio批量删除某些文件
     * @param bucketFileNamesList 文件名列表
     * @return
     */
    @Log(title = "从minio删除某些文件", businessType = BusinessType.DELETE)
    @DeleteMapping("/delFile")
    public AjaxResult delFile(@RequestBody List<String> bucketFileNamesList) {
        LoginUser loginUser = tokenService.getLoginUser(ServletUtils.getRequest());
        String bucketName = remoteTenantService.getBucketNameByEnterpriseName(loginUser.getEnterpriseName()).getData();
        R<Boolean> result = remoteFileService.delFileOfMinio(bucketFileNamesList, bucketName);
        if(result.getData()){
            return AjaxResult.success(result.getMsg());
        }else{
            return AjaxResult.error(result.getMsg());
        }
    }

    @Log(title = "从minio删除某个桶：bucketName", businessType = BusinessType.DELETE)
    @DeleteMapping("/delBucketName")
    public AjaxResult delBucketName(String bucketName) {
        R<Boolean> result = remoteFileService.removeBucketName(bucketName);
        if(result.getData()){
            return AjaxResult.success(result.getMsg());
        }else{
            return AjaxResult.error(result.getMsg());
        }
    }

    @Log(title = "从minio删除病人的某个文件夹内所有对象", businessType = BusinessType.DELETE)
    @DeleteMapping("/delFolderFiles")
    public AjaxResult delFolderFiles(@RequestBody List<String> dicomImageList) {
        LoginUser loginUser = tokenService.getLoginUser(ServletUtils.getRequest());
        String bucketName = remoteTenantService.getBucketNameByEnterpriseName(loginUser.getEnterpriseName()).getData();
        R<Boolean> result = remoteFileService.removeFolderFilesOfMinio(dicomImageList,bucketName);
        if(result.getData()){
            return AjaxResult.success(result.getMsg());
        }else{
            return AjaxResult.error(result.getMsg());
        }
    }


}
