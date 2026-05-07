package org.eu.originalkeen.system.log.operate.domain.entity;

import com.mybatisflex.annotation.Table;
import org.eu.originalkeen.core.domain.entity.PrimaryKeyEntity;
import org.eu.originalkeen.core.enums.OperateStatus;
import org.eu.originalkeen.core.enums.OperateType;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;
import java.util.Date;

/**
 * 操作日志实体类
 * 对应数据库中system_operate_log表，用于记录用户的操作日志
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Table("system_operate_log")
@EqualsAndHashCode(callSuper = true)
public class OperateLogEntity extends PrimaryKeyEntity implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -2812272872141054681L;

    /**
     * 操作标题
     * 操作的标题或名称
     */
    private String title;

    /**
     * 操作类型
     * 操作的操作类型，对应 {@link OperateType} 枚举值
     */
    private String operateType;

    /**
     * 执行方法
     * 执行的方法名称，包含类名和方法名
     */
    private String executeMethod;

    /**
     * 请求方法
     * HTTP请求方法，如GET、POST等
     */
    private String requestMethod;

    /**
     * 请求URL
     * 请求的URL地址
     */
    private String requestUrl;

    /**
     * 操作IP
     * 用户操作的IP地址
     */
    private String operateIp;

    /**
     * 操作位置
     * 用户操作的地理位置
     */
    private String operateLocation;

    /**
     * 请求参数
     * 请求的参数信息，通常为JSON格式
     */
    private String requestParam;

    /**
     * 响应结果
     * 请求的响应结果，通常为JSON格式
     */
    private String responseResult;

    /**
     * 错误消息
     * 操作过程中的错误消息，如果有的话
     */
    private String errorMessage;

    /**
     * 响应时间
     * 请求的响应时间，单位为毫秒
     */
    private Long responseDuration;

    /**
     * 操作状态
     * 操作的状态码，对应 {@link OperateStatus} 枚举值
     */
    private String operateStatus;

    /**
     * 操作人
     * 执行操作的用户ID
     */
    private Long operateBy;

    /**
     * 操作时间
     * 执行操作的时间
     */
    private Date operateTime;

}
