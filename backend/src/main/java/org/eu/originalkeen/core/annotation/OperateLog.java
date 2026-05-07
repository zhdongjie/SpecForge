package org.eu.originalkeen.core.annotation;

import org.eu.originalkeen.core.enums.OperateType;

import java.lang.annotation.*;

/**
 * 操作日志注解
 * 用于标记需要记录操作日志的方法，配合AOP实现自动记录操作日志
 */
@Documented
@Target({ElementType.METHOD})
@Retention(RetentionPolicy.RUNTIME)
public @interface OperateLog {

    /**
     * 操作标题
     * 操作的标题或名称
     *
     * @return 操作标题
     */
    String title();

    /**
     * 操作类型
     * 操作的类型，如新增、修改、删除等
     *
     * @return 操作类型枚举值
     */
    OperateType operateType();

    /**
     * 是否保存请求参数
     * 是否将请求参数保存到操作日志中
     *
     * @return 如果保存请求参数返回true，默认为true
     */
    boolean isSaveRequestParam() default true;

    /**
     * 是否保存响应结果
     * 是否将响应结果保存到操作日志中
     *
     * @return 如果保存响应结果返回true，默认为true
     */
    boolean isSaveResponseResult() default true;

    /**
     * 排除的参数名称
     * 不需要保存到操作日志中的参数名称数组
     *
     * @return 排除的参数名称数组，默认为空数组
     */
    String[] excludeParamNames() default {};

}
