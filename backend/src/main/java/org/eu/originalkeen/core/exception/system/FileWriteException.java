package org.eu.originalkeen.core.exception.system;

import org.eu.originalkeen.core.exception.SystemException;

import java.io.Serial;

/**
 * 文件写入异常
 * 在写入文件过程中发生错误时抛出的异常
 */
public class FileWriteException extends SystemException {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = 7868041374304588131L;

    /**
     * 构造函数
     * 创建一个带有错误消息和原因异常的文件写入异常
     *
     * @param message 错误消息
     * @param cause   原因异常
     */
    public FileWriteException(String message, Throwable cause) {
        super(message, cause);
    }

}
