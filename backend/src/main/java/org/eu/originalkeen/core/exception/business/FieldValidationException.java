package org.eu.originalkeen.core.exception.business;

import org.eu.originalkeen.core.exception.BusinessException;
import lombok.Getter;

import java.io.Serial;

/**
 * 字段校验异常
 * 在表单字段校验过程中发生错误时抛出的异常
 */
@Getter
public class FieldValidationException extends BusinessException {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = 3825883991550980623L;

    /**
     * 发生错误的字段名
     */
    private final String field;

    /**
     * 构造函数
     * 创建一个字段校验异常
     *
     * @param field      发生错误的字段名
     * @param messageKey 错误消息键
     * @param args       消息参数，用于格式化消息
     */
    public FieldValidationException(String field, String messageKey, Object... args) {
        super(messageKey, args);
        this.field = field;
    }

}
