package org.eu.originalkeen.system.permission.service.impl;

import com.mybatisflex.core.query.If;
import com.mybatisflex.core.relation.RelationManager;
import com.mybatisflex.spring.service.impl.ServiceImpl;
import org.eu.originalkeen.core.constant.SystemConstant;
import org.eu.originalkeen.core.domain.bo.PermissionBo;
import org.eu.originalkeen.core.exception.BusinessException;
import org.eu.originalkeen.core.utils.LocaleUtils;
import org.eu.originalkeen.system.permission.domain.bo.PermissionNodeBo;
import org.eu.originalkeen.system.permission.domain.bo.ValidateAuthorityUniqueBo;
import org.eu.originalkeen.system.permission.domain.entity.PermissionEntity;
import org.eu.originalkeen.system.permission.domain.vo.PermissionDetailsVo;
import org.eu.originalkeen.system.permission.domain.vo.PermissionNodeVo;
import org.eu.originalkeen.system.permission.mapper.PermissionMapper;
import org.eu.originalkeen.system.permission.service.PermissionService;
import org.springframework.stereotype.Service;

import java.util.HashSet;
import java.util.List;
import java.util.Set;

import static com.mybatisflex.core.query.QueryMethods.distinct;
import static org.eu.originalkeen.system.permission.domain.entity.table.PermissionTableDef.permission;
import static org.eu.originalkeen.system.permission.domain.entity.table.PermissionTranslationTableDef.permission_translation;
import static org.eu.originalkeen.system.permission.domain.entity.table.RolePermissionTableDef.role_permission;
import static org.eu.originalkeen.system.role.domain.entity.table.RoleTableDef.role;
import static org.eu.originalkeen.system.role.domain.entity.table.UserRoleTableDef.user_role;

/**
 * 权限服务实现类
 * 实现权限管理相关的业务逻辑，包括权限的增删改查和树形结构管理
 * <p>
 * 主要功能：
 * 1. 查询权限详情和权限树形结构
 * 2. 查询用户所拥有的权限
 * 3. 校验权限的有效性和唯一性
 * 4. 管理权限节点及其子节点
 * <p>
 * 继承自ServiceImpl，自动注入PermissionMapper用于数据库操作
 */
@Service
public class PermissionServiceImpl extends ServiceImpl<PermissionMapper, PermissionEntity> implements PermissionService {

    /**
     * 查询权限详情
     * 获取指定权限ID的详细信息，包括权限的各项属性
     *
     * @param id 要查询的权限ID
     * @return 包含权限详细信息的响应对象
     * @throws BusinessException 当权限不存在时抛出
     */
    @Override
    public PermissionDetailsVo enquiryDetails(Long id) {
        return mapper.selectOneWithRelationsByQueryAs(
                queryChain()
                        .select(
                                permission.id,
                                permission.parent_id,
                                permission.authority,
                                permission.sort,
                                permission.permission_type,
                                permission.icon,
                                permission.link_address,
                                permission.link_target,
                                permission.router_path,
                                permission.component_path,
                                permission.keep_alive,
                                permission.visible,
                                permission.permission_status
                        )
                        .from(permission)
                        .where(permission.id.eq(id)),
                PermissionDetailsVo.class
        );
    }

    /**
     * 查询权限树
     * 获取整个权限树结构，从根节点开始的所有权限节点
     *
     * @return 包含权限树结构的响应对象
     */
    @Override
    public List<PermissionNodeVo> enquiryTree() {
        // 1. 设置关联查询的最大深度，确保能够查询到完整的树形结构
        RelationManager.setMaxDepth(10);

        // 2. 添加额外的语言代码参数，用于查询对应语言的权限名称
        RelationManager.addExtraConditionParam("languageCode", LocaleUtils.getLangCode());

        return mapper.selectListWithRelationsByQueryAs(
                queryChain()
                        .select(
                                permission.id,
                                permission.parent_id,
                                permission_translation.permission_name,
                                permission.authority,
                                permission.sort,
                                permission.permission_type,
                                permission.icon,
                                permission.link_address,
                                permission.link_target,
                                permission.router_path,
                                permission.component_path,
                                permission.keep_alive,
                                permission.visible,
                                permission.permission_status,
                                permission.created_time
                        )
                        .from(permission)
                        .innerJoin(permission_translation)
                        .on(permission.id.eq(permission_translation.permission_id))
                        .where(permission.parent_id.eq(SystemConstant.PERMISSION_ROOT_NODE_ID))
                        .and(permission_translation.language_code.eq(LocaleUtils.getLangCode()))
                        .orderBy(permission.sort.asc()),
                PermissionNodeVo.class
        );
    }

    /**
     * 查询用户的权限
     * 根据用户ID查询用户所有的权限信息
     *
     * @param userId 用户ID
     * @return 用户的权限列表
     */
    @Override
    public List<PermissionBo> selectUserPermissions(Long userId) {
        return queryChain()
                .select(distinct(
                        permission.id,
                        permission.parent_id,
                        permission_translation.permission_name,
                        permission.authority,
                        permission.sort,
                        permission.permission_type,
                        permission.icon,
                        permission.link_address,
                        permission.link_target,
                        permission.router_path,
                        permission.component_path,
                        permission.keep_alive,
                        permission.visible
                ))
                .from(user_role)
                .innerJoin(role)
                .on(user_role.role_id.eq(role.id))
                .innerJoin(role_permission)
                .on(role_permission.role_id.eq(role.id))
                .innerJoin(permission)
                .on(permission.id.eq(role_permission.permission_id))
                .innerJoin(permission_translation)
                .on(permission.id.eq(permission_translation.permission_id))
                // 添加查询条件
                // 只查询指定用户ID且权限状态为启用的权限
                .where(user_role.user_id.eq(userId))
                .and(permission.permission_status.eq(SystemConstant.PERMISSION_ENABLED_STATUS))
                .and(permission_translation.language_code.eq(LocaleUtils.getLangCode()))
                // 将查询结果映射为PermissionBo对象列表
                .listAs(PermissionBo.class);
    }

    /**
     * 过滤出有效的权限ID
     * 从权限ID列表中过滤出实际存在于数据库中的权限ID
     *
     * @param permissionIds 要过滤的权限ID列表
     * @return 有效的权限ID列表
     */
    @Override
    public Set<Long> selectEffectivePermissionIds(Set<Long> permissionIds) {
        return new HashSet<>(queryChain()
                .select(permission.id)
                .from(permission)
                .where(permission.id.in(permissionIds))
                .listAs(Long.class)
        );
    }

    /**
     * 校验权限是否存在
     * 根据权限ID校验权限是否存在，如果是根节点ID则直接返回true
     *
     * @param permissionId 要校验的权限ID
     * @return 如果权限存在返回true，否则返回false
     */
    @Override
    public boolean selectPermissionExists(Long permissionId) {
        if (SystemConstant.PERMISSION_ROOT_NODE_ID.equals(permissionId)) {
            return true;
        }

        return exists(permission.id.eq(permissionId));
    }

    /**
     * 校验权限标识是否存在
     * 校验指定的权限标识（authority）是否已经存在，排除当前权限ID
     *
     * @param validateAuthorityUniqueBo 权限标识唯一性校验对象
     * @return 如果权限标识已存在返回true，否则返回false
     */
    @Override
    public boolean selectAuthorityExists(ValidateAuthorityUniqueBo validateAuthorityUniqueBo) {
        return exists(permission.id.ne(validateAuthorityUniqueBo.getId(), If::notNull)
                .and(permission.authority.eq(validateAuthorityUniqueBo.getAuthority()))
        );
    }

    /**
     * 查询权限节点及其子节点
     * 根据权限ID查询权限节点及其所有子节点的树形结构
     *
     * @param permissionId 权限ID
     * @return 权限节点对象，包含子节点信息
     */
    @Override
    public PermissionNodeBo selectPermissionNodes(Long permissionId) {
        // 设置关联查询的最大深度，确保能够查询到完整的树形结构
        RelationManager.setMaxDepth(10);

        return mapper.selectOneWithRelationsByQueryAs(
                queryChain()
                        .select(permission.id, permission.parent_id)
                        .from(permission)
                        .where(permission.id.eq(permissionId)),
                PermissionNodeBo.class
        );
    }

    /**
     * 查询用户权限的多语言信息
     * 根据用户ID查询用户权限的标识和名称，仅用于多语言切换
     *
     * @param userId 用户ID
     * @return 用户权限的多语言信息列表
     */
    @Override
    public List<PermissionBo> selectUserPermissionsForLanguage(Long userId) {
        return queryChain()
                .select(
                        permission.authority,
                        permission_translation.permission_name
                )
                .from(user_role)
                .innerJoin(role)
                .on(user_role.role_id.eq(role.id))
                .innerJoin(role_permission)
                .on(role_permission.role_id.eq(role.id))
                .innerJoin(permission)
                .on(permission.id.eq(role_permission.permission_id))
                .innerJoin(permission_translation)
                .on(permission.id.eq(permission_translation.permission_id))
                // 添加查询条件
                // 只查询指定用户ID且权限状态为启用的权限
                .where(user_role.user_id.eq(userId))
                .and(permission.permission_status.eq(SystemConstant.PERMISSION_ENABLED_STATUS))
                .and(permission_translation.language_code.eq(LocaleUtils.getLangCode()))
                // 将查询结果映射为PermissionBo对象列表
                .listAs(PermissionBo.class);
    }

}
