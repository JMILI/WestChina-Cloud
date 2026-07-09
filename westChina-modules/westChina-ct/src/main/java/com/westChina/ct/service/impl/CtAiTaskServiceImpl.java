package com.westChina.ct.service.impl;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.westChina.common.core.utils.IdUtils;
import com.westChina.ct.config.CtAiTaskMqConfig;
import com.westChina.ct.exception.TaskCancelledException;
import com.westChina.ct.service.ICtAiService;
import com.westChina.ct.service.ICtAiTaskService;
import com.westChina.ct.support.CtAiTaskCancellationRegistry;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

import java.time.LocalTime;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;

@Service
public class CtAiTaskServiceImpl implements ICtAiTaskService {

    private static final Logger log = LoggerFactory.getLogger(CtAiTaskServiceImpl.class);
    private static final long TASK_TTL_HOURS = 24;
    private static final String TASK_KEY_PREFIX = "ct:ai:task:";

    private final ObjectMapper objectMapper = new ObjectMapper();
    private final RabbitTemplate rabbitTemplate;
    private final RedisTemplate<String, String> redisTemplate;
    private final ICtAiService ctAiService;
    private final CtAiTaskCancellationRegistry cancellationRegistry;

    public CtAiTaskServiceImpl(
        RabbitTemplate rabbitTemplate,
        RedisTemplate<String, String> redisTemplate,
        ICtAiService ctAiService,
        CtAiTaskCancellationRegistry cancellationRegistry
    ) {
        this.rabbitTemplate = rabbitTemplate;
        this.redisTemplate = redisTemplate;
        this.ctAiService = ctAiService;
        this.cancellationRegistry = cancellationRegistry;
    }

    @Override
    public String submitDetectTask(Map<String, Object> request) {
        String taskId = IdUtils.fastSimpleUUID();
        Map<String, Object> aiRequest = ctAiService.prepareStreamDetectRequest(request);
        aiRequest.put("taskId", taskId);

        List<Map<String, Object>> logs = new ArrayList<>();
        appendLogEntry(logs, "info", "[MQ] 任务已入队，等待消费者执行");

        Map<String, Object> task = new HashMap<>();
        task.put("taskId", taskId);
        task.put("status", "PENDING");
        task.put("message", "任务已提交，等待执行");
        task.put("dicomId", aiRequest.get("dicomId"));
        task.put("progress", 0);
        task.put("stage", "queued");
        task.put("logs", logs);
        task.put("logCount", logs.size());
        task.put("createdAt", System.currentTimeMillis());
        task.put("updatedAt", System.currentTimeMillis());
        saveTask(taskId, task);

        Map<String, Object> message = new HashMap<>();
        message.put("taskId", taskId);
        message.put("aiRequest", aiRequest);
        rabbitTemplate.convertAndSend(CtAiTaskMqConfig.EXCHANGE, CtAiTaskMqConfig.ROUTING_KEY, message);
        return taskId;
    }

    @Override
    public Map<String, Object> getTaskStatus(String taskId) {
        String raw = redisTemplate.opsForValue().get(taskKey(taskId));
        if (raw == null) {
            Map<String, Object> notFound = new HashMap<>();
            notFound.put("taskId", taskId);
            notFound.put("status", "NOT_FOUND");
            notFound.put("message", "任务不存在或已过期");
            notFound.put("logs", new ArrayList<>());
            return notFound;
        }
        try {
            Map<String, Object> task = objectMapper.readValue(raw, new TypeReference<Map<String, Object>>() {});
            normalizeTask(task);
            return task;
        } catch (Exception e) {
            Map<String, Object> failed = new HashMap<>();
            failed.put("taskId", taskId);
            failed.put("status", "ERROR");
            failed.put("message", "任务状态解析失败");
            failed.put("logs", new ArrayList<>());
            return failed;
        }
    }

    @Override
    public boolean cancelDetectTask(String taskId) {
        if (taskId == null || taskId.trim().isEmpty()) {
            throw new IllegalArgumentException("缺少 taskId");
        }
        Map<String, Object> task = getTaskStatus(taskId);
        String status = String.valueOf(task.get("status"));
        if ("NOT_FOUND".equals(status)) {
            throw new IllegalArgumentException("任务不存在或已过期");
        }
        if ("DONE".equals(status) || "FAILED".equals(status) || "CANCELLED".equals(status)) {
            return false;
        }
        cancellationRegistry.markCancelled(taskId);
        ctAiService.cancelRemoteDetectTask(taskId);
        List<Map<String, Object>> logs = ensureLogsList(task);
        appendLogEntry(logs, "warn", "[MQ] 用户取消任务");
        task.put("status", "CANCELLED");
        task.put("message", "任务已取消");
        task.put("stage", "cancelled");
        task.put("logs", logs);
        task.put("logCount", logs.size());
        task.put("updatedAt", System.currentTimeMillis());
        saveTask(taskId, task);
        return true;
    }

    @RabbitListener(queues = CtAiTaskMqConfig.QUEUE, concurrency = "${ct.ai.task-consumer-concurrency:4}")
    @SuppressWarnings("unchecked")
    public void consumeDetectTask(Map<String, Object> message) {
        String taskId = message == null ? null : String.valueOf(message.get("taskId"));
        if (taskId == null || "null".equals(taskId)) {
            return;
        }
        if (cancellationRegistry.isCancelled(taskId)) {
            log.info("[CT-AI] skip cancelled task in queue, taskId={}", taskId);
            return;
        }
        try {
            Map<String, Object> taskState = new HashMap<>(getTaskStatus(taskId));
            taskState.put("taskId", taskId);
            taskState.put("status", "RUNNING");
            taskState.put("message", "任务执行中");
            taskState.put("stage", "connect");
            taskState.put("updatedAt", System.currentTimeMillis());
            List<Map<String, Object>> logs = ensureLogsList(taskState);
            appendLogEntry(logs, "info", "[MQ] 消费者开始执行，连接 AI 推理服务…");
            taskState.put("logs", logs);
            taskState.put("logCount", logs.size());
            saveTask(taskId, taskState);

            Map<String, Object> aiRequest = (Map<String, Object>) message.get("aiRequest");
            if (aiRequest != null && aiRequest.get("dicomId") != null) {
                taskState.put("dicomId", aiRequest.get("dicomId"));
                aiRequest.putIfAbsent("taskId", taskId);
            }

            Map<String, Object> result = ctAiService.detectLesionStreamCollect(aiRequest, event -> {
                applyStreamEvent(event, taskState, logs);
                taskState.put("logs", logs);
                taskState.put("logCount", logs.size());
                taskState.put("status", "RUNNING");
                taskState.put("message", "任务执行中");
                taskState.put("updatedAt", System.currentTimeMillis());
                saveTask(taskId, taskState);
            }, taskId);

            if (cancellationRegistry.isCancelled(taskId)) {
                log.info("[CT-AI] task cancelled after stream, taskId={}", taskId);
                return;
            }

            Map<String, Object> done = new HashMap<>();
            done.put("taskId", taskId);
            done.put("status", "DONE");
            done.put("message", "识别完成");
            done.put("result", result);
            done.put("progress", 100);
            done.put("stage", "done");
            done.put("updatedAt", System.currentTimeMillis());
            saveTask(taskId, mergeKeepCreated(taskId, done));
        } catch (TaskCancelledException ex) {
            log.info("[CT-AI] async task cancelled, taskId={}", taskId);
        } catch (Exception ex) {
            if (cancellationRegistry.isCancelled(taskId)) {
                log.info("[CT-AI] async task cancelled during failure, taskId={}", taskId);
                return;
            }
            log.error("[CT-AI] async task failed, taskId={}", taskId, ex);
            Map<String, Object> failed = new HashMap<>();
            failed.put("taskId", taskId);
            failed.put("status", "FAILED");
            failed.put("message", ex.getMessage() == null ? "任务执行失败" : ex.getMessage());
            failed.put("updatedAt", System.currentTimeMillis());
            Map<String, Object> merged = mergeKeepCreated(taskId, failed);
            List<Map<String, Object>> logs = ensureLogsList(merged);
            appendLogEntry(logs, "error", merged.get("message").toString());
            merged.put("logs", logs);
            merged.put("logCount", logs.size());
            saveTask(taskId, merged);
        }
    }

    private void normalizeTask(Map<String, Object> task) {
        if (task == null) {
            return;
        }
        List<Map<String, Object>> logs = ensureLogsList(task);
        task.put("logs", logs);
        task.put("logCount", logs.size());
        if ("PENDING".equals(String.valueOf(task.get("status")))) {
            if (task.get("stage") == null || "".equals(String.valueOf(task.get("stage")))) {
                task.put("stage", "queued");
            }
        }
    }

    @SuppressWarnings("unchecked")
    private List<Map<String, Object>> ensureLogsList(Map<String, Object> task) {
        Object logs = task.get("logs");
        if (logs instanceof List) {
            return (List<Map<String, Object>>) logs;
        }
        List<Map<String, Object>> list = new ArrayList<>();
        task.put("logs", list);
        return list;
    }

    private void appendLogEntry(List<Map<String, Object>> logs, String level, String message) {
        Map<String, Object> entry = new HashMap<>();
        entry.put("time", formatLogTime());
        entry.put("level", level == null ? "info" : level);
        entry.put("message", message == null ? "" : message);
        logs.add(entry);
    }

    private String formatLogTime() {
        LocalTime t = LocalTime.now();
        return String.format("%02d:%02d:%02d", t.getHour(), t.getMinute(), t.getSecond());
    }

    private void applyStreamEvent(Map<String, Object> event, Map<String, Object> taskState, List<Map<String, Object>> logs) {
        if (event == null || event.get("type") == null) {
            return;
        }
        String type = String.valueOf(event.get("type"));
        switch (type) {
            case "log":
                appendLogEntry(logs, String.valueOf(event.getOrDefault("level", "info")), String.valueOf(event.get("message")));
                if (event.get("progress") != null) {
                    taskState.put("progress", event.get("progress"));
                }
                if (event.get("stage") != null) {
                    taskState.put("stage", event.get("stage"));
                }
                break;
            case "progress":
                if (event.get("percent") != null) {
                    taskState.put("progress", event.get("percent"));
                }
                if (event.get("stage") != null) {
                    taskState.put("stage", event.get("stage"));
                }
                if (event.get("message") != null) {
                    appendLogEntry(logs, "info", String.valueOf(event.get("message")));
                }
                break;
            case "stats": {
                Map<String, Object> stats = new HashMap<>();
                stats.put("lesionCount", event.get("lesionCount"));
                stats.put("candidates", event.get("candidates"));
                stats.put("lungVoxels", event.get("lungVoxels"));
                taskState.put("stats", stats);
                appendLogEntry(
                    logs,
                    "success",
                    String.format(
                        "统计：候选 %s 个，检出病灶 %s 处",
                        event.get("candidates"),
                        event.get("lesionCount")
                    )
                );
                break;
            }
            case "warn":
                appendLogEntry(
                    logs,
                    "warn",
                    String.valueOf(event.get("message") != null ? event.get("message") : event.get("code"))
                );
                break;
            case "step_start": {
                String label = event.get("label") != null
                    ? String.valueOf(event.get("label"))
                    : (event.get("step_id") != null ? String.valueOf(event.get("step_id")) : "处理中");
                appendLogEntry(logs, "info", "▶ " + label);
                break;
            }
            case "step_end": {
                StringBuilder sb = new StringBuilder("✓ ");
                sb.append(event.get("step_id") != null ? event.get("step_id") : "步骤");
                if (event.get("duration_ms") instanceof Number) {
                    double seconds = ((Number) event.get("duration_ms")).doubleValue() / 1000.0;
                    sb.append(String.format(" %.1fs", seconds));
                }
                appendLogEntry(logs, "success", sb.toString());
                break;
            }
            default:
                break;
        }
    }

    private Map<String, Object> mergeKeepCreated(String taskId, Map<String, Object> target) {
        Map<String, Object> existing = getTaskStatus(taskId);
        if (existing.get("createdAt") != null) {
            target.put("createdAt", existing.get("createdAt"));
        }
        if (existing.get("logs") != null && !target.containsKey("logs")) {
            target.put("logs", existing.get("logs"));
            target.put("logCount", existing.get("logCount"));
        }
        if (existing.get("progress") != null && !target.containsKey("progress")) {
            target.put("progress", existing.get("progress"));
        }
        if (existing.get("stage") != null && !target.containsKey("stage")) {
            target.put("stage", existing.get("stage"));
        }
        if (existing.get("stats") != null && !target.containsKey("stats")) {
            target.put("stats", existing.get("stats"));
        }
        if (existing.get("dicomId") != null && !target.containsKey("dicomId")) {
            target.put("dicomId", existing.get("dicomId"));
        }
        return target;
    }

    private void saveTask(String taskId, Map<String, Object> data) {
        try {
            normalizeTask(data);
            redisTemplate.opsForValue().set(
                taskKey(taskId),
                objectMapper.writeValueAsString(data),
                TASK_TTL_HOURS,
                TimeUnit.HOURS
            );
        } catch (Exception e) {
            log.error("[CT-AI] save task status failed, taskId={}", taskId, e);
        }
    }

    private String taskKey(String taskId) {
        return TASK_KEY_PREFIX + taskId;
    }
}
