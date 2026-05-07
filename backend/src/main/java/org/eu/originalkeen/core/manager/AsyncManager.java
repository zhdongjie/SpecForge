package org.eu.originalkeen.core.manager;

import org.eu.originalkeen.core.utils.SpringUtils;

import java.util.TimerTask;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

/**
 * 异步管理器
 * 用于管理异步定时任务的执行，采用单例模式
 */
public class AsyncManager {

    /**
     * 操作延迟时间（毫秒）
     * 异步定时任务执行前的延迟时间
     */
    private static final int OPERATE_DELAY_TIME = 10;

    /**
     * 调度执行器服务
     * 用于执行异步定时任务的线程池
     */
    private final ScheduledExecutorService executor = SpringUtils.getBean(ScheduledExecutorService.class);

    /**
     * 异步管理器单例
     * 全局唯一的异步管理器实例
     */
    private static final AsyncManager asyncManager = new AsyncManager();

    /**
     * 获取异步管理器实例
     * 返回全局唯一的异步管理器实例
     *
     * @return 异步管理器实例
     */
    public static AsyncManager instance() {
        return asyncManager;
    }

    /**
     * 执行异步定时任务
     * 将定时任务提交到调度执行器进行异步执行
     *
     * @param task 要执行的定时任务
     */
    public void execute(TimerTask task) {
        executor.schedule(task, OPERATE_DELAY_TIME, TimeUnit.MILLISECONDS);
    }

    /**
     * 关闭执行器
     * 关闭调度执行器服务，通常在应用关闭时调用
     */
    public void shutdown() {
        executor.shutdown();
    }

    /**
     * 私有构造函数
     * 防止外部实例化，确保单例模式
     */
    private AsyncManager() {
    }

}
