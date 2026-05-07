package org.eu.originalkeen.core.utils;

import lombok.NonNull;
import org.springframework.beans.BeansException;
import org.springframework.beans.factory.ListableBeanFactory;
import org.springframework.beans.factory.config.BeanFactoryPostProcessor;
import org.springframework.beans.factory.config.ConfigurableListableBeanFactory;
import org.springframework.context.ApplicationContext;
import org.springframework.context.ApplicationContextAware;
import org.springframework.stereotype.Component;

import java.util.Objects;

/**
 * Spring工具类
 * 提供获取Spring容器中的Bean的工具方法
 */
@Component
public class SpringUtils implements BeanFactoryPostProcessor, ApplicationContextAware {

    /**
     * Bean工厂
     * 用于获取Spring容器中的Bean
     */
    private static ConfigurableListableBeanFactory beanFactory;

    /**
     * 应用上下文
     * Spring应用程序上下文
     */
    private static ApplicationContext applicationContext;

    /**
     * 处理Bean工厂
     * 在Bean工厂初始化后调用，用于获取Bean工厂实例
     *
     * @param beanFactory Bean工厂
     * @throws BeansException 如果处理过程中发生错误则抛出异常
     */
    @Override
    public void postProcessBeanFactory(@NonNull ConfigurableListableBeanFactory beanFactory) throws BeansException {
        if (Objects.isNull(SpringUtils.beanFactory)) {
            SpringUtils.beanFactory = beanFactory;
        }
    }

    /**
     * 设置应用上下文
     * 在应用上下文初始化后调用，用于获取应用上下文实例
     *
     * @param applicationContext 应用上下文
     */
    @Override
    public void setApplicationContext(@NonNull ApplicationContext applicationContext) {
        if (Objects.isNull(SpringUtils.applicationContext)) {
            SpringUtils.applicationContext = applicationContext;
        }
    }

    /**
     * 获取Bean工厂
     * 获取可用于检索Bean的工厂实例
     *
     * @return 可列举的Bean工厂
     * @throws IllegalStateException 如果SpringUtils未正确初始化则抛出异常
     */
    public static ListableBeanFactory getBeanFactory() {
        if (Objects.nonNull(beanFactory)) {
            return beanFactory;
        }
        if (Objects.nonNull(applicationContext)) {
            return applicationContext;
        }

        throw new IllegalStateException("SpringUtils has not been initialized properly");
    }

    /**
     * 获取Bean实例
     * 根据类型从容器中获取Bean实例
     *
     * @param clazz Bean类型
     * @param <T>   Bean类型参数
     * @return Bean实例
     * @throws BeansException 如果无法获取Bean则抛出异常
     */
    public static <T> T getBean(Class<T> clazz) {
        return getBeanFactory().getBean(clazz);
    }

    /**
     * 根据名称获取Bean实例
     * 通过Bean名称从容器中获取Bean实例
     *
     * @param name Bean名称
     * @return Bean实例
     * @throws BeansException 如果无法获取Bean则抛出异常
     */
    public static Object getBean(String name) throws BeansException {
        return beanFactory.getBean(name);
    }

}
