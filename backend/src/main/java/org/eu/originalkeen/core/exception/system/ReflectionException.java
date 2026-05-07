package org.eu.originalkeen.core.exception.system;

import org.eu.originalkeen.core.exception.SystemException;

import java.io.Serial;

/**
 * 反射异常
 * 在反射操作过程中发生错误时抛出的异常
 */
public class ReflectionException extends SystemException {

    @Serial
    private static final long serialVersionUID = -8814251699125888056L;

    /**
     * 构造函数
     * 创建一个带有错误消息和原因异常的反射异常
     *
     * @param message 异常消息
     * @param cause   原始异常
     */
    public ReflectionException(String message, Throwable cause) {
        super(message, cause);
    }

}
