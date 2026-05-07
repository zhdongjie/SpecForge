package org.eu.originalkeen.system.permission.service;

import com.mybatisflex.core.service.IService;
import org.eu.originalkeen.system.permission.domain.entity.RolePermissionEntity;

import java.util.Set;

/**
 * 角色权限服务接口
 * 提供角色权限管理相关的业务逻辑方法
 */
public interface RolePermissionService extends IService<RolePermissionEntity> {

    /**
     * 创建角色权限关系
     * 为指定角色创建与权限的关联关系
     *
     * @param roleId                 角色ID
     * @param effectivePermissionIds 权限ID列表
     */
    void createRolePermissionRelation(Long roleId, Set<Long> effectivePermissionIds);

    /**
     * 删除角色权限关系
     * 删除指定角色与指定权限的关联关系
     *
     * @param roleId         角色ID
     * @param deletedRoleIds 要删除的权限ID列表
     */
    void deleteRolePermissionRelation(Long roleId, Set<Long> deletedRoleIds);

    /**
     * 删除角色权限关系
     * 删除指定角色的所有权限关联关系
     *
     * @param roleIds 角色ID列表
     */
    void deleteRolePermissionRelation(Set<Long> roleIds);

    /**
     * 获取角色的权限ID列表
     * 根据角色ID获取其所有权限的ID列表
     *
     * @param roleId 角色ID
     * @return 权限ID列表
     */
    Set<Long> selectPermissionIdsByRoleId(Long roleId);

    /**
     * 获取已使用的权限ID列表
     * 从指定的权限ID列表中筛选出已被使用的权限ID
     *
     * @param permissionIds 权限ID列表
     * @return 已使用的权限ID列表
     */
    Set<Long> selectUsedPermissionIds(Set<Long> permissionIds);

}
