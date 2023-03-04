package com.westChina.file.controller;

import com.westChina.file.service.MinioSysFileServiceImpl;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;

import static org.junit.jupiter.api.Assertions.*;

class SysFileControllerTest {
    @Autowired
    private MinioSysFileServiceImpl minioSysFileServiceImpl;
    @Test
    void upload() {
    }

    @Test
    void delete() {
    }

    @Test
    void directUploadOfMinio() {
    }

    @Test
    void makeMinioBucket() throws Exception {
        minioSysFileServiceImpl.makeMinioBucket("123");
    }

    @Test
    void deleteMinioFile() {
        String url="1.3.12.2.1107.5.1.4.77426.30000021081723585752900180618_1677848758212.png";
        Boolean result = minioSysFileServiceImpl.removeOne(url,"common");
    }
}