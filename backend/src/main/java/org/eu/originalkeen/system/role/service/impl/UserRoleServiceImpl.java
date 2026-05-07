package org.eu.originalkeen.system.role.service.impl;

import com.mybatisflex.spring.service.impl.ServiceImpl;
import org.eu.originalkeen.system.role.domain.entity.UserRoleEntity;
import org.eu.originalkeen.system.role.mapper.UserRoleMapper;
import org.eu.originalkeen.system.role.service.UserRoleService;
import org.springframework.stereotype.Service;

import java.util.Collection;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import static com.mybatisflex.core.query.QueryMethods.distinct;
import static org.eu.originalkeen.system.role.domain.entity.table.UserRoleTableDef.user_role;

/**
 * 用户角色服务实现类
 * 实现用户角色管理相关的业务逻辑，管理用户与角色之间的多对多关联关系
 * <p>
 * 主要功能：
 * 1. 创建和删除用户与角色的关联关系
 * 2. 查询用户的角色信息和角色的使用情况
 * 3. 批量处理用户角色关联
 * <p>
 * 继承自ServiceImpl，自动注入UserRoleMapper用于数据库操作
 */
@Service
public class UserRoleServiceImpl extends ServiceImpl<UserRoleMapper, UserRoleEntity> implements UserRoleService {

    /**
     * 创建用户与角色的关联关系
     * 为指定用户创建与角色列表的关联关系
     *
     * @param userId           用户ID
     * @param effectiveRoleIds 要关联的角色ID列表
     */
    @Override
    public void createUserRoleRelation(Long userId, Set<Long> effectiveRoleIds) {
        List<UserRoleEntity> userRoleRelation = getUserRoleRelation(userId, effectiveRoleIds);

        saveBatch(userRoleRelation);
    }

    /**
     * 删除用户角色关系实现
     * 删除指定用户与指定角色的关联关系
     *
     * @param userId  用户ID
     * @param roleIds 要删除的角色ID列表
     */
    @Override
    public void deleteUserRoleRelation(Long userId, Set<Long> roleIds) {
        remove(user_role.user_id.eq(userId).and(user_role.role_id.in(roleIds)));
    }

    /**
     * 删除用户角色关系实现
     * 删除指定用户的所有角色关联关系
     *
     * @param userIds 用户ID列表
     */
    @Override
    public void deleteUserRoleRelation(Set<Long> userIds) {
        remove(user_role.user_id.in(userIds));
    }

    /**
     * 获取已使用的角色ID列表实现
     * 从指定的角色ID列表中筛选出已被使用的角色ID
     *
     * @param roleIds 角色ID列表
     * @return 已使用的角色ID列表
     */
    @Override
    public Set<Long> selectUsedRoleIds(Set<Long> roleIds) {
        return new HashSet<>(queryChain()
                .select(distinct(user_role.role_id))
                .from(user_role)
                .where(user_role.role_id.in(roleIds))
                .listAs(Long.class)
        );
    }

    /**
     * 批量创建用户与角色的关联关系
     * 为多个用户创建与角色列表的关联关系，通过内部的getUserRoleRelation方法生成关联实体
     *
     * @param userIds 用户ID列表
     * @param roleIds 要关联的有效角色ID列表
     */
    @Override
    public void createUserRoleRelation(List<Long> userIds, Set<Long> roleIds) {
        List<UserRoleEntity> userRoleRelation = userIds.stream()
                .map(userId -> getUserRoleRelation(userId, roleIds))
                .flatMap(Collection::stream)
                .toList();

        saveBatch(userRoleRelation);
    }

    /**
     * 获取用户的角色ID列表实现
     * 根据用户ID获取其所有角色的ID列表
     *
     * @param userId 用户ID
     * @return 角色ID列表
     */
    @Override
    public Set<Long> selectRoleIdsByUserId(Long userId) {
        return new HashSet<>(queryChain()
                .select(user_role.role_id)
                .from(user_role)
                .where(user_role.user_id.eq(userId))
                .listAs(Long.class)
        );
    }

    /**
     * 获取用户角色关系实体列表
     * 根据用户ID和角色ID列表创建用户角色关系实体列表
     *
     * @param userId  用户ID
     * @param roleIds 角色ID列表
     * @return 用户角色关系实体列表
     */
    private List<UserRoleEntity> getUserRoleRelation(Long userId, Set<Long> roleIds) {
        return roleIds.stream()
                .map(roleId -> UserRoleEntity.of(userId, roleId))
                .toList();
    }

}
