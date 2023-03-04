package com.westChina.ct.controller;

import com.westChina.common.core.domain.R;
import com.westChina.common.core.utils.ServletUtils;
import com.westChina.common.core.utils.StringUtils;
import com.westChina.common.core.web.controller.BaseController;
import com.westChina.common.core.web.domain.AjaxResult;
import com.westChina.common.log.annotation.Log;
import com.westChina.common.log.enums.BusinessType;
import com.westChina.common.redis.service.RedisService;
import com.westChina.common.security.annotation.RequiresPermissions;
import com.westChina.common.security.service.TokenService;
import com.westChina.ct.domain.CtPatients;
import com.westChina.ct.domain.DicomMaker;
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
     * 删除病人信息
     */
    @Log(title = "删除文件", businessType = BusinessType.DELETE)
    @DeleteMapping("/delFile")
    public AjaxResult delFile(@RequestBody List<String> bucketFileNamesList) {
        LoginUser loginUser = tokenService.getLoginUser(ServletUtils.getRequest());
        String bucketName = remoteTenantService.getBucketNameByEnterpriseName(loginUser.getEnterpriseName()).getData();
        R<Boolean> result =  remoteFileService.delFileOfMinio(bucketFileNamesList, bucketName);
        AjaxResult ajax = AjaxResult.success(result.getMsg());
        if (!result.getData()){
            ajax = AjaxResult.error(result.getMsg());
        }
        return ajax;
    }



















    public File transferToFile(MultipartFile multipartFile) {
//        选择用缓冲区来实现这个转换即使用java 创建的临时文件 使用 MultipartFile.transferto()方法 。
        File file = null;
        try {
            String originalFilename = multipartFile.getOriginalFilename();
            assert originalFilename != null : "文件名为空字符";
            String[] filename = originalFilename.split("\\.");
            file = File.createTempFile(filename[0], filename[1]);
            multipartFile.transferTo(file);
            file.deleteOnExit();
        } catch (IOException e) {
            e.printStackTrace();
        }
        return file;
    }

    public String tranByte2String(byte[] b) {
        return new String(b);
    }

}
