package com.westChina.ct.service.impl;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.westChina.common.core.domain.R;
import com.westChina.common.core.utils.ServletUtils;
import com.westChina.common.core.utils.StringUtils;
import com.westChina.common.security.service.TokenService;
import com.westChina.ct.config.CtAiProperties;
import com.westChina.ct.domain.CtDicom;
import com.westChina.ct.exception.TaskCancelledException;
import com.westChina.ct.service.ICtAiService;
import com.westChina.ct.service.ICtDicomService;
import com.westChina.ct.support.CtAiTaskCancellationRegistry;
import com.westChina.system.api.model.LoginUser;
import com.westChina.tenant.api.feign.RemoteTenantService;

@Service
public class CtAiServiceImpl implements ICtAiService {

    private static final Logger log = LoggerFactory.getLogger(CtAiServiceImpl.class);

    private final ObjectMapper objectMapper = new ObjectMapper();

    @Autowired
    private CtAiProperties ctAiProperties;

    @Autowired
    @Qualifier("ctAiRestTemplate")
    private RestTemplate ctAiRestTemplate;

    @Autowired
    @Qualifier("ctAiQuickRestTemplate")
    private RestTemplate ctAiQuickRestTemplate;

    @Autowired
    private ICtDicomService dicomService;

    @Autowired
    private TokenService tokenService;

    @Autowired
    private RemoteTenantService remoteTenantService;

    @Autowired
    private CtAiTaskCancellationRegistry cancellationRegistry;

    @Override
    public Map<String, Object> detectLesion(Map<String, Object> request) {
        log.info("[CT-AI] detectLesion start, request={}", summarizeRequest(request));
        Map<String, Object> aiRequest = buildAiRequest(request);
        return detectLesionByAiRequest(aiRequest);
    }

    @Override
    public Map<String, Object> detectLesionByAiRequest(Map<String, Object> aiRequest) {
        String url = trimTrailingSlash(ctAiProperties.getBaseUrl()) + "/detectLesion";
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<Map<String, Object>> entity = new HttpEntity<>(aiRequest, headers);

        try {
            ResponseEntity<Map<String, Object>> response = ctAiRestTemplate.exchange(
                url,
                HttpMethod.POST,
                entity,
                new ParameterizedTypeReference<Map<String, Object>>() {}
            );
            Map<String, Object> body = response.getBody();
            if (body == null) {
                throw new IllegalStateException("AI 服务返回空响应");
            }
            log.info("[CT-AI] detectLesion success, dicomId={}, lesions={}",
                aiRequest.get("dicomId"),
                body.get("lesions") instanceof java.util.List ? ((java.util.List<?>) body.get("lesions")).size() : "unknown");
            return body;
        } catch (RestClientException ex) {
            log.error("[CT-AI] 调用 AI 服务失败, url={}, aiRequest={}", url, aiRequest, ex);
            throw new IllegalStateException(
                "AI 推理服务不可用，请确认 ai-service 已启动（scripts/start-ai.sh）: " + ex.getMessage(), ex);
        }
    }

    @Override
    public Map<String, Object> prepareStreamDetectRequest(Map<String, Object> request) {
        Map<String, Object> aiRequest = buildAiRequest(request);
        log.info("[CT-AI] stream request prepared, dicomId={}, aiRequest={}",
            request == null ? null : request.get("dicomId"), aiRequest);
        return aiRequest;
    }

    @Override
    public void streamDetectLesion(Map<String, Object> aiRequest, SseEmitter emitter) {
        try {
            detectLesionStreamCollect(aiRequest, event -> {
                try {
                    emitter.send(SseEmitter.event().data(objectMapper.writeValueAsString(event)));
                } catch (Exception sendEx) {
                    throw new IllegalStateException("发送 SSE 事件失败: " + sendEx.getMessage(), sendEx);
                }
            });
            emitter.complete();
        } catch (Exception ex) {
            log.error("[CT-AI] AI 流式识别失败, aiRequest={}", aiRequest, ex);
            try {
                String message = ex.getMessage() == null ? ex.toString() : ex.getMessage();
                emitter.send(SseEmitter.event().data(
                    objectMapper.writeValueAsString(
                        new HashMap<String, Object>() {{
                            put("type", "error");
                            put("message", message);
                        }}
                    )
                ));
            } catch (Exception sendEx) {
                log.debug("发送 SSE 错误事件失败", sendEx);
            }
            emitter.complete();
        }
    }

    @Override
    public void cancelRemoteDetectTask(String taskId) {
        if (taskId == null || taskId.trim().isEmpty()) {
            return;
        }
        String url = trimTrailingSlash(ctAiProperties.getBaseUrl()) + "/detectLesion/cancel/" + taskId;
        try {
            ctAiQuickRestTemplate.exchange(
                url,
                HttpMethod.POST,
                new HttpEntity<>(new HttpHeaders()),
                new ParameterizedTypeReference<Map<String, Object>>() {}
            );
            log.info("[CT-AI] remote cancel notified, taskId={}", taskId);
        } catch (Exception ex) {
            log.warn("[CT-AI] remote cancel notify failed, taskId={}, msg={}", taskId, ex.getMessage());
        }
    }

    @Override
    @SuppressWarnings("unchecked")
    public Map<String, Object> detectLesionStreamCollect(
        Map<String, Object> aiRequest,
        java.util.function.Consumer<Map<String, Object>> onEvent
    ) {
        return detectLesionStreamCollect(aiRequest, onEvent, null);
    }

    @Override
    @SuppressWarnings("unchecked")
    public Map<String, Object> detectLesionStreamCollect(
        Map<String, Object> aiRequest,
        java.util.function.Consumer<Map<String, Object>> onEvent,
        String taskId
    ) {
        HttpURLConnection connection = null;
        try {
            if (aiRequest == null || aiRequest.isEmpty()) {
                throw new IllegalStateException("AI 请求未构建，请检查 prepareStreamDetectRequest");
            }
            if (taskId != null && cancellationRegistry.isCancelled(taskId)) {
                throw new TaskCancelledException();
            }
            log.info("[CT-AI] detectLesionStreamCollect start, taskId={}, aiRequest={}", taskId, aiRequest);
            String url = trimTrailingSlash(ctAiProperties.getBaseUrl()) + "/detectLesion/stream";
            connection = (HttpURLConnection) new URL(url).openConnection();
            connection.setRequestMethod("POST");
            connection.setDoOutput(true);
            connection.setDoInput(true);
            connection.setConnectTimeout(ctAiProperties.getConnectTimeoutMs());
            connection.setReadTimeout(ctAiProperties.getReadTimeoutMs());
            connection.setRequestProperty("Content-Type", "application/json;charset=UTF-8");
            connection.setRequestProperty("Accept", "text/event-stream");
            if (taskId != null) {
                cancellationRegistry.registerConnection(taskId, connection);
            }

            byte[] bodyBytes = objectMapper.writeValueAsBytes(aiRequest);
            try (OutputStream os = connection.getOutputStream()) {
                os.write(bodyBytes);
            }

            int status = connection.getResponseCode();
            log.info("[CT-AI] python stream response status={}, seriesUid={}", status, aiRequest.get("seriesUid"));
            InputStream stream = status >= 400 ? connection.getErrorStream() : connection.getInputStream();
            if (stream == null) {
                throw new IllegalStateException("AI 流式服务无响应，HTTP " + status);
            }

            Map<String, Object> result = null;
            try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(stream, StandardCharsets.UTF_8))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    if (taskId != null && cancellationRegistry.isCancelled(taskId)) {
                        connection.disconnect();
                        throw new TaskCancelledException();
                    }
                    if (!line.startsWith("data:")) {
                        continue;
                    }
                    String data = line.length() > 5 ? line.substring(5).trim() : "";
                    if (data.isEmpty()) {
                        continue;
                    }
                    Map<String, Object> event = objectMapper.readValue(data, Map.class);
                    if (onEvent != null) {
                        onEvent.accept(event);
                    }
                    String type = String.valueOf(event.get("type"));
                    if ("result".equals(type)) {
                        Object payload = event.get("data");
                        if (payload instanceof Map) {
                            result = (Map<String, Object>) payload;
                        }
                    } else if ("error".equals(type)) {
                        Object message = event.get("message");
                        throw new IllegalStateException(message == null ? "AI 识别失败" : String.valueOf(message));
                    }
                }
            }
            if (result == null) {
                throw new IllegalStateException("AI 流式识别未返回结果");
            }
            log.info("[CT-AI] detectLesionStreamCollect complete, seriesUid={}", aiRequest.get("seriesUid"));
            return result;
        } catch (TaskCancelledException ex) {
            throw ex;
        } catch (Exception ex) {
            if (taskId != null && cancellationRegistry.isCancelled(taskId)) {
                throw new TaskCancelledException();
            }
            log.error("[CT-AI] detectLesionStreamCollect failed, aiRequest={}", aiRequest, ex);
            if (ex instanceof IllegalStateException) {
                throw (IllegalStateException) ex;
            }
            throw new IllegalStateException(ex.getMessage() == null ? ex.toString() : ex.getMessage(), ex);
        } finally {
            if (taskId != null) {
                cancellationRegistry.unregisterConnection(taskId);
            }
            if (connection != null) {
                connection.disconnect();
            }
        }
    }

    private Map<String, Object> buildAiRequest(Map<String, Object> request) {
        log.info("[CT-AI] buildAiRequest begin, rawRequest={}", summarizeRequest(request));
        String bodyPart = stringVal(request.get("bodyPart"));
        if (!isChestBodyPart(bodyPart)) {
            throw new IllegalArgumentException("当前仅支持胸部 CT 病灶识别，检查部位：" + bodyPart);
        }

        Long dicomId = parseLong(request.get("dicomId"));
        if (dicomId == null) {
            throw new IllegalArgumentException("缺少 dicomId");
        }

        CtDicom query = new CtDicom(dicomId);
        CtDicom dicom = dicomService.selectDicomByDicomId(query);
        if (dicom == null) {
            throw new IllegalArgumentException("未找到 DICOM 序列记录：" + dicomId);
        }
        log.info("[CT-AI] dicom record loaded, dicomId={}, studyUid={}, seriesUid={}, bodyPart={}, count={}",
            dicom.getDicomId(), dicom.getDicomCtStudyUid(), dicom.getDicomCtSeriesUid(),
            dicom.getDicomCtBody(), dicom.getDicomCtCount());

        String bucketName = stringVal(request.get("bucket"));
        if (StringUtils.isEmpty(bucketName)) {
            bucketName = resolveBucketName();
        }
        if (StringUtils.isEmpty(bucketName)) {
            throw new IllegalStateException("无法获取租户 MinIO 存储桶");
        }
        log.info("[CT-AI] tenant bucket resolved, dicomId={}, bucket={}", dicomId, bucketName);

        int imageCount = parseInt(request.get("imageCount"),
            dicom.getDicomCtCount() == null ? 0 : dicom.getDicomCtCount().intValue());
        if (imageCount <= 0) {
            imageCount = dicom.getDicomCtCount() == null ? 0 : dicom.getDicomCtCount().intValue();
        }
        if (imageCount <= 0) {
            throw new IllegalArgumentException("序列切片数量为 0");
        }

        String studyUid = firstNonEmpty(stringVal(request.get("studyUid")), dicom.getDicomCtStudyUid());
        String seriesUid = firstNonEmpty(stringVal(request.get("seriesUid")), dicom.getDicomCtSeriesUid());
        if (StringUtils.isEmpty(studyUid) || StringUtils.isEmpty(seriesUid)) {
            throw new IllegalArgumentException("缺少 studyUid 或 seriesUid");
        }

        if (!ctAiProperties.isEnabled()) {
            throw new IllegalStateException("AI 推理服务未启用");
        }

        Map<String, Object> aiRequest = new HashMap<>();
        aiRequest.put("bucket", bucketName);
        aiRequest.put("dicomId", dicomId);
        aiRequest.put("studyUid", studyUid);
        aiRequest.put("seriesUid", seriesUid);
        aiRequest.put("dicomCtPath", dicom.getDicomCtPath());
        aiRequest.put("imageCount", imageCount);
        aiRequest.put("bodyPart", firstNonEmpty(bodyPart, dicom.getDicomCtBody()));
        aiRequest.put("currentSliceIndex", parseInt(request.get("currentSliceIndex"), 0));
        aiRequest.put("detectEngine", firstNonEmpty(stringVal(request.get("detectEngine")), "heuristic"));
        aiRequest.put("detectMode", resolveDetectMode(request));
        aiRequest.put("singleSlice", isSingleSliceRequest(request));
        aiRequest.put("sliceIndex", parseInt(request.get("sliceIndex"), parseInt(request.get("currentSliceIndex"), 0)));
        aiRequest.put("detectSubEngine", firstNonEmpty(stringVal(request.get("detectSubEngine")), "auto"));
        String enhancedSeriesUid = stringVal(request.get("enhancedSeriesUid"));
        if (StringUtils.isNotEmpty(enhancedSeriesUid)) {
            aiRequest.put("enhancedSeriesUid", enhancedSeriesUid);
            int enhancedImageCount = parseInt(request.get("enhancedImageCount"), 0);
            if (enhancedImageCount > 0) {
                aiRequest.put("enhancedImageCount", enhancedImageCount);
            }
        }
        aiRequest.put("taskId", stringVal(request.get("taskId")));
        log.info("[CT-AI] buildAiRequest success, dicomId={}, aiRequest={}", dicomId, aiRequest);
        return aiRequest;
    }

    private String resolveBucketName() {
        LoginUser loginUser = tokenService.getLoginUser(ServletUtils.getRequest());
        if (loginUser == null || StringUtils.isEmpty(loginUser.getEnterpriseName())) {
            log.warn("[CT-AI] resolveBucketName failed, loginUser or enterpriseName empty. loginUser={}",
                loginUser == null ? "null" : loginUser.getUserId());
            return null;
        }
        log.info("[CT-AI] resolving bucket for enterprise={}", loginUser.getEnterpriseName());
        R<String> bucketResult = remoteTenantService.getBucketNameByEnterpriseName(loginUser.getEnterpriseName());
        if (bucketResult == null) {
            log.warn("[CT-AI] bucket service returned null for enterprise={}", loginUser.getEnterpriseName());
            return null;
        }
        log.info("[CT-AI] bucket service response, enterprise={}, bucket={}, msg={}",
            loginUser.getEnterpriseName(), bucketResult.getData(), bucketResult.getMsg());
        return bucketResult.getData();
    }

    private String summarizeRequest(Map<String, Object> request) {
        if (request == null) {
            return "null";
        }
        Map<String, Object> safe = new HashMap<>();
        safe.put("dicomId", request.get("dicomId"));
        safe.put("studyUid", request.get("studyUid"));
        safe.put("seriesUid", request.get("seriesUid"));
        safe.put("bodyPart", request.get("bodyPart"));
        safe.put("currentSliceIndex", request.get("currentSliceIndex"));
        safe.put("imageCount", request.get("imageCount"));
        safe.put("bucket", request.get("bucket"));
        safe.put("detectEngine", request.get("detectEngine"));
        safe.put("detectMode", request.get("detectMode"));
        safe.put("detect_mode", request.get("detect_mode"));
        safe.put("singleSlice", request.get("singleSlice"));
        safe.put("sliceIndex", request.get("sliceIndex"));
        safe.put("detectSubEngine", request.get("detectSubEngine"));
        safe.put("enhancedSeriesUid", request.get("enhancedSeriesUid"));
        safe.put("enhancedImageCount", request.get("enhancedImageCount"));
        return safe.toString();
    }

    private boolean isChestBodyPart(String bodyPart) {
        if (StringUtils.isEmpty(bodyPart)) {
            return false;
        }
        String upper = bodyPart.toUpperCase();
        return upper.contains("CHEST") || upper.contains("THORAX") || upper.contains("LUNG")
            || bodyPart.contains("胸") || bodyPart.contains("肺");
    }

    private String stringVal(Object value) {
        return value == null ? "" : value.toString();
    }

    private String resolveDetectMode(Map<String, Object> request) {
        String mode = firstNonEmpty(
            stringVal(request.get("detectMode")),
            stringVal(request.get("detect_mode"))
        );
        if (StringUtils.isNotEmpty(mode)) {
            return mode.trim().toLowerCase();
        }
        if (isSingleSliceRequest(request)) {
            return "single";
        }
        return "series";
    }

    private boolean isSingleSliceRequest(Map<String, Object> request) {
        if (request == null) {
            return false;
        }
        Object flag = request.get("singleSlice");
        if (Boolean.TRUE.equals(flag)) {
            return true;
        }
        if (flag instanceof String) {
            return "true".equalsIgnoreCase((String) flag);
        }
        return false;
    }

    private String firstNonEmpty(String a, String b) {
        if (StringUtils.isNotEmpty(a)) {
            return a;
        }
        return b == null ? "" : b;
    }

    private Long parseLong(Object value) {
        if (value == null) {
            return null;
        }
        if (value instanceof Number) {
            return ((Number) value).longValue();
        }
        try {
            return Long.parseLong(value.toString());
        } catch (NumberFormatException ex) {
            return null;
        }
    }

    private int parseInt(Object value, int defaultValue) {
        if (value == null) {
            return defaultValue;
        }
        if (value instanceof Number) {
            return ((Number) value).intValue();
        }
        try {
            return Integer.parseInt(value.toString());
        } catch (NumberFormatException ex) {
            return defaultValue;
        }
    }

    private String trimTrailingSlash(String url) {
        if (url == null) {
            return "";
        }
        return url.endsWith("/") ? url.substring(0, url.length() - 1) : url;
    }

    @Override
    @SuppressWarnings("unchecked")
    public List<Map<String, Object>> listDetectEngines() {
        String url = trimTrailingSlash(ctAiProperties.getBaseUrl()) + "/engines";
        try {
            ResponseEntity<Map<String, Object>> response = ctAiQuickRestTemplate.exchange(
                url,
                HttpMethod.GET,
                null,
                new ParameterizedTypeReference<Map<String, Object>>() {}
            );
            Map<String, Object> body = response.getBody();
            if (body != null && body.get("engines") instanceof List) {
                return (List<Map<String, Object>>) body.get("engines");
            }
        } catch (RestClientException ex) {
            log.warn("[CT-AI] listDetectEngines failed, url={}", url, ex);
        }
        return schemeEngineFallback("AI 服务未响应，请检查 ai-service 是否运行");
    }

    private List<Map<String, Object>> schemeEngineFallback(String unavailableReason) {
        List<Map<String, Object>> fallback = new ArrayList<>();
        fallback.add(schemeEngineOption("scheme-a", "肺区智能筛查",
            "肺区分割 + 形态学筛查，支持全序列与当前层",
            false, unavailableReason, null, new String[] { "series", "single" }, false, null));
        fallback.add(schemeEngineOption("scheme-b", "融合精准分析",
            "肺叶/血管 + 深度学习检测器 + GGO，仅全序列，需 GPU",
            false, unavailableReason, null, new String[] { "series" }, true,
            schemeBSubEngines(false)));
        fallback.add(schemeEngineOption("scheme-c", "单层异常倾向",
            "分类模型 + Grad-CAM 热力图，仅当前层（参考性筛查）",
            false, unavailableReason, null, new String[] { "single" }, false, null));
        return fallback;
    }

    private List<Map<String, Object>> schemeBSubEngines(boolean available) {
        List<Map<String, Object>> subs = new ArrayList<>();
        subs.add(subEngineOption("auto", "自动", "自动选择最优检测器", available, null));
        subs.add(subEngineOption("monai", "MONAI RetinaNet", "MONAI LUNA16 bundle", false,
            unavailableReasonOrEmpty(available, "MONAI bundle 未就绪")));
        subs.add(subEngineOption("nndet", "nnDetection (LUNA16)", "需下载权重", false,
            unavailableReasonOrEmpty(available, "权重未就绪")));
        return subs;
    }

    private String unavailableReasonOrEmpty(boolean available, String reason) {
        return available ? "" : reason;
    }

    private Map<String, Object> subEngineOption(String id, String label, String description,
        boolean available, String unavailableReason) {
        Map<String, Object> item = new HashMap<>();
        item.put("id", id);
        item.put("label", label);
        item.put("description", description);
        item.put("available", available);
        if (unavailableReason != null && !unavailableReason.isEmpty()) {
            item.put("unavailableReason", unavailableReason);
        }
        return item;
    }

    private Map<String, Object> schemeEngineOption(String id, String label, String description,
        boolean available, String unavailableReason, String installHint, String[] supportedModes,
        boolean requiresGpu, List<Map<String, Object>> subEngines) {
        Map<String, Object> item = new HashMap<>();
        item.put("id", id);
        item.put("label", label);
        item.put("description", description);
        item.put("available", available);
        if (unavailableReason != null && !unavailableReason.isEmpty()) {
            item.put("unavailableReason", unavailableReason);
        }
        if (installHint != null && !installHint.isEmpty()) {
            item.put("installHint", installHint);
        }
        if (requiresGpu) {
            item.put("requiresGpu", true);
        }
        if (supportedModes != null && supportedModes.length > 0) {
            item.put("supportedModes", supportedModes);
        }
        if (subEngines != null) {
            item.put("subEngines", subEngines);
        }
        return item;
    }
}
