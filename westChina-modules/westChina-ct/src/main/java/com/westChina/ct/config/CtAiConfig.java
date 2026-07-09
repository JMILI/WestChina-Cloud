package com.westChina.ct.config;

import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.web.client.RestTemplate;

@Configuration
@EnableConfigurationProperties(CtAiProperties.class)
public class CtAiConfig {

    @Bean(name = "ctAiRestTemplate")
    public RestTemplate ctAiRestTemplate(CtAiProperties properties) {
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(properties.getConnectTimeoutMs());
        factory.setReadTimeout(properties.getReadTimeoutMs());
        return new RestTemplate(factory);
    }

    @Bean(name = "ctAiQuickRestTemplate")
    public RestTemplate ctAiQuickRestTemplate(CtAiProperties properties) {
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(properties.getConnectTimeoutMs());
        factory.setReadTimeout(properties.getEnginesReadTimeoutMs());
        return new RestTemplate(factory);
    }
}
