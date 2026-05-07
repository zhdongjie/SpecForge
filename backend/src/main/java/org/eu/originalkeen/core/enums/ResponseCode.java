package org.eu.originalkeen.core.enums;

import lombok.AllArgsConstructor;
import lombok.Getter;

/**
 * 响应状态码枚举
 * 定义系统中使用的标准响应状态码
 */
@Getter
@AllArgsConstructor
public enum ResponseCode {

    /**
     * 成功状态码
     * 请求处理成功
     */
    SUCCESS(20000),

    /**
     * 错误请求状态码
     * 请求参数有误或请求不符合要求
     */
    BAD_REQUEST(40000),

    /**
     * 未授权状态码
     * 用户未登录或登录已过期
     */
    UNAUTHORIZED(40100),

    /**
     * 禁止访问状态码
     * 用户没有权限访问该资源
     */
    FORBIDDEN(40300),

    /**
     * 服务器错误状态码
     * 服务器内部错误
     */
    SERVER_ERROR(50000),
    ;

    /**
     * 状态码值
     * 响应状态码的数值
     */
    private final Integer value;

}
