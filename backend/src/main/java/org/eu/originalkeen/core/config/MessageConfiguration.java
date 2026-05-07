package org.eu.originalkeen.core.config;

import org.springframework.context.MessageSource;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.validation.beanvalidation.LocalValidatorFactoryBean;

/**
 * 消息配置类
 * 配置校验消息源，用于国际化校验错误消息
 */
@Configuration
public class MessageConfiguration {

    /**
     * 校验器工厂Bean
     * 配置校验器使用消息源进行错误消息国际化
     *
     * @param messageSource 消息源
     * @return 本地校验器工厂Bean
     */
    @Bean
    public LocalValidatorFactoryBean validator(MessageSource messageSource) {
        LocalValidatorFactoryBean validator = new LocalValidatorFactoryBean();
        validator.setValidationMessageSource(messageSource);
        return validator;
    }

}
