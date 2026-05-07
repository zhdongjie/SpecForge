package org.eu.originalkeen.core.domain.bo;

import org.eu.originalkeen.core.constant.SystemConstant;
import org.eu.originalkeen.system.role.domain.bo.RoleBo;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.security.core.GrantedAuthority;

import java.io.Serial;
import java.io.Serializable;

/**
 * 权限标识业务对象
 * 实现Spring Security的GrantedAuthority接口，用于存储权限标识
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class AuthorityBo implements GrantedAuthority, Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = 7623874335240331965L;

    /**
     * 权限标识
     * 权限的唯一标识字符串，用于授权校验
     */
    private String authority;

    /**
     * 从角色权限字符串创建AuthorityBo实例
     * 工厂方法，用于创建权限标识对象
     *
     * @param roleAuthority 角色权限字符串
     * @return AuthorityBo实例
     */
    public static AuthorityBo of(String roleAuthority) {
        return new AuthorityBo(roleAuthority);
    }

    /**
     * 从权限业务对象创建AuthorityBo实例
     * 工厂方法，用于从权限对象创建权限标识对象
     *
     * @param permissionBo 权限业务对象
     * @return AuthorityBo实例
     */
    public static AuthorityBo of(PermissionBo permissionBo) {
        return new AuthorityBo(permissionBo.getAuthority());
    }

    /**
     * 从角色业务对象创建AuthorityBo实例
     * 工厂方法，用于从角色对象创建权限标识对象
     *
     * @param roleBo 角色业务对象
     * @return AuthorityBo实例
     */
    public static AuthorityBo of(RoleBo roleBo) {
        return new AuthorityBo(SystemConstant.ROLE_AUTHORITY_PREFIX + roleBo.getRoleCode().toUpperCase());
    }

}
