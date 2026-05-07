package org.eu.originalkeen.core.utils;

import org.apache.commons.lang3.StringUtils;
import org.springframework.context.i18n.LocaleContextHolder;

import java.util.Locale;

/**
 * Locale 工具类
 * 提供获取当前请求 Locale 相关信息的方法
 */
public class LocaleUtils {

    /**
     * 获取当前请求 Locale
     * 从 LocaleContextHolder 获取当前请求 Locale
     */
    public static Locale getCurrentLocale() {
        return LocaleContextHolder.getLocale();
    }

    /**
     * 获取当前请求的标准语言码（zh-CN / en-US）
     * 从 Locale 获取当前请求的标准语言码
     */
    public static String getLangCode() {
        Locale locale = getCurrentLocale();

        if (StringUtils.isEmpty(locale.getCountry())) {
            return locale.getLanguage();
        }
        return locale.getLanguage() + "-" + locale.getCountry();
    }

    /**
     * 私有构造函数
     * 防止实例化工具类
     */
    private LocaleUtils() {
    }

}
