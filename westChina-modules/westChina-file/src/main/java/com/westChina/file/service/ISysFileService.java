package com.westChina.file.service;

import org.springframework.web.multipart.MultipartFile;

/**
 * 文件上传接口
 * 
 * @author ruoyi
 */
public interface ISysFileService
{
    /**
     * 文件上传接口
     * 
     * @param file 上传的文件
     * @return 访问地址
     * @throws Exception
     */
    public String uploadFile(MultipartFile file) throws Exception;

    /**
     * 文件删除接口
     *
     * @param url 文件地址
     * @return 删除状态
     * @throws Exception
     */
    public Boolean deleteFile(String url) throws Exception;



//    /**
//     * 文件上传接口,直接上传
//     * @author jm
//     * @param file 上传的文件
//     * @return 访问地址
//     * @throws Exception
//     */
//    public String directUpload(MultipartFile file) throws Exception;
//
//
//    public Boolean makeMinioBucket(String bucketName) throws Exception;
//
//    public  Boolean removeOne(String fileName, String bucketName);
//
//    public  String directUploadOfMinio(MultipartFile file, String bucketName) throws Exception;

}
