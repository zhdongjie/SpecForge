package org.eu.originalkeen.system.permission.domain.dto;

import org.eu.originalkeen.core.constant.RegexpConstant;
import org.eu.originalkeen.system.permission.domain.dto.provide.*;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.validator.constraints.Length;
import org.hibernate.validator.constraints.Range;
import org.hibernate.validator.group.GroupSequenceProvider;

import java.io.Serial;
import java.io.Serializable;
import java.util.List;

/**
 * 创建权限数据传输对象
 * 用于接收和校验创建权限的请求数据，支持不同类型的权限校验
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@GroupSequenceProvider(PermissionGroupSequenceProvider.CreatePermission.class)
public class CreatePermissionDto implements Serializable, PermissionDtoWrapper {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = 2733039862523507086L;

    /**
     * 父级ID
     * 父级权限的ID，用于构建权限树结构
     */
    @NotNull(message = "{form.permission.parentNodeIsRequired}")
    private Long parentId;

    /**
     * 权限翻译列表
     * 权限在不同语言下的翻译列表
     */
    @Valid
    @NotEmpty(message = "{form.permission.permissionTranslationsIsRequired}")
    private List<PermissionTranslationDto> translations;

    /**
     * 权限标识
     * 权限的唯一标识字符串，用于授权校验
     */
    @NotBlank(message = "{form.permission.authorityIsRequired}")
    @Length(max = 128, message = "{form.permission.invalidAuthorityLength}")
    private String authority;

    /**
     * 排序值
     * 权限在同级中的排序顺序，值越小越靠前，范围在1-99之间
     */
    @NotNull(message = "{form.common.sortIsRequired}")
    @Range(min = 1, max = 99, message = "{form.common.invalidSortSize}")
    private Integer sort;

    /**
     * 权限类型
     * 权限的类型，对应 system_permission_type 字典数据
     */
    @NotBlank(message = "{form.permission.permissionTypeIsRequired}")
    private String permissionType;

    /**
     * 图标
     * 权限菜单的图标类名
     */
    @Length(max = 128, message = "{form.permission.invalidIconLength}", groups = {Subheader.class, Group.class, Template.class, Link.class, Button.class})
    private String icon;

    /**
     * 链接地址
     * 外部链接类型权限的URL地址，仅在链接类型权限时校验
     */
    @NotBlank(message = "{form.permission.linkAddressIsRequired}", groups = {Link.class})
    @Length(max = 256, message = "{form.permission.invalidLinkAddressLength}", groups = {Link.class})
    @Pattern(regexp = RegexpConstant.LINK_ADDRESS_REGEX, message = "{form.permission.invalidLinkAddressFormat}", groups = {Link.class})
    private String linkAddress;

    /**
     * 链接目标
     * 外部链接的打开方式，对应 system_permission_link_target 字典数据
     */
    @NotBlank(message = "{form.permission.linkTargetIsRequired}", groups = {Link.class})
    private String linkTarget;

    /**
     * 路由路径
     * 前端路由的路径，用于前端路由匹配，仅在模板类型权限时校验
     */
    @NotBlank(message = "{form.permission.routerPathIsRequired}", groups = {Template.class})
    @Length(max = 256, message = "{form.permission.invalidRouterPathLength}", groups = {Template.class})
    @Pattern(regexp = RegexpConstant.ROUTER_PATH_REGEX, message = "{form.permission.invalidRouterPathFormat}", groups = {Template.class})
    private String routerPath;

    /**
     * 组件路径
     * 前端组件的路径，用于动态加载组件，仅在模板类型权限时校验
     */
    @NotBlank(message = "{form.permission.componentPathIsRequired}", groups = {Template.class})
    @Length(max = 256, message = "{form.permission.invalidComponentPathLength}", groups = {Template.class})
    @Pattern(regexp = RegexpConstant.COMPONENT_PATH_REGEX, message = "{form.permission.invalidComponentPathFormat}", groups = {Template.class})
    private String componentPath;

    /**
     * 是否缓存
     * 前端路由是否保持组件状态不销毁，仅在模板类型权限时校验
     */
    @NotNull(message = "{form.permission.keepAliveIsRequired}", groups = {Template.class})
    private Boolean keepAlive;

    /**
     * 是否可见
     * 权限是否在菜单中可见，默认为可见
     */
    private Boolean visible = true;

    /**
     * 权限状态
     * 权限的状态，对应 system_permission_status 字典数据
     */
    @NotBlank(message = "{form.permission.permissionStatusIsRequired}")
    private String permissionStatus;

}
