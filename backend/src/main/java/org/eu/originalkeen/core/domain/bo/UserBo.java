package org.eu.originalkeen.core.domain.bo;

import com.mybatisflex.annotation.ColumnMask;
import org.eu.originalkeen.system.role.domain.bo.RoleBo;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.apache.commons.collections4.CollectionUtils;
import org.apache.commons.collections4.MapUtils;
import org.springframework.security.core.userdetails.UserDetails;

import java.io.Serial;
import java.io.Serializable;
import java.util.*;
import java.util.stream.Collectors;

/**
 * 用户业务对象
 * 实现Spring Security的UserDetails接口，用于存储用户信息和权限
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class UserBo implements UserDetails, Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -2807564315647655263L;

    /**
     * 用户ID
     * 用户的唯一标识
     */
    private Long id;

    /**
     * 用户名
     * 用户的登录账号
     */
    private String username;

    /**
     * 性别
     * 用户的性别，对应 system_user_gender 字典数据
     */
    private String gender;

    /**
     * 出生日期
     * 用户的出生日期
     */
    private Date birthday;

    /**
     * 电子邮箱
     * 用户的电子邮箱地址
     */
    private String email;

    /**
     * 手机号码
     * 用户的手机联系方式
     */
    private String phoneNumber;

    /**
     * 头像
     * 用户头像图片的URL地址
     */
    @ColumnMask("FILE_ACCESS_DOMAIN")
    private String avatar;

    /**
     * 加密密码
     * 用户的登录密码，已经过加密处理
     */
    private String encodedPassword;

    /**
     * 是否启用
     * 用户账号是否启用，默认为启用
     */
    private boolean enabled = true;

    /**
     * 账号是否未过期
     * 用户账号是否未过期，默认为未过期
     */
    private boolean accountNonExpired = true;

    /**
     * 账号是否未锁定
     * 用户账号是否未锁定，默认为未锁定
     */
    private boolean accountNonLocked = true;

    /**
     * 凭证是否未过期
     * 用户凭证（密码）是否未过期，默认为未过期
     */
    private boolean credentialsNonExpired = true;

    /**
     * 角色列表
     * 用户拥有的角色列表
     */
    private List<RoleBo> roles;

    /**
     * 权限列表
     * 用户拥有的权限对象列表
     */
    private List<PermissionBo> permissions;

    /**
     * 权限标识列表
     * 用户拥有的权限标识对象列表，用于Spring Security的授权
     */
    private List<AuthorityBo> authorities;

    /**
     * 创建时间
     * 用户账号的创建时间
     */
    private Date createdTime;

    /**
     * 多语言角色名称缓存
     * key: 语言代码 (zh-CN, en-US等)
     * value: 角色代码到名称的映射
     */
    private Map<String, Map<String, String>> langRoleNames = new HashMap<>();

    /**
     * 多语言权限名称缓存
     * key: 语言代码 (zh-CN, en-US等)
     * value: 权限标识到名称的映射
     */
    private Map<String, Map<String, String>> langPermissionNames = new HashMap<>();

    /**
     * 已加载的语言代码列表
     */
    private Set<String> loadedLangCodes = new HashSet<>();

    /**
     * 添加一种语言的角色和权限名称
     *
     * @param langCode    语言代码
     * @param roles       角色列表
     * @param permissions 权限列表
     */
    public void addLangData(String langCode, List<RoleBo> roles, List<PermissionBo> permissions) {
        // 缓存角色名称
        Map<String, String> roleNameMap = new HashMap<>();
        if (CollectionUtils.isNotEmpty(roles)) {
            roleNameMap = roles.stream()
                    .collect(Collectors.toMap(RoleBo::getRoleCode, RoleBo::getRoleName));
        }
        langRoleNames.put(langCode, roleNameMap);

        // 缓存权限名称
        Map<String, String> permNameMap = new HashMap<>();
        if (CollectionUtils.isNotEmpty(permissions)) {
            permNameMap = permissions.stream()
                    .collect(Collectors.toMap(PermissionBo::getAuthority, PermissionBo::getPermissionName, (v1, v2) -> v1));
        }
        langPermissionNames.put(langCode, permNameMap);

        // 标记语言已加载
        loadedLangCodes.add(langCode);
    }

    /**
     * 判断是否需要加载指定语言
     * 校验用户对象是否已加载指定语言的角色和权限名称
     *
     * @param langCode 语言代码，例如 zh-CN、en-US
     * @return 如果需要加载返回true，否则返回false
     */
    public boolean needLoadLang(String langCode) {
        return !loadedLangCodes.contains(langCode);
    }

    /**
     * 切换到指定语言
     * 更新当前角色和权限列表中的名称为指定语言
     *
     * @param langCode 语言代码
     */
    public void switchToLang(String langCode) {
        // 如果需要加载该语言数据但尚未加载，则无法切换
        if (needLoadLang(langCode)) {
            return;
        }

        // 更新角色名称
        Map<String, String> roleNameMap = langRoleNames.get(langCode);
        if (CollectionUtils.isNotEmpty(roles) && MapUtils.isNotEmpty(roleNameMap)) {
            for (RoleBo role : roles) {
                role.setRoleName(roleNameMap.get(role.getRoleCode()));
            }
        }

        // 更新权限名称
        Map<String, String> permNameMap = langPermissionNames.get(langCode);
        if (CollectionUtils.isNotEmpty(permissions) && MapUtils.isNotEmpty(permNameMap)) {
            for (PermissionBo perm : permissions) {
                perm.setPermissionName(permNameMap.get(perm.getAuthority()));
            }
        }

    }

    /**
     * 添加权限标识
     * 将指定的权限标识列表添加到用户的权限列表中
     *
     * @param authorities 要添加的权限标识列表
     */
    public void addAuthorities(List<AuthorityBo> authorities) {
        if (CollectionUtils.isEmpty(authorities)) {
            authorities = Collections.emptyList();
        }
        this.authorities.addAll(authorities);
    }

    /**
     * 获取密码
     * 实现UserDetails接口的方法，返回用户的加密密码
     *
     * @return 用户的加密密码
     */
    @Override
    public String getPassword() {
        return this.encodedPassword;
    }

}
