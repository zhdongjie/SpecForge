package org.eu.originalkeen.core.exception;

import org.eu.originalkeen.core.utils.MessageUtils;
import lombok.Getter;

import java.io.Serial;

/**
 * 业务异常类
 * 用于表示业务逻辑处理过程中的异常情况
 */
@Getter
public class BusinessException extends RuntimeException {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = 8717361286172109868L;

    /**
     * 构造函数
     * 创建一个业务异常
     *
     * @param messageKey 响应消息键
     * @param args       消息参数，用于格式化消息
     */
    public BusinessException(String messageKey, Object... args) {
        super(MessageUtils.message(messageKey, args));
    }

}
