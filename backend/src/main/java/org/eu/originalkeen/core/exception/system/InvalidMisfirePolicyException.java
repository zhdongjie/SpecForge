package org.eu.originalkeen.core.exception.system;

import org.eu.originalkeen.core.exception.SystemException;
import lombok.Getter;

import java.io.Serial;

/**
 * 无效的定时任务失败策略异常
 * 当定时任务配置了无效的定时任务失败策略（MisfirePolicy）时抛出的异常
 * <p>
 * 定时任务失败策略用于定义当定时任务错过原定执行时间后的处理方式，如：
 * - 默认策略（DEFAULT）：使用Quartz的默认处理方式
 * - 忽略失败（IGNORE_MISFIRES）：忽略所有失败的触发器，立即触发
 * - 触发并继续（FIRE_AND_PROCEED）：触发一次失败的触发器，然后继续正常调度
 * - 不做任何处理（DO_NOTHING）：不触发失败的触发器，等待下一次调度
 * <p>
 * 当定时任务配置了不支持或不存在的失败策略时，会抛出此异常
 */
@Getter
public class InvalidMisfirePolicyException extends SystemException {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = 1875127338541474898L;

    /**
     * 构造函数
     * 创建一个带有错误消息的无效定时任务失败策略异常
     *
     * @param message 错误消息
     */
    public InvalidMisfirePolicyException(String message) {
        super(message);
    }

}
