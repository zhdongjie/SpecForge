package org.eu.originalkeen.core.annotation;

import org.eu.originalkeen.core.enums.AccessType;

import java.lang.annotation.*;

/**
 * 访问日志注解
 * 用于标记需要记录访问日志的方法，配合AOP实现自动记录访问日志
 */
@Documented
@Target({ElementType.METHOD})
@Retention(RetentionPolicy.RUNTIME)
public @interface AccessLog {

    /**
     * 访问类型
     * 指定访问日志的类型，对应 {@link AccessType} 枚举
     *
     * @return 访问类型枚举值
     */
    AccessType value();

}
