package org.eu.originalkeen.core.exception;

import java.io.Serial;

/**
 * 系统异常类
 * 用于表示系统内部错误或异常情况，不应该展示给用户的异常
 */
public class SystemException extends RuntimeException {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -2852470876657287678L;

    /**
     * 构造函数
     * 创建一个包含错误消息的系统异常
     *
     * @param message 错误消息
     */
    protected SystemException(String message) {
        super(message);
    }

    /**
     * 构造函数
     * 创建一个包含错误消息和原因异常的系统异常
     *
     * @param message 错误消息
     * @param cause   原因异常
     */
    protected SystemException(String message, Throwable cause) {
        super(message, cause);
    }

}
