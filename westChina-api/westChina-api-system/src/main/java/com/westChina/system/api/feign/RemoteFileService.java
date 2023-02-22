package com.westChina.system.api.feign;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RequestPart;
import org.springframework.web.multipart.MultipartFile;
import com.westChina.common.core.constant.ServiceConstants;
import com.westChina.common.core.domain.R;
import com.westChina.system.api.domain.material.SysFile;
import com.westChina.system.api.feign.factory.RemoteFileFallbackFactory;

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
    @PostMapping(value = "/directUpload", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public R<SysFile> directUpload(@RequestPart(value = "file") MultipartFile file, @RequestParam(value = "bucketName") String bucketName);
    /**
     * 创建minio桶
     *
     * @param bucketName 桶名
     * @return 结果
     */
    @PostMapping(value = "/makeMinioBucket")
    public R<Boolean> makeMinioBucket(@RequestParam(value = "bucketName") String bucketName);
}
