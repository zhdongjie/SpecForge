package org.eu.originalkeen.core.domain;

import java.util.Date;

/**
 * 审计接口
 * 用于定义需要进行审计跟踪的实体类的必要方法
 */
public interface Audit {

    /**
     * 获取创建时间
     * 返回实体的创建时间
     *
     * @return 创建时间
     */
    Date getCreatedTime();

    /**
     * 获取创建人
     * 返回创建实体的用户ID
     *
     * @return 创建人的用户ID
     */
    Long getCreatedBy();

    /**
     * 获取最后修改时间
     * 返回实体的最后修改时间
     *
     * @return 最后修改时间
     */
    Date getLastModifiedTime();

    /**
     * 获取最后修改人
     * 返回最后修改实体的用户ID
     *
     * @return 最后修改人的用户ID
     */
    Long getLastModifiedBy();

    /**
     * 设置创建时间
     * 设置实体的创建时间
     *
     * @param createdTime 创建时间
     */
    void setCreatedTime(Date createdTime);

    /**
     * 设置创建人
     * 设置创建实体的用户ID
     *
     * @param createdBy 创建人的用户ID
     */
    void setCreatedBy(Long createdBy);

    /**
     * 设置最后修改时间
     * 设置实体的最后修改时间
     *
     * @param lastModifiedTime 最后修改时间
     */
    void setLastModifiedTime(Date lastModifiedTime);

    /**
     * 设置最后修改人
     * 设置最后修改实体的用户ID
     *
     * @param lastModifiedBy 最后修改人的用户ID
     */
    void setLastModifiedBy(Long lastModifiedBy);

}
