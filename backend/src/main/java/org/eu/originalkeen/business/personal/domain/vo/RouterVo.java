package org.eu.originalkeen.business.personal.domain.vo;

import org.eu.originalkeen.core.domain.bo.PermissionBo;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;

/**
 * 路由器视图对象
 * 用于封装前端路由菜单信息，包含菜单ID、父级ID、名称和资源路径
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class RouterVo implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = 5685172731025106872L;

    /**
     * 菜单ID
     * 路由菜单的唯一标识
     */
    private Long id;

    /**
     * 父级ID
     * 父级菜单的ID，用于构建菜单树结构
     */
    private Long parentId;

    /**
     * 菜单名称
     * 路由菜单的显示名称
     */
    private String name;

    /**
     * 资源路径
     * 菜单对应的前端路由路径或权限标识
     */
    private String resource;

    /**
     * 排序值
     * 权限在同级中的排序顺序，值越小越靠前
     */
    private Integer sort;

    /**
     * 权限类型
     * 权限的类型，对应 system_permission_type 字典数据
     */
    private String type;

    /**
     * 图标
     * 权限菜单的图标类名
     */
    private String icon;

    /**
     * 链接地址
     * 外部链接类型权限的URL地址
     */
    private String href;

    /**
     * 链接目标
     * 外部链接的打开方式，对应 system_permission_link_target 字典数据
     */
    private String target;

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
     * 从PermissionBo创建RouterVo实例
     * 将权限业务对象转换为路由视图对象
     *
     * @param permissionBo 权限业务对象
     * @return RouterVo实例
     */
    public static RouterVo of(PermissionBo permissionBo) {
        return new RouterVo(
                permissionBo.getId(),
                permissionBo.getParentId(),
                permissionBo.getPermissionName(),
                permissionBo.getAuthority(),
                permissionBo.getSort(),
                permissionBo.getPermissionType(),
                permissionBo.getIcon(),
                permissionBo.getLinkAddress(),
                permissionBo.getLinkTarget(),
                permissionBo.getRouterPath(),
                permissionBo.getComponentPath(),
                permissionBo.getKeepAlive(),
                permissionBo.getVisible()
        );
    }

}
