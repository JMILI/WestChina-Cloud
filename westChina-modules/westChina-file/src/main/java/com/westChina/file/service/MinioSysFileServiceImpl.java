package com.westChina.file.service;

import com.westChina.file.config.MinioConfig;
import io.minio.*;
import io.minio.messages.Bucket;
import io.minio.messages.DeleteError;
import io.minio.messages.DeleteObject;
import io.minio.messages.Item;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

@Service()
public class MinioSysFileServiceImpl extends AMinioSysFileService {


    @Autowired
    private MinioConfig minioConfig;

    @Autowired
    private MinioClient minioClient;

    private static final Logger log = LoggerFactory.getLogger(MinioSysFileServiceImpl.class);


    /**
     * 创建minio bucket 桶
     *
     * @param bucketName 桶名
     * @return
     * @throws Exception
     */

    public Boolean makeMinioBucket(String bucketName) throws Exception {
        if (bucketExists(bucketName)) {
            System.out.println("Bucket already exists.");
            return false;
        } else {
            makeBucket(bucketName);
            return true;
        }

    }

    /**
     * 查看存储bucket是否存在
     *
     * @return Boolean
     */
    public Boolean bucketExists(String bucketName) {
        Boolean found = false;
        try {
            BucketExistsArgs args = BucketExistsArgs.builder().bucket(bucketName)
                    .build();
            found = minioClient.bucketExists(args);
        } catch (Exception e) {
            log.error("bucketExists  ", e);
        }
        return found;
    }

    /**
     * 创建存储bucket
     *
     * @return Boolean
     */
    public Boolean makeBucket(String bucketName) {
        try {
            MakeBucketArgs makeArgs = MakeBucketArgs.builder()
                    .bucket(bucketName)
                    .build();
            minioClient.makeBucket(makeArgs);
        } catch (Exception e) {
            log.error("makeBucket  ", e);
            return false;
        }
        return true;
    }

    /**
     * 删除存储bucket
     *
     * @return Boolean
     */
    public Boolean removeBucket(String bucketName) {
        try {
            RemoveBucketArgs removeArgs = RemoveBucketArgs.builder()
                    .bucket(bucketName)
                    .build();
            minioClient.removeBucket(removeArgs);
        } catch (Exception e) {
            log.error("removeBucket  ", e);
            return false;
        }
        return true;
    }

    /**
     * 获取全部bucket
     */
    public List<Bucket> getAllBuckets() {
        try {
            return minioClient.listBuckets();
        } catch (Exception e) {
            log.error("getAllBuckets  ", e);
        }
        return null;
    }


    /**
     * 文件下载
     *
     * @param fileName 文件的路径和名字
     * @return Boolean
     */
    public void download(String fileName, String saveName, String bucketName) {
        DownloadObjectArgs build = DownloadObjectArgs.builder()
                .bucket(bucketName)
                .filename(saveName)
                .object(fileName)
                .build();
        try {
            minioClient.downloadObject(build);
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }


    /**
     * 查看文件对象
     *
     * @return 存储bucket内文件对象信息
     */
    public List<Item> listObjects(String bucketName) {
        ListObjectsArgs listObjectsArgs = ListObjectsArgs.builder()
                .bucket(bucketName)
                .build();
        Iterable<Result<Item>> results = minioClient.listObjects(listObjectsArgs);
        List<Item> itemList = new ArrayList<>();
        try {
            for (Result<Item> result : results) {
                itemList.add(result.get());
            }
        } catch (Exception e) {
            log.error("listObjects  ", e);
            return null;
        }
        return itemList;
    }

    /**
     * minio上传文件
     *
     * @param file       上传的文件
     * @param bucketName
     * @return
     * @throws Exception
     * @author jm
     */
    public String directUploadOfMinio(MultipartFile file, String bucketName) throws Exception {
        if (file != null) {
            String fileName = file.getOriginalFilename();
            log.info(fileName);
            PutObjectArgs args = PutObjectArgs.builder()
                    .bucket(bucketName)
                    .object(fileName)
                    .stream(file.getInputStream(), file.getSize(), -1)
                    .contentType(file.getContentType())
                    .build();
            minioClient.putObject(args);
            return minioConfig.getUrl() + "/" + bucketName + fileName;
        } else {
            log.error("文件为空");
            return "";
        }
    }

    /**
     * 删除
     *
     * @param fileName
     * @return
     * @throws Exception
     */
    public Boolean removeOne(String fileName, String bucketName) {
        try {
            RemoveObjectArgs removeArgs = RemoveObjectArgs.builder()
                    .bucket(bucketName)
                    .object(fileName)
                    .build();
            minioClient.removeObject(removeArgs);
        } catch (Exception e) {
            log.error("remove  ", e);
            return false;
        }
        return true;
    }

    /**
     * 批量删除文件对象
     *
     * @param bucketFileNamesList 对象名称集合
     */
    public Iterable<Result<DeleteError>> removeObjects(List<String> bucketFileNamesList, String bucketName) {
        List<DeleteObject> dos = bucketFileNamesList.stream().map(DeleteObject::new).collect(Collectors.toList());
        RemoveObjectsArgs build = RemoveObjectsArgs.builder()
                .bucket(bucketName)
                .objects(dos)
                .build();
        return minioClient.removeObjects(build);
    }
}
