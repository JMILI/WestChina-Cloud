package com.westChina.file.controller;

import com.westChina.file.service.MinioSysFileServiceImpl;
import io.minio.Result;
import io.minio.messages.DeleteError;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import com.westChina.common.core.domain.R;
import com.westChina.common.core.utils.file.FileUtils;
import com.westChina.file.service.ISysFileService;
import com.westChina.system.api.domain.material.SysFile;

import java.util.List;

/**
 * 文件请求处理
 *
 * @author ruoyi
 */
@RestController
public class SysFileController
{
    private static final Logger log = LoggerFactory.getLogger(SysFileController.class);

    @Autowired
    private ISysFileService sysFileService;

    @Autowired
    private MinioSysFileServiceImpl minioSysFileServiceImpl;

    /**
     * 文件上传请求
     */
    @PostMapping("upload")
    public R<SysFile> upload(MultipartFile file)
    {
        try
        {
            // 上传并返回访问地址
            String url = sysFileService.uploadFile(file);
            SysFile sysFile = new SysFile();
            sysFile.setName(FileUtils.getName(url));
            sysFile.setUrl(url);
            return R.ok(sysFile);
        }
        catch (Exception e)
        {
            log.error("上传文件失败", e);
            return R.fail(e.getMessage());
        }
    }

    /**
     * 文件上传请求
     */
    @PostMapping("delete")
    public R<Boolean> delete(String url)
    {
        try
        {
            Boolean result = sysFileService.deleteFile(url);
            return R.ok(result);
        }
        catch (Exception e)
        {
            log.error("文件删除失败", e);
            return R.fail(e.getMessage());
        }
    }

    /**
     * 文件上传请求 直接上传
     */
    @PostMapping("directUploadOfMinio")
    public R<SysFile> directUploadOfMinio(MultipartFile file, String bucketName) {
        try {
            // 上传并返回访问地址
            String url = minioSysFileServiceImpl.directUploadOfMinio(file, bucketName);
            SysFile sysFile = new SysFile();
            sysFile.setName(FileUtils.getName(url));
            sysFile.setUrl(url);
            return R.ok(sysFile);
        } catch (Exception e) {
            log.error("上传文件失败", e);
            return R.fail(e.getMessage());
        }
    }

    /**
     * 创建minio桶
     */
    @PostMapping("makeMinioBucket")
    public R<Boolean> makeMinioBucket(String bucketName)
    {
        try
        {
            Boolean result =minioSysFileServiceImpl.makeMinioBucket(bucketName);
            return  R.ok(result);
        }
        catch (Exception e)
        {
            log.error("存在桶", e);
            return R.fail(e.getMessage());
        }
    }


    /**
     * 文件上传请求
     */
    @DeleteMapping("delFileOfMinio")
    public R<Boolean> delFileOfMinio(@RequestBody  List<String> bucketFileNamesList,String bucketName)
    {
        try
        {
            for(String item:bucketFileNamesList) {
                minioSysFileServiceImpl.removeOne(item,bucketName);
            }
            return R.ok(true,"删除成功");
        }
        catch (Exception e)
        {
            log.error("文件删除失败", e);
            return R.fail(false,e.getMessage());
        }
    }
}