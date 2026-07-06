package com.westChina.ct.controller;

import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import com.westChina.common.core.web.controller.BaseController;
import com.westChina.common.core.web.domain.AjaxResult;
import com.westChina.ct.config.CtAiProperties;
import com.westChina.ct.service.ICtAiService;

/**
 * 胸部 CT AI 病灶识别
 */
@RestController
@RequestMapping("/ai")
public class CtAiController extends BaseController {

    private static final ExecutorService SSE_EXECUTOR = Executors.newCachedThreadPool();
    private static final Logger log = LoggerFactory.getLogger(CtAiController.class);

    @Autowired
    private ICtAiService ctAiService;

    @Autowired
    private CtAiProperties ctAiProperties;

    @GetMapping("/engines")
    public AjaxResult listEngines() {
        try {
            return AjaxResult.success(ctAiService.listDetectEngines());
        } catch (Exception ex) {
            log.error("[CT-AI] list engines failed", ex);
            return AjaxResult.error("获取识别引擎列表失败：" + ex.getMessage());
        }
    }

    @PostMapping("/detectLesion")
    public AjaxResult detectLesion(@RequestBody Map<String, Object> body) {
        try {
            log.info("[CT-AI] HTTP detect request received, body={}", body);
            Map<String, Object> result = ctAiService.detectLesion(body);
            return AjaxResult.success(result);
        } catch (IllegalArgumentException ex) {
            log.warn("[CT-AI] detect request validation failed, body={}", body, ex);
            return AjaxResult.error(ex.getMessage());
        } catch (IllegalStateException ex) {
            log.error("[CT-AI] detect request state failed, body={}", body, ex);
            return AjaxResult.error(ex.getMessage());
        } catch (Exception ex) {
            log.error("[CT-AI] detect request unexpected error, body={}", body, ex);
            return AjaxResult.error("病灶识别失败：" + ex.getMessage());
        }
    }

    @PostMapping(value = "/detectLesionStream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter detectLesionStream(@RequestBody Map<String, Object> body) {
        log.info("[CT-AI] HTTP stream request received, body={}", body);
        SseEmitter emitter = new SseEmitter((long) ctAiProperties.getReadTimeoutMs());
        final Map<String, Object> aiRequest;
        try {
            aiRequest = ctAiService.prepareStreamDetectRequest(body);
        } catch (Exception ex) {
            log.error("[CT-AI] stream request prepare failed, body={}", body, ex);
            try {
                emitter.send(SseEmitter.event().data("{\"type\":\"error\",\"message\":\""
                    + sanitizeSseMessage(ex.getMessage() == null ? ex.toString() : ex.getMessage()) + "\"}"));
            } catch (Exception sendEx) {
                log.debug("[CT-AI] failed to send prepare error event", sendEx);
            }
            emitter.complete();
            return emitter;
        }
        SSE_EXECUTOR.execute(() -> {
            try {
                ctAiService.streamDetectLesion(aiRequest, emitter);
            } catch (Exception ex) {
                log.error("[CT-AI] stream request unexpected error, body={}", body, ex);
                try {
                    emitter.send(SseEmitter.event().data("{\"type\":\"error\",\"message\":\""
                        + sanitizeSseMessage(ex.getMessage() == null ? ex.toString() : ex.getMessage()) + "\"}"));
                } catch (Exception sendEx) {
                    log.debug("[CT-AI] failed to send async error event", sendEx);
                }
                emitter.complete();
            }
        });
        return emitter;
    }

    private String sanitizeSseMessage(String message) {
        if (message == null) {
            return "";
        }
        return message.replace("\\", "\\\\").replace("\"", "\\\"");
    }
}
