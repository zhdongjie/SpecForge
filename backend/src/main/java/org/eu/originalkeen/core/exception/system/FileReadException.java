package org.eu.originalkeen.core.exception.system;

import org.eu.originalkeen.core.exception.SystemException;

import java.io.Serial;

/**
 * 文件读取异常
 * 在读取文件过程中发生错误时抛出的异常
 */
public class FileReadException extends SystemException {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = 4081489128542148211L;

    /**
     * 构造函数
     * 创建一个带有错误消息和原因异常的文件读取异常
     *
     * @param message 错误消息
     * @param cause   原因异常
     */
    public FileReadException(String message, Throwable cause) {
        super(message, cause);
    }

}
