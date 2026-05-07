package org.eu.originalkeen.core.exception.system;

import org.eu.originalkeen.core.exception.SystemException;

import java.io.Serial;

/**
 * HTTP请求异常
 * 在发送HTTP请求过程中发生错误时抛出的异常
 */
public class HttpRequestException extends SystemException {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = 1171647117209380061L;

    /**
     * 构造函数
     * 创建一个带有错误消息和原因异常的HTTP请求异常
     *
     * @param message 错误消息
     * @param cause   原因异常
     */
    public HttpRequestException(String message, Throwable cause) {
        super(message, cause);
    }

}
