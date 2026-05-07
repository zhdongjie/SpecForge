package org.eu.originalkeen.system.permission.service.impl;

import com.mybatisflex.spring.service.impl.ServiceImpl;
import org.eu.originalkeen.system.permission.domain.entity.RolePermissionEntity;
import org.eu.originalkeen.system.permission.mapper.RolePermissionMapper;
import org.eu.originalkeen.system.permission.service.RolePermissionService;
import org.springframework.stereotype.Service;

import java.util.HashSet;
import java.util.List;
import java.util.Set;

import static com.mybatisflex.core.query.QueryMethods.distinct;
import static org.eu.originalkeen.system.permission.domain.entity.table.RolePermissionTableDef.role_permission;

/**
 * 角色权限服务实现类
 * 实现角色权限管理相关的业务逻辑
 * <p>
 * 主要功能：
 * 1. 创建和删除角色与权限的关联关系
 * 2. 查询角色拥有的权限
 * 3. 校验权限的使用情况
 * <p>
 * 继承自ServiceImpl，自动注入RolePermissionMapper用于数据库操作
 */
@Service
public class RolePermissionServiceImpl extends ServiceImpl<RolePermissionMapper, RolePermissionEntity>
        implements RolePermissionService {

    /**
     * 创建角色权限关系实现
     * 为指定角色创建与权限的关联关系
     *
     * @param roleId        角色ID
     * @param permissionIds 权限ID列表
     */
    @Override
    public void createRolePermissionRelation(Long roleId, Set<Long> permissionIds) {
        List<RolePermissionEntity> rolePermissionRelation = getRolePermissionRelation(roleId, permissionIds);

        saveBatch(rolePermissionRelation);
    }

    /**
     * 删除角色权限关系实现
     * 删除指定角色与指定权限的关联关系
     *
     * @param roleId        角色ID
     * @param permissionIds 要删除的权限ID列表
     */
    @Override
    public void deleteRolePermissionRelation(Long roleId, Set<Long> permissionIds) {
        remove(role_permission.role_id.eq(roleId).and(role_permission.permission_id.in(permissionIds)));
    }

    /**
     * 删除角色权限关系实现
     * 删除指定角色的所有权限关联关系
     *
     * @param roleIds 角色ID列表
     */
    @Override
    public void deleteRolePermissionRelation(Set<Long> roleIds) {
        remove(role_permission.role_id.in(roleIds));
    }

    /**
     * 获取角色的权限ID列表实现
     * 根据角色ID获取其所有权限的ID列表
     *
     * @param roleId 角色ID
     * @return 权限ID列表
     */
    @Override
    public Set<Long> selectPermissionIdsByRoleId(Long roleId) {
        return new HashSet<>(queryChain()
                .select(role_permission.permission_id)
                .from(role_permission)
                .where(role_permission.role_id.eq(roleId))
                .listAs(Long.class)
        );
    }

    /**
     * 获取已使用的权限ID列表实现
     * 从指定的权限ID列表中筛选出已被使用的权限ID
     *
     * @param permissionIds 权限ID列表
     * @return 已使用的权限ID列表
     */
    @Override
    public Set<Long> selectUsedPermissionIds(Set<Long> permissionIds) {
        return new HashSet<>(queryChain()
                .select(distinct(role_permission.permission_id))
                .from(role_permission)
                .where(role_permission.permission_id.in(permissionIds))
                .listAs(Long.class)
        );
    }

    /**
     * 获取角色权限关系实体列表
     * 根据角色ID和权限ID列表创建角色权限关系实体列表
     *
     * @param roleId        角色ID
     * @param permissionIds 权限ID列表
     * @return 角色权限关系实体列表
     */
    private List<RolePermissionEntity> getRolePermissionRelation(Long roleId, Set<Long> permissionIds) {
        return permissionIds.stream()
                .map(permissionId -> RolePermissionEntity.of(roleId, permissionId))
                .toList();
    }

}
