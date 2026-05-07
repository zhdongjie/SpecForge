package org.eu.originalkeen.system.permission.domain.entity;

import com.mybatisflex.annotation.Id;
import com.mybatisflex.annotation.Table;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;

/**
 * 角色权限关系实体类
 * 对应数据库中system_role_permission表，存储角色和权限的关联关系
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Table("system_role_permission")
public class RolePermissionEntity implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -8903636554552110483L;

    /**
     * 角色ID
     * 角色的唯一标识，为联合主键的一部分
     */
    @Id
    private Long roleId;

    /**
     * 权限ID
     * 权限的唯一标识，为联合主键的一部分
     */
    @Id
    private Long permissionId;

    /**
     * 创建RolePermissionEntity实例
     * 工厂方法，用于创建角色权限关系实体
     *
     * @param roleId       角色ID
     * @param permissionId 权限ID
     * @return RolePermissionEntity实例
     */
    public static RolePermissionEntity of(Long roleId, Long permissionId) {
        return new RolePermissionEntity(roleId, permissionId);
    }

}
