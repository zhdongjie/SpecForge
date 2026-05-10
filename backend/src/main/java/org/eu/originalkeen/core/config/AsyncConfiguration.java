package org.eu.originalkeen.core.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;

/**
 * 异步执行配置
 * 为访问日志和操作日志提供统一的调度线程池。
 */
@Configuration
public class AsyncConfiguration {

    /**
     * 日志异步调度线程池
     * 使用固定大小线程池避免日志任务阻塞主请求线程。
     *
     * @return 可复用的调度执行器
     */
    @Bean(destroyMethod = "shutdown")
    public ScheduledExecutorService scheduledExecutorService() {
        return Executors.newScheduledThreadPool(4);
    }

}
