package com.westChina.ct.exception;

/**
 * MQ 异步识别任务被用户取消。
 */
public class TaskCancelledException extends IllegalStateException {

    public TaskCancelledException() {
        super("任务已取消");
    }

    public TaskCancelledException(String message) {
        super(message);
    }
}
