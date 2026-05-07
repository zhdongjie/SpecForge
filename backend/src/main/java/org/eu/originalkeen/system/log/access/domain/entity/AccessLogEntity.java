package org.eu.originalkeen.system.log.access.domain.entity;

import com.mybatisflex.annotation.Table;
import org.eu.originalkeen.core.domain.entity.PrimaryKeyEntity;
import org.eu.originalkeen.core.enums.AccessStatus;
import org.eu.originalkeen.core.enums.AccessType;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;
import java.util.Date;

/**
 * 访问日志实体类
 * 对应数据库中system_access_log表，用于记录用户的访问日志
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Table("system_access_log")
@EqualsAndHashCode(callSuper = true)
public class AccessLogEntity extends PrimaryKeyEntity implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = 8350259755493491210L;

    /**
     * 用户名
     * 访问用户的登录账号
     */
    private String username;

    /**
     * 访问IP
     * 用户访问的IP地址
     */
    private String accessIp;

    /**
     * 访问位置
     * 用户访问的地理位置
     */
    private String accessLocation;

    /**
     * 浏览器
     * 用户使用的浏览器类型
     */
    private String browser;

    /**
     * 操作系统
     * 用户使用的操作系统
     */
    private String operatingSystem;

    /**
     * 访问状态
     * 访问的状态码，对应 {@link AccessStatus} 枚举
     */
    private String accessStatus;

    /**
     * 访问类型
     * 访问的类型，对应 {@link AccessType} 枚举
     */
    private String accessType;

    /**
     * 提示消息
     * 访问过程中的提示消息
     */
    private String promptMessage;

    /**
     * 访问时间
     * 用户访问的时间
     */
    private Date accessTime;

}
