package org.eu.originalkeen.system.role.service;

import com.mybatisflex.core.service.IService;
import org.eu.originalkeen.system.role.domain.entity.UserRoleEntity;

import java.util.List;
import java.util.Set;

/**
 * 用户角色服务接口
 * 提供用户角色管理相关的业务逻辑方法
 */
public interface UserRoleService extends IService<UserRoleEntity> {

    /**
     * 创建用户与角色的关联关系
     * 为指定用户创建与角色列表的关联关系
     *
     * @param userId           用户ID
     * @param effectiveRoleIds 要关联的角色ID列表
     */
    void createUserRoleRelation(Long userId, Set<Long> effectiveRoleIds);

    /**
     * 删除用户与角色的关联关系
     * 删除指定用户与指定角色的关联关系
     *
     * @param userId  用户ID
     * @param roleIds 要删除关联的角色ID列表
     */
    void deleteUserRoleRelation(Long userId, Set<Long> roleIds);

    /**
     * 删除用户与角色的关联关系
     * 删除指定用户列表的所有角色关联
     *
     * @param userIds 要删除角色关联的用户ID列表
     */
    void deleteUserRoleRelation(Set<Long> userIds);

    /**
     * 获取用户的角色ID列表
     * 根据用户ID获取其所有角色的ID列表
     *
     * @param userId 用户ID
     * @return 角色ID列表
     */
    Set<Long> selectRoleIdsByUserId(Long userId);

    /**
     * 获取已使用的角色ID列表
     * 从指定的角色ID列表中筛选出已被用户使用的角色ID
     *
     * @param roleIds 角色ID列表
     * @return 已使用的角色ID列表
     */
    Set<Long> selectUsedRoleIds(Set<Long> roleIds);

    /**
     * 批量创建用户与角色的关联关系
     * 为多个用户创建与角色列表的关联关系
     *
     * @param userIds          用户ID列表
     * @param effectiveRoleIds 要关联的角色ID列表
     */
    void createUserRoleRelation(List<Long> userIds, Set<Long> effectiveRoleIds);

}
