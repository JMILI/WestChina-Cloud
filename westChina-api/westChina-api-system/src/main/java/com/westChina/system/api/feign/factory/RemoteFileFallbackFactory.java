package com.westChina.system.api.feign.factory;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.cloud.openfeign.FallbackFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.multipart.MultipartFile;
import com.westChina.common.core.domain.R;
import com.westChina.system.api.feign.RemoteFileService;
import com.westChina.system.api.domain.material.SysFile;

import java.util.List;

/**
 * 文件服务降级处理
 *
 * @author westChina
 */
@Component
public class RemoteFileFallbackFactory implements FallbackFactory<RemoteFileService> {

    private static final Logger log = LoggerFactory.getLogger(RemoteFileFallbackFactory.class);

    @Override
    public RemoteFileService create(Throwable throwable) {
        log.error("文件服务调用失败:{}", throwable.getMessage());
        return new RemoteFileService() {
            @Override
            public R<SysFile> upload(MultipartFile file) {
                return R.fail("上传文件失败:" + throwable.getMessage());
            }

            @Override
            public R<Boolean> delete(String url) {

                return R.fail("上传文件失败:" + throwable.getMessage());
            }

            @Override
            public R<SysFile> directUploadOfMinio(MultipartFile file,String bucketName) {
                return R.fail("上传文件失败:" + throwable.getMessage());
            }

            @Override
            public R<Boolean> makeMinioBucket(String bucketName) {
                return R.fail("创建桶失败:" + throwable.getMessage());
            }
            @Override
            public R<Boolean> delFileOfMinio(List<String> bucketFileNamesList, String bucketName){
                return R.fail("删除文件失败:" + throwable.getMessage());
            }

            @Override
            public R<Boolean> removeBucketName(String bucketName) {
                return R.fail("删除桶失败:" + throwable.getMessage());
            }
            @Override
            public R<Boolean> removeFolderFilesOfMinio(List<String> dicomImageList, String bucketName){
                return R.fail("删除文件失败:" + throwable.getMessage());
            }
        };
    }
}