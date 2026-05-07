package org.eu.originalkeen.core.enums;

import lombok.AllArgsConstructor;
import lombok.Getter;

/**
 * 内容类型枚举
 * 定义系统使用的各种文件的MIME类型
 */
@Getter
@AllArgsConstructor
public enum ContentType {
    /**
     * JSON数据格式，用于返回 JSON 数据
     */
    JSON("application/json"),
    ;

    /**
     * MIME类型值
     * 内容类型的标准MIME类型字符串
     */
    private final String value;

}
