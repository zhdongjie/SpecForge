package org.eu.originalkeen.core.exception.system;

import org.eu.originalkeen.core.exception.SystemException;

import java.io.Serial;

/**
 * JWK生成异常
 * 在生成JSON Web Key过程中发生错误时抛出的异常
 */
public class JwkGenerationException extends SystemException {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = 6900347079972489159L;

    /**
     * 构造函数
     * 创建一个带有错误消息和原因异常的JWK生成异常
     *
     * @param message 错误消息
     * @param cause   原因异常
     */
    public JwkGenerationException(String message, Throwable cause) {
        super(message, cause);
    }

}
