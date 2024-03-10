package com.westChina.system.api.feign;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import com.westChina.common.core.constant.ServiceConstants;
import com.westChina.common.core.domain.R;
import com.westChina.system.api.domain.material.SysFile;
import com.westChina.system.api.feign.factory.RemoteFileFallbackFactory;

import java.util.List;

/**
 * 文件服务
 *
 * @author westChina
 * @originalAuthor ruoyi
 */
@FeignClient(contextId = "remoteFileService", value = ServiceConstants.FILE_SERVICE, fallbackFactory = RemoteFileFallbackFactory.class)
public interface RemoteFileService {

    /**
     * 上传文件
     *
     * @param file 文件信息
     * @return 结果
     */
    @PostMapping(value = "/upload", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public R<SysFile> upload(@RequestPart(value = "file") MultipartFile file);

    /**
     * 上传文件
     *
     * @param url 文件地址
     * @return 结果
     */
    @PostMapping(value = "/delete")
    public R<Boolean> delete(@RequestParam(value = "url") String url);
    /**
     * 上传文件-ct
     *
     * @param file 文件信息
     * @return 结果
     */
    @PostMapping(value = "/directUploadOfMinio", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public R<SysFile> directUploadOfMinio(@RequestPart(value = "file") MultipartFile file, @RequestParam(value = "bucketName") String bucketName);
    /**
     * 创建minio桶
     *
     * @param bucketName 桶名
     * @return 结果
     */
    @PostMapping(value = "/makeMinioBucket")
    public R<Boolean> makeMinioBucket(@RequestParam(value = "bucketName") String bucketName);
    @DeleteMapping(value = "/delFileOfMinio")
    public R<Boolean> delFileOfMinio(@RequestBody List<String> bucketFileNamesList,@RequestParam(value = "bucketName") String bucketName);
    @DeleteMapping(value = "/removeBucketName")
    public R<Boolean> removeBucketName(@RequestParam(value = "bucketName") String bucketName);

    @DeleteMapping(value = "/removeFolderFilesOfMinio")
    public R<Boolean> removeFolderFilesOfMinio(@RequestBody List<String> dicomImageList,@RequestParam(value = "bucketName") String bucketName);
}
