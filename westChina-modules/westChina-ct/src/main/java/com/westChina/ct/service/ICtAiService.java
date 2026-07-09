package com.westChina.ct.service;

import java.util.List;
import java.util.Map;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

/**
 * 胸部 CT AI 病灶识别
 */
public interface ICtAiService {

    /**
     * 识别指定序列病灶
     */
    Map<String, Object> detectLesion(Map<String, Object> request);

    /**
     * 对已构建好的 aiRequest 执行识别（用于 MQ 异步任务）。
     */
    Map<String, Object> detectLesionByAiRequest(Map<String, Object> aiRequest);

    /**
     * 流式识别并收集 SSE 事件（用于 MQ 异步任务写 Redis 日志/进度）。
     */
    Map<String, Object> detectLesionStreamCollect(
        Map<String, Object> aiRequest,
        java.util.function.Consumer<Map<String, Object>> onEvent
    );

    /**
     * 流式识别并收集 SSE 事件；taskId 非空时支持协作式取消。
     */
    Map<String, Object> detectLesionStreamCollect(
        Map<String, Object> aiRequest,
        java.util.function.Consumer<Map<String, Object>> onEvent,
        String taskId
    );

    /**
     * 在主请求线程中构建完整 AI 请求（含 bucket / DICOM 元数据），避免异步线程丢失登录上下文
     */
    Map<String, Object> prepareStreamDetectRequest(Map<String, Object> request);

    /**
     * 流式识别（SSE 转发 Python 日志与进度），aiRequest 须由 prepareStreamDetectRequest 预先构建
     */
    void streamDetectLesion(Map<String, Object> aiRequest, SseEmitter emitter);

    /**
     * 通知 ai-service 取消指定任务（最佳努力）。
     */
    void cancelRemoteDetectTask(String taskId);

    /**
     * 获取可用识别引擎列表
     */
    List<Map<String, Object>> listDetectEngines();
}
