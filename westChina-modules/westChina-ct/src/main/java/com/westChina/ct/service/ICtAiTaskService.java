package com.westChina.ct.service;

import java.util.Map;

public interface ICtAiTaskService {

    /**
     * 提交 AI 异步任务，返回 taskId。
     */
    String submitDetectTask(Map<String, Object> request);

    /**
     * 查询任务状态。
     */
    Map<String, Object> getTaskStatus(String taskId);

    /**
     * 取消排队中或执行中的任务。
     */
    boolean cancelDetectTask(String taskId);
}

