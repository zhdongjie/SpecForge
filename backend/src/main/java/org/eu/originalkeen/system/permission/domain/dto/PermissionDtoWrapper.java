package org.eu.originalkeen.system.permission.domain.dto;

import java.util.List;

/**
 * 权限DTO包装器接口
 * 定义权限数据传输对象的通用方法，用于创建和更新权限DTO的统一处理
 */
public interface PermissionDtoWrapper {

    /**
     * 获取父级ID
     * 返回父级权限的ID
     *
     * @return 父级ID
     */
    Long getParentId();

    /**
     * 获取权限名称
     * 返回权限的显示名称
     *
     * @return 权限名称
     */
    List<PermissionTranslationDto> getTranslations();

    /**
     * 获取权限标识
     * 返回权限的唯一标识字符串
     *
     * @return 权限标识
     */
    String getAuthority();

    /**
     * 获取排序值
     * 返回权限的排序值
     *
     * @return 排序值
     */
    Integer getSort();

    /**
     * 获取权限类型
     * 返回权限的类型值
     *
     * @return 权限类型
     */
    String getPermissionType();

    /**
     * 获取图标
     * 返回权限的图标
     *
     * @return 图标
     */
    String getIcon();

    /**
     * 获取可见性
     * 返回权限是否可见
     *
     * @return 可见性
     */
    Boolean getVisible();

    /**
     * 获取权限状态
     * 返回权限的状态
     *
     * @return 权限状态
     */
    String getPermissionStatus();

    /**
     * 获取链接地址
     * 返回链接类型权限的地址
     *
     * @return 链接地址
     */
    String getLinkAddress();

    /**
     * 获取链接目标
     * 返回链接类型权限的目标窗口
     *
     * @return 链接目标
     */
    String getLinkTarget();

    /**
     * 获取路由路径
     * 返回模板类型权限的路由路径
     *
     * @return 路由路径
     */
    String getRouterPath();

    /**
     * 获取组件路径
     * 返回模板类型权限的组件路径
     *
     * @return 组件路径
     */
    String getComponentPath();

    /**
     * 获取是否缓存
     * 返回模板类型权限是否缓存
     *
     * @return 是否缓存
     */
    Boolean getKeepAlive();

}
