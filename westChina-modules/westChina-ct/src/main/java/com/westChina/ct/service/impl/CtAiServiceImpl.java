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
import com.westChina.ct.service.ICtAiService;
import com.westChina.ct.service.ICtDicomService;
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
    private ICtDicomService dicomService;

    @Autowired
    private TokenService tokenService;

    @Autowired
    private RemoteTenantService remoteTenantService;

    @Override
    public Map<String, Object> detectLesion(Map<String, Object> request) {
        log.info("[CT-AI] detectLesion start, request={}", summarizeRequest(request));
        Map<String, Object> aiRequest = buildAiRequest(request);
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
                request.get("dicomId"),
                body.get("lesions") instanceof java.util.List ? ((java.util.List<?>) body.get("lesions")).size() : "unknown");
            return body;
        } catch (RestClientException ex) {
            log.error("[CT-AI] 调用 AI 服务失败, url={}, request={}", url, summarizeRequest(request), ex);
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
        HttpURLConnection connection = null;
        try {
            if (aiRequest == null || aiRequest.isEmpty()) {
                throw new IllegalStateException("AI 请求未构建，请检查 prepareStreamDetectRequest");
            }
            log.info("[CT-AI] streamDetectLesion start, aiRequest={}", aiRequest);
            String url = trimTrailingSlash(ctAiProperties.getBaseUrl()) + "/detectLesion/stream";
            log.info("[CT-AI] opening python stream, url={}, payload={}", url, aiRequest);
            connection = (HttpURLConnection) new URL(url).openConnection();
            connection.setRequestMethod("POST");
            connection.setDoOutput(true);
            connection.setDoInput(true);
            connection.setConnectTimeout(ctAiProperties.getConnectTimeoutMs());
            connection.setReadTimeout(ctAiProperties.getReadTimeoutMs());
            connection.setRequestProperty("Content-Type", "application/json;charset=UTF-8");
            connection.setRequestProperty("Accept", "text/event-stream");

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

            try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(stream, StandardCharsets.UTF_8))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    if (line.startsWith("data:")) {
                        String data = line.length() > 5 ? line.substring(5).trim() : "";
                        log.debug("[CT-AI] stream event, seriesUid={}, data={}", aiRequest.get("seriesUid"), data);
                        emitter.send(SseEmitter.event().data(data));
                    }
                }
            }
            log.info("[CT-AI] streamDetectLesion complete, seriesUid={}", aiRequest.get("seriesUid"));
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
        } finally {
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
            ResponseEntity<Map<String, Object>> response = ctAiRestTemplate.exchange(
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
        List<Map<String, Object>> fallback = new ArrayList<>();
        fallback.add(engineOption("heuristic", "启发式 HU 分割", "传统图像处理，速度快", true, null));
        fallback.add(engineOption("totalsegmentator", "TotalSegmentator 肺分割", "需安装 totalsegmentator", false,
            "pip install totalsegmentator nibabel"));
        fallback.add(engineOption("monai-retinanet", "MONAI RetinaNet",
            "LUNA16 预训练 3D 肺结节检测（RetinaNet）", false,
            "pip install -r requirements-monai.txt"));
        return fallback;
    }

    private Map<String, Object> engineOption(String id, String label, String description, boolean available,
        String installHint) {
        Map<String, Object> item = new HashMap<>();
        item.put("id", id);
        item.put("label", label);
        item.put("description", description);
        item.put("available", available);
        if (installHint != null) {
            item.put("installHint", installHint);
        }
        return item;
    }
}
