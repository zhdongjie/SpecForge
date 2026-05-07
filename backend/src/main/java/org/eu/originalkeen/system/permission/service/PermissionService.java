package org.eu.originalkeen.system.permission.service;

import com.mybatisflex.core.service.IService;
import org.eu.originalkeen.core.domain.bo.PermissionBo;
import org.eu.originalkeen.system.permission.domain.bo.PermissionNodeBo;
import org.eu.originalkeen.system.permission.domain.bo.ValidateAuthorityUniqueBo;
import org.eu.originalkeen.system.permission.domain.entity.PermissionEntity;
import org.eu.originalkeen.system.permission.domain.vo.PermissionDetailsVo;
import org.eu.originalkeen.system.permission.domain.vo.PermissionNodeVo;

import java.util.List;
import java.util.Set;

/**
 * 权限服务接口
 * 提供权限管理相关的业务逻辑方法
 */
public interface PermissionService extends IService<PermissionEntity> {

    /**
     * 查询权限详情
     * 根据ID查询权限详细信息
     *
     * @param id 权限ID
     * @return 权限详情响应对象
     */
    PermissionDetailsVo enquiryDetails(Long id);

    /**
     * 查询权限树
     * 查询权限的树形结构
     *
     * @return 权限树响应对象
     */
    List<PermissionNodeVo> enquiryTree();

    /**
     * 查询用户权限
     * 根据用户ID查询用户所拥有的所有权限
     *
     * @param userId 用户ID
     * @return 用户权限列表
     */
    List<PermissionBo> selectUserPermissions(Long userId);

    /**
     * 查询用户权限的多语言信息
     * 根据用户ID查询用户权限的标识和名称，仅用于多语言切换
     *
     * @param userId 用户ID
     * @return 用户权限的多语言信息列表
     */
    List<PermissionBo> selectUserPermissionsForLanguage(Long userId);

    /**
     * 查询有效的权限ID列表
     * 从权限ID列表中过滤出实际存在的权限ID
     *
     * @param permissionIds 权限ID列表
     * @return 有效的权限ID列表
     */
    Set<Long> selectEffectivePermissionIds(Set<Long> permissionIds);

    /**
     * 查询权限是否存在
     * 根据权限ID查询权限是否存在
     *
     * @param permissionId 权限ID
     * @return 存在返回true，不存在返回false
     */
    boolean selectPermissionExists(Long permissionId);

    /**
     * 查询权限标识是否存在
     * 根据权限标识查询是否已存在
     *
     * @param validateAuthorityUniqueBo 权限标识唯一性校验业务对象
     * @return 存在返回true，不存在返回false
     */
    boolean selectAuthorityExists(ValidateAuthorityUniqueBo validateAuthorityUniqueBo);

    /**
     * 查询权限节点
     * 根据权限ID查询权限节点及其子节点
     *
     * @param permissionId 权限ID
     * @return 权限节点业务对象
     */
    PermissionNodeBo selectPermissionNodes(Long permissionId);

}
