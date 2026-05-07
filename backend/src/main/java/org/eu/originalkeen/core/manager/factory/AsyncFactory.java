package org.eu.originalkeen.core.manager.factory;

import org.eu.originalkeen.core.utils.SpringUtils;
import org.eu.originalkeen.system.log.access.domain.entity.AccessLogEntity;
import org.eu.originalkeen.system.log.access.service.AccessLogService;
import org.eu.originalkeen.system.log.operate.domain.entity.OperateLogEntity;
import org.eu.originalkeen.system.log.operate.service.OperateLogService;
import lombok.extern.slf4j.Slf4j;

import java.util.TimerTask;

/**
 * 异步工厂类
 * 用于创建各种异步定时任务，如记录日志等
 */
@Slf4j
public class AsyncFactory {

    /**
     * 记录访问日志
     * 创建一个异步定时任务，用于保存访问日志
     *
     * @param accessLogEntity 访问日志实体
     * @return 定时任务
     */
    public static TimerTask recordAccess(AccessLogEntity accessLogEntity) {
        return new TimerTask() {
            @Override
            public void run() {
                SpringUtils.getBean(AccessLogService.class).save(accessLogEntity);
            }
        };
    }

    /**
     * 记录操作日志
     * 创建一个异步定时任务，用于保存操作日志
     *
     * @param operateLogEntity 操作日志实体
     * @return 定时任务
     */
    public static TimerTask recordOperate(OperateLogEntity operateLogEntity) {
        return new TimerTask() {
            @Override
            public void run() {
                SpringUtils.getBean(OperateLogService.class).save(operateLogEntity);
            }
        };
    }

    /**
     * 私有构造函数
     * 防止实例化工具类
     */
    private AsyncFactory() {
    }

}
