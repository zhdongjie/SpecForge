package org.eu.originalkeen.core.domain.vo;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;
import java.util.Set;

/**
 * 字段错误视图对象
 * 用于封装表单校验错误信息，包含字段名和错误消息列表
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class FieldErrorVo implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -5637925819174350065L;

    /**
     * 字段名
     * 发生错误的字段名称
     */
    private String field;

    /**
     * 错误消息列表
     * 与字段相关的错误消息列表
     */
    private Set<String> errors;

    /**
     * 创建FieldErrorVo实例
     * 工厂方法，用于创建字段错误视图对象
     *
     * @param field  字段名
     * @param errors 错误消息列表
     * @return FieldErrorVo实例
     */
    public static FieldErrorVo of(String field, Set<String> errors) {
        return new FieldErrorVo(field, errors);
    }

}
