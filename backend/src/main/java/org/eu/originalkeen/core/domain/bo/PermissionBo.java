package org.eu.originalkeen.core.domain.bo;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;

/**
 * 权限业务对象
 * 用于存储权限信息，包含权限ID、父级ID、名称和权限标识
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class PermissionBo implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = 2141197163170774405L;

    /**
     * 权限ID
     * 权限的唯一标识
     */
    private Long id;

    /**
     * 父级ID
     * 父级权限的ID，用于构建权限树结构
     */
    private Long parentId;

    /**
     * 权限名称
     * 权限的显示名称
     */
    private String permissionName;

    /**
     * 权限标识
     * 权限的唯一标识字符串，用于授权校验
     */
    private String authority;

    /**
     * 排序值
     * 权限在同级中的排序顺序，值越小越靠前
     */
    private Integer sort;

    /**
     * 权限类型
     * 权限的类型，对应 system_permission_type 字典数据
     */
    private String permissionType;

    /**
     * 图标
     * 权限菜单的图标类名
     */
    private String icon;

    /**
     * 链接地址
     * 外部链接类型权限的URL地址
     */
    private String linkAddress;

    /**
     * 链接目标
     * 外部链接的打开方式，对应 system_permission_link_target 字典数据
     */
    private String linkTarget;

    /**
     * 路由路径
     * 前端路由的路径，用于前端路由匹配
     */
    private String routerPath;

    /**
     * 组件路径
     * 前端组件的路径，用于动态加载组件
     */
    private String componentPath;

    /**
     * 是否缓存
     * 前端路由是否保持组件状态不销毁
     */
    private Boolean keepAlive;

    /**
     * 是否可见
     * 权限是否在菜单中可见
     */
    private Boolean visible;

}
