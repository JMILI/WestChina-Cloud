package com.westChina.file.service;

import io.minio.BucketExistsArgs;
import io.minio.MakeBucketArgs;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Primary;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;
import com.westChina.file.config.MinioConfig;
import com.westChina.file.utils.FileUploadUtils;
import io.minio.MinioClient;
import io.minio.PutObjectArgs;

/**
 * Minio 文件存储
 *
 * @author ruoyi
 */
@Primary
@Service
public class MinioSysFileServiceImpl implements ISysFileService {
    @Autowired
    private MinioConfig minioConfig;

    @Autowired
    private MinioClient client;

    private static final Logger log = LoggerFactory.getLogger(MinioSysFileServiceImpl.class);

    /**
     * 本地文件上传接口
     *
     * @param file 上传的文件
     * @return 访问地址
     * @throws Exception
     */
    @Override
    public String uploadFile(MultipartFile file) throws Exception {
        String fileName = FileUploadUtils.extractFilename(file);
        PutObjectArgs args = PutObjectArgs.builder()
                .bucket(minioConfig.getBucketName())
                .object(fileName)
                .stream(file.getInputStream(), file.getSize(), -1)
                .contentType(file.getContentType())
                .build();
        client.putObject(args);
        return minioConfig.getUrl() + "/" + minioConfig.getBucketName() + "/" + fileName;
    }

    /**
     * 文件删除接口
     *
     * @param url 文件地址
     * @return 删除状态
     * @throws Exception
     */
    @Override
    public Boolean deleteFile(String url) throws Exception {
        return true;
    }

    /**
     * @param file       上传的文件
     * @param bucketName
     * @return
     * @throws Exception
     * @author jm
     */
    @Override
    public String directUpload(MultipartFile file, String bucketName) throws Exception {
        if (file != null) {
            String fileName = file.getOriginalFilename();
            log.info(fileName);
            PutObjectArgs args = PutObjectArgs.builder()
                    .bucket(bucketName)
                    .object(fileName)
                    .stream(file.getInputStream(), file.getSize(), -1)
                    .contentType(file.getContentType())
                    .build();
            client.putObject(args);
            return minioConfig.getUrl() + "/" + bucketName + fileName;
        } else {
            log.error("文件为空");
            return "";
        }
    }

    @Override
    public Boolean makeMinioBucket(String bucketName) throws Exception {
        BucketExistsArgs args = BucketExistsArgs.builder().bucket(bucketName).build();
        boolean isExist = client.bucketExists(args);
        if (isExist) {
            System.out.println("Bucket already exists.");
            return false;
        } else {
            MakeBucketArgs makeArgs = MakeBucketArgs.builder().bucket(bucketName).build();
            client.makeBucket(makeArgs);
            return true;
        }
    }
}
