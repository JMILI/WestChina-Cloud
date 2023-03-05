package com.westChina.file.service;

import com.westChina.file.config.MinioConfig;
import io.minio.MinioClient;
import io.minio.RemoveObjectArgs;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;


class MinioSysFileServiceImplTest {

    @Autowired
    private MinioConfig minioConfig;

    @Autowired
    private MinioClient minioClient;
    @Test
    void removeOne() {
        int a=1;
        System.out.println("1"+a);
        a=a*2;
        System.out.println("2"+a);
//        sleep(1000);
        a=a*3;
        System.out.println("3"+a);
        a=a+1;
        System.out.println("4"+a);
    }

    @Test
    void testRemoveOne() {
        System.out.println("dasdasd");
        String bucketName= "common";
        String fileName = "1.3.12.2.1107.5.1.4.77426.30000021081723585752900164070_1677848597733.png";
//        String fileName = "1.2.156.14702.6.146.20210819000527/1.3.12.2.1107.5.1.4.77426.30000021081723585752900164069/1.dcm";
        try {

            RemoveObjectArgs removeArgs = RemoveObjectArgs.builder()
                    .bucket(bucketName)
                    .object(fileName)
                    .build();
            minioClient.removeObject(removeArgs);
        } catch (Exception e) {
            System.out.println("cuowu"+e);
        }
    }
}