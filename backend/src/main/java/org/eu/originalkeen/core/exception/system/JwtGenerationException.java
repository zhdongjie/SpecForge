package org.eu.originalkeen.core.exception.system;

import org.eu.originalkeen.core.exception.SystemException;

import java.io.Serial;

/**
 * JWT生成异常
 * 在生成JWT令牌或JWK密钥过程中发生错误时抛出的异常
 */
public class JwtGenerationException extends SystemException {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -6636597991576685795L;

    /**
     * 构造函数
     * 创建一个带有错误消息和原因异常的JWT生成异常
     *
     * @param message 错误消息
     * @param cause   原因异常
     */
    public JwtGenerationException(String message, Throwable cause) {
        super(message, cause);
    }

}
