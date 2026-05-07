package org.eu.originalkeen.core.domain;

/**
 * 字典接口
 * 用于定义字典类型的必要方法，如枚举类型等
 */
public interface Dictionary {

    /**
     * 获取标签
     * 返回字典项的显示标签
     *
     * @return 标签字符串
     */
    String getLabel();

    /**
     * 获取值
     * 返回字典项的实际值
     *
     * @return 字典项的值对象
     */
    String getValue();

}
