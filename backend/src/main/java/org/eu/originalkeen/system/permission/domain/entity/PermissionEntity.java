package org.eu.originalkeen.system.permission.domain.entity;

import com.mybatisflex.annotation.Table;
import org.eu.originalkeen.core.constant.SystemConstant;
import org.eu.originalkeen.core.domain.Audit;
import org.eu.originalkeen.core.domain.entity.PrimaryKeyEntity;
import org.eu.originalkeen.system.permission.domain.dto.PermissionDtoWrapper;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;
import org.apache.commons.lang3.StringUtils;

import java.io.Serial;
import java.io.Serializable;
import java.util.Date;

/**
 * 权限实体类
 * 对应数据库中system_permission表，存储权限信息
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Table("system_permission")
@EqualsAndHashCode(callSuper = true)
public class PermissionEntity extends PrimaryKeyEntity implements Serializable, Audit {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -2921829200605363195L;

    /**
     * 父级ID
     * 父级权限的ID，用于构建权限树结构
     */
    private Long parentId;

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
     * 记录创建的时间
     */
    private Date createdTime;

    /**
     * 创建人
     * 记录创建人的用户ID
     */
    private Long createdBy;

    /**
     * 最后修改时间
     * 记录最后一次修改的时间
     */
    private Date lastModifiedTime;

    /**
     * 最后修改人
     * 记录最后一次修改人的用户ID
     */
    private Long lastModifiedBy;

    /**
     * 从权限DTO包装器创建权限实体
     * 根据权限类型创建不同类型的权限实体
     *
     * @param permissionDtoWrapper 权限DTO包装器
     * @return 权限实体对象
     */
    public static PermissionEntity of(PermissionDtoWrapper permissionDtoWrapper) {
        if (StringUtils.equals(SystemConstant.PERMISSION_TYPE_SUBHEADER, permissionDtoWrapper.getPermissionType())) {
            return ofSubheader(permissionDtoWrapper);
        }
        if (StringUtils.equals(SystemConstant.PERMISSION_TYPE_GROUP, permissionDtoWrapper.getPermissionType())) {
            return ofGroup(permissionDtoWrapper);
        }
        if (StringUtils.equals(SystemConstant.PERMISSION_TYPE_TEMPLATE, permissionDtoWrapper.getPermissionType())) {
            return ofTemplate(permissionDtoWrapper);
        }
        if (StringUtils.equals(SystemConstant.PERMISSION_TYPE_LINK, permissionDtoWrapper.getPermissionType())) {
            return ofLink(permissionDtoWrapper);
        }
        if (StringUtils.equals(SystemConstant.PERMISSION_TYPE_BUTTON, permissionDtoWrapper.getPermissionType())) {
            return ofButton(permissionDtoWrapper);
        }
        if (StringUtils.equals(SystemConstant.PERMISSION_TYPE_FUNCTION, permissionDtoWrapper.getPermissionType())) {
            return ofFunction(permissionDtoWrapper);
        }
        return null;
    }

    /**
     * 创建子标题类型权限实体
     * 从权限DTO包装器创建子标题类型的权限实体
     *
     * @param permissionDtoWrapper 权限DTO包装器
     * @return 组类型权限实体
     */
    private static PermissionEntity ofSubheader(PermissionDtoWrapper permissionDtoWrapper) {
        return new PermissionEntity(
                permissionDtoWrapper.getParentId(),
                permissionDtoWrapper.getAuthority(),
                permissionDtoWrapper.getSort(),
                permissionDtoWrapper.getPermissionType(),
                permissionDtoWrapper.getIcon(),
                null,
                null,
                null,
                null,
                null,
                permissionDtoWrapper.getVisible(),
                permissionDtoWrapper.getPermissionStatus(),
                null,
                null,
                null,
                null
        );
    }

    /**
     * 创建组类型权限实体
     * 从权限DTO包装器创建组类型的权限实体
     *
     * @param permissionDtoWrapper 权限DTO包装器
     * @return 组类型权限实体
     */
    private static PermissionEntity ofGroup(PermissionDtoWrapper permissionDtoWrapper) {
        return new PermissionEntity(
                permissionDtoWrapper.getParentId(),
                permissionDtoWrapper.getAuthority(),
                permissionDtoWrapper.getSort(),
                permissionDtoWrapper.getPermissionType(),
                permissionDtoWrapper.getIcon(),
                null,
                null,
                null,
                null,
                null,
                permissionDtoWrapper.getVisible(),
                permissionDtoWrapper.getPermissionStatus(),
                null,
                null,
                null,
                null
        );
    }

    /**
     * 创建模板类型权限实体
     * 从权限DTO包装器创建模板类型的权限实体
     *
     * @param permissionDtoWrapper 权限DTO包装器
     * @return 模板类型权限实体
     */
    private static PermissionEntity ofTemplate(PermissionDtoWrapper permissionDtoWrapper) {
        return new PermissionEntity(
                permissionDtoWrapper.getParentId(),
                permissionDtoWrapper.getAuthority(),
                permissionDtoWrapper.getSort(),
                permissionDtoWrapper.getPermissionType(),
                permissionDtoWrapper.getIcon(),
                null,
                null,
                permissionDtoWrapper.getRouterPath(),
                permissionDtoWrapper.getComponentPath(),
                permissionDtoWrapper.getKeepAlive(),
                permissionDtoWrapper.getVisible(),
                permissionDtoWrapper.getPermissionStatus(),
                null,
                null,
                null,
                null
        );
    }

    /**
     * 创建链接类型权限实体
     * 从权限DTO包装器创建链接类型的权限实体
     *
     * @param permissionDtoWrapper 权限DTO包装器
     * @return 链接类型权限实体
     */
    private static PermissionEntity ofLink(PermissionDtoWrapper permissionDtoWrapper) {
        return new PermissionEntity(
                permissionDtoWrapper.getParentId(),
                permissionDtoWrapper.getAuthority(),
                permissionDtoWrapper.getSort(),
                permissionDtoWrapper.getPermissionType(),
                permissionDtoWrapper.getIcon(),
                permissionDtoWrapper.getLinkAddress(),
                permissionDtoWrapper.getLinkTarget(),
                null,
                null,
                null,
                permissionDtoWrapper.getVisible(),
                permissionDtoWrapper.getPermissionStatus(),
                null,
                null,
                null,
                null
        );
    }

    /**
     * 创建按钮类型权限实体
     * 从权限DTO包装器创建按钮类型的权限实体
     *
     * @param permissionDtoWrapper 权限DTO包装器
     * @return 按钮类型权限实体
     */
    private static PermissionEntity ofButton(PermissionDtoWrapper permissionDtoWrapper) {
        return new PermissionEntity(
                permissionDtoWrapper.getParentId(),
                permissionDtoWrapper.getAuthority(),
                permissionDtoWrapper.getSort(),
                permissionDtoWrapper.getPermissionType(),
                permissionDtoWrapper.getIcon(),
                null,
                null,
                null,
                null,
                null,
                permissionDtoWrapper.getVisible(),
                permissionDtoWrapper.getPermissionStatus(),
                null,
                null,
                null,
                null
        );
    }

    /**
     * 创建功能类型权限实体
     * 从权限DTO包装器创建功能类型的权限实体
     *
     * @param permissionDtoWrapper 权限DTO包装器
     * @return 功能类型权限实体
     */
    private static PermissionEntity ofFunction(PermissionDtoWrapper permissionDtoWrapper) {
        return new PermissionEntity(
                permissionDtoWrapper.getParentId(),
                permissionDtoWrapper.getAuthority(),
                permissionDtoWrapper.getSort(),
                permissionDtoWrapper.getPermissionType(),
                null,
                null,
                null,
                null,
                null,
                null,
                false,
                permissionDtoWrapper.getPermissionStatus(),
                null,
                null,
                null,
                null
        );
    }

}
