package com.westChina.ct.config;

import javax.annotation.PostConstruct;
import org.springframework.amqp.core.Binding;
import org.springframework.amqp.core.BindingBuilder;
import org.springframework.amqp.core.DirectExchange;
import org.springframework.amqp.core.Queue;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.amqp.support.converter.Jackson2JsonMessageConverter;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * CT AI 异步任务队列配置
 */
@Configuration
public class CtAiTaskMqConfig {

    public static final String EXCHANGE = "exchange-ct-ai-task";
    public static final String QUEUE = "queue-ct-ai-task";
    public static final String ROUTING_KEY = "routingKey.ct.ai.task";

    @Autowired
    private RabbitTemplate rabbitTemplate;

    /**
     * 与 {@link org.springframework.amqp.rabbit.config.SimpleRabbitListenerContainerFactory}
     * 的 Jackson 转换器保持一致，避免生产者 Java 序列化、消费者 JSON 反序列化不匹配。
     */
    @PostConstruct
    public void configureJsonMessageConverter() {
        rabbitTemplate.setMessageConverter(new Jackson2JsonMessageConverter());
    }

    @Bean
    public DirectExchange ctAiTaskExchange() {
        return new DirectExchange(EXCHANGE, true, false);
    }

    @Bean
    public Queue ctAiTaskQueue() {
        return new Queue(QUEUE, true);
    }

    @Bean
    public Binding ctAiTaskBinding() {
        return BindingBuilder.bind(ctAiTaskQueue()).to(ctAiTaskExchange()).with(ROUTING_KEY);
    }
}

