package com.westChina.ct.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

/**
 * CT AI 推理服务配置
 */
@ConfigurationProperties(prefix = "ct.ai")
public class CtAiProperties {

    /** Python FastAPI 服务根地址 */
    private String baseUrl = "http://127.0.0.1:9810";

    private boolean enabled = true;

    private int connectTimeoutMs = 5000;

    private int readTimeoutMs = 7200000;

    /** 引擎列表 / health 等元数据接口读超时（毫秒） */
    private int enginesReadTimeoutMs = 30000;

    /** MQ 消费者并发数（与 CPU 核数相关，见 bootstrap.yml） */
    private int taskConsumerConcurrency = 4;

    public String getBaseUrl() {
        return baseUrl;
    }

    public void setBaseUrl(String baseUrl) {
        this.baseUrl = baseUrl;
    }

    public boolean isEnabled() {
        return enabled;
    }

    public void setEnabled(boolean enabled) {
        this.enabled = enabled;
    }

    public int getConnectTimeoutMs() {
        return connectTimeoutMs;
    }

    public void setConnectTimeoutMs(int connectTimeoutMs) {
        this.connectTimeoutMs = connectTimeoutMs;
    }

    public int getReadTimeoutMs() {
        return readTimeoutMs;
    }

    public void setReadTimeoutMs(int readTimeoutMs) {
        this.readTimeoutMs = readTimeoutMs;
    }

    public int getEnginesReadTimeoutMs() {
        return enginesReadTimeoutMs;
    }

    public void setEnginesReadTimeoutMs(int enginesReadTimeoutMs) {
        this.enginesReadTimeoutMs = enginesReadTimeoutMs;
    }

    public int getTaskConsumerConcurrency() {
        return taskConsumerConcurrency;
    }

    public void setTaskConsumerConcurrency(int taskConsumerConcurrency) {
        this.taskConsumerConcurrency = taskConsumerConcurrency;
    }
}
