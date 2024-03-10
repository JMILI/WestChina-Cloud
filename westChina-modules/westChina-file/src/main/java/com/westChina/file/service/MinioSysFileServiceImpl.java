package com.westChina.file.service;

import com.alibaba.cloud.commons.lang.StringUtils;
import com.westChina.file.config.MinioConfig;
import io.minio.*;
import io.minio.errors.*;
import io.minio.messages.Bucket;
import io.minio.messages.Item;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import javax.servlet.ServletOutputStream;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.List;

@Service()
public class MinioSysFileServiceImpl extends AMinioSysFileService {
    /*
     * 桶占位符
     */
    private static final String BUCKET_PARAM = "${bucketName}";
    /**
     * bucket权限-只读
     */
    private static final String READ_ONLY = "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"AWS\":[\"*\"]},\"Action\":[\"s3:GetBucketLocation\",\"s3:ListBucket\"],\"Resource\":[\"arn:aws:s3:::" + BUCKET_PARAM + "\"]},{\"Effect\":\"Allow\",\"Principal\":{\"AWS\":[\"*\"]},\"Action\":[\"s3:GetObject\"],\"Resource\":[\"arn:aws:s3:::" + BUCKET_PARAM + "/*\"]}]}";

    /**
     * bucket权限-只写
     */
    private static final String WRITE_ONLY = "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"AWS\":[\"*\"]},\"Action\":[\"s3:GetBucketLocation\",\"s3:ListBucketMultipartUploads\"],\"Resource\":[\"arn:aws:s3:::" + BUCKET_PARAM + "\"]},{\"Effect\":\"Allow\",\"Principal\":{\"AWS\":[\"*\"]},\"Action\":[\"s3:AbortMultipartUpload\",\"s3:DeleteObject\",\"s3:ListMultipartUploadParts\",\"s3:PutObject\"],\"Resource\":[\"arn:aws:s3:::" + BUCKET_PARAM + "/*\"]}]}";
    /**
     * bucket权限-读写:public
     */
    private static final String READ_WRITE = "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"AWS\":[\"*\"]},\"Action\":[\"s3:GetBucketLocation\",\"s3:ListBucket\",\"s3:ListBucketMultipartUploads\"],\"Resource\":[\"arn:aws:s3:::" + BUCKET_PARAM + "\"]},{\"Effect\":\"Allow\",\"Principal\":{\"AWS\":[\"*\"]},\"Action\":[\"s3:DeleteObject\",\"s3:GetObject\",\"s3:ListMultipartUploadParts\",\"s3:PutObject\",\"s3:AbortMultipartUpload\"],\"Resource\":[\"arn:aws:s3:::" + BUCKET_PARAM + "/*\"]}]}";

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
            if (makeBucket(bucketName)) {
                minioClient.setBucketPolicy(
                        SetBucketPolicyArgs
                                .builder()
                                .bucket(bucketName)
                                .config(READ_WRITE.replace(BUCKET_PARAM, bucketName))
                                .build());
                return true;
            } else {
                return false;
            }

        }

    }




    /**
     * 下载文件
     *
     * @param originalName 文件路径
     */
    public InputStream downloadFile(String bucketName, String originalName, HttpServletResponse response) {
        try {
            InputStream file = minioClient.getObject(GetObjectArgs.builder().bucket(bucketName).object(originalName).build());
            String filename = new String(originalName.getBytes("ISO8859-1"), StandardCharsets.UTF_8);
            if (StringUtils.isNotBlank(originalName)) {
                filename = originalName;
            }
            response.setHeader("Content-Disposition", "attachment;filename=" + filename);
            ServletOutputStream servletOutputStream = response.getOutputStream();
            int len;
            byte[] buffer = new byte[1024];
            while ((len = file.read(buffer)) > 0) {
                servletOutputStream.write(buffer, 0, len);
            }
            servletOutputStream.flush();
            file.close();
            servletOutputStream.close();
            return file;
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }


    /**
     * 查看存储bucket是否存在
     *
     * @return Boolean
     */
    public Boolean bucketExists(String bucketName) {
        boolean found = false;
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
     * 删除存储bucket:bucketName
     *
     * @return Boolean
     */
    public Boolean removeBucket(String bucketName) {
        try {
            //清空桶里的所有文件
            clearBucket(bucketName);
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
     * 清空某个bucket
     *
     * @param bucketName
     */
    public void clearBucket(String bucketName) {
        boolean flag = bucketExists(bucketName);
        if (flag) {
            try {
                // 递归列举某个bucket下的所有文件，然后循环删除
                Iterable<Result<Item>> iterable = minioClient.listObjects(ListObjectsArgs.builder()
                        .bucket(bucketName)
                        .recursive(true)
                        .build());
                for (Result<Item> itemResult : iterable) {
                    minioClient.removeObject(RemoveObjectArgs.builder().bucket(bucketName).object(itemResult.get().objectName()).build());
                }
            } catch (Exception e) {
                System.out.println("错误");
            }
        }
    }

    /**
     * @param bucketName:
     * @description: 删除桶下面所有文件
     * @date 2022/8/16 14:36
     */
    public void deleteBucketFile(String bucketName) {
        try {
            if (StringUtils.isBlank(bucketName)) {
                return;
            }
            boolean isExist = minioClient.bucketExists(BucketExistsArgs.builder().bucket(bucketName).build());
            if (isExist) {
                minioClient.deleteBucketEncryption(DeleteBucketEncryptionArgs.builder().bucket(bucketName).build());
            }
        } catch (Exception e) {
            e.printStackTrace();
            log.error(e.getMessage());
        }
    }

    /**
     * 根据文件路径得到预览文件绝对地址
     *
     * @param bucketName
     * @param fileName
     * @return
     */
    public String getPreviewFileUrl(String bucketName, String fileName) {
        try {
            return minioClient.getPresignedObjectUrl(GetPresignedObjectUrlArgs.builder().bucket(bucketName).object(fileName).build());
        } catch (Exception e) {
            e.printStackTrace();
            return "";
        }
    }

    /**
     * 获取文件流
     *
     * @param fileName   文件名
     * @param bucketName 桶名（文件夹）
     * @return
     */
    public InputStream getFileInputStream(String fileName, String bucketName) {
        try {
            return minioClient.getObject(GetObjectArgs.builder().bucket(bucketName).object(fileName).build());
        } catch (Exception e) {
            e.printStackTrace();
            log.error(e.getMessage());
        }
        return null;
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
     * @param file 上传的文件
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
            return fileName;
        } else {
            log.error("文件为空");
            return "";
        }
    }

    /**
     * 删除单个文件，
     *
     * @param fileName 文件名
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
     * 删除文件夹内所有文件
     * 注意这里删除之后，文件夹并没有删除
     *
     * @param bucketName bucket名称
     * @param folder     文件或文件夹名称
     * @since tarzan LIU
     */
    public void deleteFolder(String bucketName, String folder) {
        try {
            if (StringUtils.isNotBlank(folder)) {
                String folders = folder + "/";
                Iterable<Result<Item>> list =
                        minioClient.listObjects(
                                ListObjectsArgs.builder()
                                        .bucket(bucketName)
                                        .recursive(true)
                                        .prefix(folders)
                                        .build());
                list.forEach(e -> {
                    try {
                        minioClient.removeObject(RemoveObjectArgs.builder().bucket(bucketName).object(e.get().objectName()).build());
                    } catch (ServerException |
                             InsufficientDataException |
                             ErrorResponseException |
                             IOException |
                             NoSuchAlgorithmException |
                             InvalidKeyException |
                             InvalidResponseException |
                             XmlParserException |
                             InternalException ex) {
                        throw new RuntimeException(ex);
                    }
                });
            }
        } catch (Exception e) {
            e.printStackTrace();
            log.error("remove  ", e);
        }
    }


}
