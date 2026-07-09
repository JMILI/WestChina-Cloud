package com.westChina.ct.support;

import java.net.HttpURLConnection;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.TimeUnit;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Component;

/**
 * CT AI 异步任务取消标记与进行中的 HTTP 流连接注册。
 */
@Component
public class CtAiTaskCancellationRegistry {

    private static final String CANCEL_KEY_PREFIX = "ct:ai:task:cancel:";
    private static final long CANCEL_TTL_HOURS = 24;

    private final RedisTemplate<String, String> redisTemplate;
    private final ConcurrentHashMap<String, HttpURLConnection> activeConnections = new ConcurrentHashMap<>();

    public CtAiTaskCancellationRegistry(RedisTemplate<String, String> redisTemplate) {
        this.redisTemplate = redisTemplate;
    }

    public void markCancelled(String taskId) {
        if (taskId == null || taskId.isEmpty()) {
            return;
        }
        redisTemplate.opsForValue().set(
            cancelKey(taskId),
            "1",
            CANCEL_TTL_HOURS,
            TimeUnit.HOURS
        );
        abortConnection(taskId);
    }

    public boolean isCancelled(String taskId) {
        if (taskId == null || taskId.isEmpty()) {
            return false;
        }
        return "1".equals(redisTemplate.opsForValue().get(cancelKey(taskId)));
    }

    public void registerConnection(String taskId, HttpURLConnection connection) {
        if (taskId == null || taskId.isEmpty() || connection == null) {
            return;
        }
        activeConnections.put(taskId, connection);
    }

    public void unregisterConnection(String taskId) {
        if (taskId == null || taskId.isEmpty()) {
            return;
        }
        activeConnections.remove(taskId);
    }

    public void abortConnection(String taskId) {
        if (taskId == null || taskId.isEmpty()) {
            return;
        }
        HttpURLConnection connection = activeConnections.remove(taskId);
        if (connection != null) {
            connection.disconnect();
        }
    }

    private String cancelKey(String taskId) {
        return CANCEL_KEY_PREFIX + taskId;
    }
}
