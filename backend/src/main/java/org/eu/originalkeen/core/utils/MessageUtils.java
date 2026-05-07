package org.eu.originalkeen.core.utils;

import lombok.extern.slf4j.Slf4j;
import org.springframework.context.MessageSource;
import org.springframework.context.NoSuchMessageException;

import java.util.Arrays;

/**
 * 消息国际化工具类
 * 提供根据消息代码获取国际化消息的功能
 */
@Slf4j
public class MessageUtils {

    /**
     * 消息源
     * 用于获取国际化消息的Spring消息源对象
     */
    private static final MessageSource messageSource = SpringUtils.getBean(MessageSource.class);

    /**
     * 获取国际化消息
     * 根据消息代码和参数获取当前语言环境下的国际化消息
     *
     * @param code 消息代码
     * @param args 消息参数，用于格式化消息
     * @return 国际化消息，如果消息代码不存在则返回代码本身
     */
    public static String message(String code, Object... args) {
        try {
            return messageSource.getMessage(code, args, LocaleUtils.getCurrentLocale());
        } catch (NoSuchMessageException exception) {
            log.warn("No message found for code: {} with args: {}", code, Arrays.toString(args));
            return code;
        }
    }

    /**
     * 私有构造函数
     * 防止实例化工具类
     */
    private MessageUtils() {
    }

}
