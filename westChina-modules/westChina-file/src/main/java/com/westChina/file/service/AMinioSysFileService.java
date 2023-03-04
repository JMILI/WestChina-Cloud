package com.westChina.file.service;

import com.westChina.file.utils.FileUploadUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Primary;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;
import com.westChina.file.config.MinioConfig;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

import io.minio.*;
import io.minio.messages.Bucket;
import io.minio.messages.DeleteError;
import io.minio.messages.DeleteObject;
import io.minio.messages.Item;

/**
 * Minio 文件存储
 *
 * @author ruoyi
 */
@Primary
@Service()
  public abstract class AMinioSysFileService implements ISysFileService {
    @Autowired
    private MinioConfig minioConfig;

    @Autowired
    private MinioClient client;

    /**
     * 本地文件上传接口
     *
     * @param file 上传的文件
     * @return 访问地址
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
     * @return 结果
     */
    public Boolean deleteFile(String url) throws Exception {
        return true;
    }



}
