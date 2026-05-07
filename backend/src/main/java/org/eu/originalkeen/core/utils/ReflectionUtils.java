package org.eu.originalkeen.core.utils;

import org.eu.originalkeen.core.exception.system.ReflectionException;
import lombok.extern.slf4j.Slf4j;

import java.lang.reflect.Field;

/**
 * 反射工具类
 * 提供反射操作的工具方法，简化反射操作并统一异常处理
 */
@Slf4j
public class ReflectionUtils extends org.springframework.util.ReflectionUtils {

    /**
     * 安全地获取字段值
     * 使用反射安全地获取对象的字段值
     *
     * @param o         目标对象
     * @param fieldName 要获取的字段名称
     * @return 字段的值
     * @throws ReflectionException 如果获取字段值失败则抛出异常
     */
    public static Object getFieldValueSafely(Object o, String fieldName) {
        try {
            Field fieldObj = o.getClass().getDeclaredField(fieldName);
            makeAccessible(fieldObj);
            return fieldObj.get(o);
        } catch (NoSuchFieldException | IllegalAccessException exception) {
            log.error("Failed to get field value: {}.{}", o.getClass().getName(), fieldName, exception);
            throw new ReflectionException(exception.getMessage(), exception);
        }
    }

    /**
     * 私有构造函数
     * 防止实例化工具类
     */
    private ReflectionUtils() {
    }

}
