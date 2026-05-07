package org.eu.originalkeen.system.permission.domain.vo;

import com.mybatisflex.annotation.RelationOneToMany;
import com.mybatisflex.annotation.RelationOneToOne;
import org.eu.originalkeen.core.domain.Tree;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;
import java.util.Date;
import java.util.List;

/**
 * 权限节点视图对象
 * 用于返回树形结构的权限数据，实现Tree接口以支持树形结构
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class PermissionNodeVo implements Serializable, Tree<Long, PermissionNodeVo> {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -4345545804016752079L;

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
    @RelationOneToOne(
            selfField = "id",
            targetTable = "system_permission_translation",
            targetField = "permissionId",
            valueField = "permissionName",
            extraCondition = "`language_code` = :languageCode"
    )
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

    /**
     * 权限状态
     * 权限的状态，对应 system_permission_status 字典数据
     */
    private String permissionStatus;

    /**
     * 创建时间
     * 权限的创建时间
     */
    private Date createdTime;

    /**
     * 子节点列表
     * 当前权限节点的子权限节点列表，用于构建树形结构
     */
    @RelationOneToMany(
            selfField = "id",
            targetField = "parentId",
            targetTable = "system_permission",
            orderBy = "sort ASC",
            selectColumns = "id, authority, sort, permission_type, icon, link_address, link_target, router_path, component_path, keep_alive, visible, permission_status, created_time"
    )
    private List<PermissionNodeVo> children;

}
