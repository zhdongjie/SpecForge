package org.eu.originalkeen.system.role.manager;

import org.eu.originalkeen.core.constant.SystemConstant;
import org.eu.originalkeen.core.domain.vo.PageVo;
import org.eu.originalkeen.core.domain.vo.ResponseVo;
import org.eu.originalkeen.core.exception.BusinessException;
import org.eu.originalkeen.core.exception.business.FieldValidationException;
import org.eu.originalkeen.core.utils.TranslationUtils;
import org.eu.originalkeen.system.dictionary.data.service.DictionaryDataService;
import org.eu.originalkeen.system.permission.service.PermissionService;
import org.eu.originalkeen.system.permission.service.RolePermissionService;
import org.eu.originalkeen.system.role.domain.bo.RoleTranslationBo;
import org.eu.originalkeen.system.role.domain.bo.ValidateRoleBo;
import org.eu.originalkeen.system.role.domain.bo.ValidateRoleCodeUniqueBo;
import org.eu.originalkeen.system.role.domain.bo.ValidateRoleNameUniqueBo;
import org.eu.originalkeen.system.role.domain.dto.*;
import org.eu.originalkeen.system.role.domain.entity.RoleEntity;
import org.eu.originalkeen.system.role.domain.vo.RoleDetailsVo;
import org.eu.originalkeen.system.role.domain.vo.RoleListVo;
import org.eu.originalkeen.system.role.domain.vo.RolePageVo;
import org.eu.originalkeen.system.role.service.RoleService;
import org.eu.originalkeen.system.role.service.RoleTranslationService;
import org.eu.originalkeen.system.role.service.UserRoleService;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.collections4.CollectionUtils;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Objects;
import java.util.Set;
import java.util.stream.Collectors;

import static org.eu.originalkeen.system.role.domain.entity.table.RoleTableDef.role;

/**
 * 角色管理器
 * 提供角色相关的业务处理功能，整合角色服务、角色翻译服务和角色权限服务等
 * <p>
 * 主要功能：
 * 1. 角色的创建、更新、删除和查询
 * 2. 角色与权限的关联管理
 * 3. 角色信息的校验逻辑
 * 4. 角色翻译信息的管理
 * <p>
 * 使用@Slf4j注解提供日志记录功能
 */
@Slf4j
@Component
public class RoleManager {

    /**
     * 用户角色关系服务
     * 用于管理用户与角色之间的关联关系
     */
    @Resource
    private UserRoleService userRoleService;

    /**
     * 角色服务
     * 提供角色的基本CRUD操作和查询功能
     */
    @Resource
    private RoleService roleService;

    /**
     * 角色权限关联服务
     * 管理角色与权限之间的关联关系
     */
    @Resource
    private RolePermissionService rolePermissionService;

    /**
     * 权限服务
     * 用于管理权限信息和角色与权限的关联关系
     */
    @Resource
    private PermissionService permissionService;

    /**
     * 角色翻译服务
     * 用于管理角色翻译数据信息
     */
    @Resource
    private RoleTranslationService roleTranslationService;

    /**
     * 字典数据服务
     * 用于管理字典数据信息和校验
     */
    @Resource
    private DictionaryDataService dictionaryDataService;

    /**
     * 校验角色名称是否唯一
     * 校验指定的角色名称在系统中是否已经存在
     *
     * @param validateRoleNameUniqueDto 角色名称唯一性校验的DTO对象
     * @return 包含角色名称是否存在的响应对象，true表示已存在，false表示不存在
     */
    @Transactional(readOnly = true)
    public ResponseVo<Boolean> validateRoleNameUnique(ValidateRoleNameUniqueDto validateRoleNameUniqueDto) {
        // 1. 转换DTO为业务对象
        //    将前端传来的DTO转换为内部业务处理对象
        ValidateRoleNameUniqueBo validateRoleNameUniqueBo = ValidateRoleNameUniqueBo.of(validateRoleNameUniqueDto);

        // 2. 查询角色名称是否存在
        //    校验数据库中是否已存在相同的角色名称（排除当前角色ID）
        Set<String> existsRoleNames = roleTranslationService.selectExistsRoleNames(validateRoleNameUniqueBo);

        // 3. 返回校验结果
        //    如果列表不为空，表示角色名称已存在
        return ResponseVo.success(CollectionUtils.isNotEmpty(existsRoleNames));
    }

    /**
     * 校验角色代码是否唯一
     * 校验指定的角色代码在系统中是否已经存在
     *
     * @param validateRoleCodeUniqueDto 角色代码唯一性校验的DTO对象
     * @return 包含角色代码是否存在的响应对象，true表示已存在，false表示不存在
     */
    @Transactional(readOnly = true)
    public ResponseVo<Boolean> validateRoleCodeUnique(ValidateRoleCodeUniqueDto validateRoleCodeUniqueDto) {
        // 1. 转换DTO为业务对象
        //    将前端传来的DTO转换为内部业务处理对象
        ValidateRoleCodeUniqueBo validateRoleCodeUniqueBo = ValidateRoleCodeUniqueBo.of(validateRoleCodeUniqueDto);

        // 2. 查询角色代码是否存在
        //    校验数据库中是否已存在相同的角色代码（排除当前角色ID）
        boolean exists = roleService.selectRoleCodeExists(validateRoleCodeUniqueBo);

        // 3. 返回校验结果
        //    返回角色代码是否存在的布尔值
        return ResponseVo.success(exists);
    }

    /**
     * 创建新的角色
     * 在系统中创建一个新的角色记录，并建立与权限的关联关系
     *
     * @param createRoleDto 创建角色的DTO对象，包含角色的各项属性和权限ID列表
     * @return 创建结果的响应对象
     * @throws BusinessException        当角色名称已存在时抛出
     * @throws FieldValidationException 当角色属性校验失败时抛出
     */
    @Transactional
    public ResponseVo<Void> create(CreateRoleDto createRoleDto) {
        // 1. 校验角色信息：校验角色代码唯一性、角色名称唯一性、角色状态有效性
        ValidateRoleBo validateRoleBo = ValidateRoleBo.of(createRoleDto);
        validateRoleInfo(validateRoleBo);

        // 2. 创建角色实体
        //    根据DTO构建实体对象，准备保存到数据库
        RoleEntity roleEntity = RoleEntity.of(createRoleDto);

        // 3. 保存角色基本信息到数据库
        //    此时会生成角色ID，后续关联操作需要使用此ID
        roleService.save(roleEntity);

        // 4. 保存角色多语言翻译信息
        //    为角色创建不同语言的名称和描述翻译记录
        roleTranslationService.createRoleTranslations(
                roleEntity.getId(),
                createRoleDto.getTranslations()
        );

        // 5. 获取有效的权限ID列表
        //    校验传入的权限ID是否有效，过滤出有效的权限ID
        Set<Long> effectivePermissionIds = getEffectivePermissionIds(
                createRoleDto.getPermissionIds()
        );

        // 6. 创建角色与权限的关联关系
        //    在角色权限关联表中建立记录，关联角色与其对应的权限
        rolePermissionService.createRolePermissionRelation(
                roleEntity.getId(),
                effectivePermissionIds
        );

        // 7. 返回成功响应
        return ResponseVo.success();
    }

    /**
     * 批量删除角色
     * 删除指定的一组角色，如果角色正在被用户使用则不允许删除
     *
     * @param roleIds 要删除的角色ID列表
     * @return 删除结果的响应对象
     * @throws BusinessException 当角色正在被用户使用时抛出
     */
    @Transactional
    public ResponseVo<Void> batchDelete(Set<Long> roleIds) {
        // 1. 校验角色是否正在被用户使用
        //    查询用户角色关联表，确定要删除的角色是否已分配给用户
        Set<Long> usedRoleIds = userRoleService.selectUsedRoleIds(roleIds);

        // 2. 如果角色正在被使用，抛出业务异常阻止删除
        //    查询出角色名称并在日志和异常信息中显示，便于问题排查
        if (CollectionUtils.isNotEmpty(usedRoleIds)) {
            Set<String> usedRoleNames = roleTranslationService.selectUsedRoleNames(usedRoleIds);
            log.warn("Unable to delete roles [{}] as they are in use", String.join(", ", usedRoleNames));
            throw new BusinessException("form.role.unableDeleteRoles", String.join(", ", usedRoleNames));
        }

        // 3. 删除角色基本信息
        //    从角色表中删除指定ID的角色记录
        roleService.removeByIds(roleIds);

        // 4. 删除角色的多语言翻译信息
        //    清理角色翻译表中关联的翻译记录
        roleTranslationService.deleteRoleTranslations(roleIds);

        // 5. 删除角色与权限的关联关系
        //    清理角色权限关联表中的关联记录
        rolePermissionService.deleteRolePermissionRelation(roleIds);

        // 6. 返回成功响应
        return ResponseVo.success();
    }

    /**
     * 更新角色信息
     * 更新指定角色的各项属性，并更新与权限的关联关系
     *
     * @param updateRoleDto 更新角色的DTO对象，包含要更新的角色属性和权限ID列表
     * @return 更新结果的响应对象
     * @throws BusinessException        当角色不存在，或角色名称与其他角色冲突时抛出
     * @throws FieldValidationException 当角色属性校验失败时抛出
     */
    @Transactional
    public ResponseVo<Void> update(UpdateRoleDto updateRoleDto) {
        // 1. 校验角色信息
        //    校验角色是否存在、角色代码和名称是否与其他角色冲突、角色状态是否有效
        ValidateRoleBo validateRoleBo = ValidateRoleBo.of(updateRoleDto);
        validateRoleInfo(validateRoleBo);

        // 2. 创建角色实体并更新基本信息
        //    根据DTO构建实体对象，更新角色表中的记录
        RoleEntity roleEntity = RoleEntity.of(updateRoleDto);
        Long roleId = updateRoleDto.getId();
        roleService.update(roleEntity, role.id.eq(roleId));

        // 3. 更新角色的多语言翻译信息
        //    更新已有的翻译记录，对于新增的语言创建新记录
        roleTranslationService.updateRoleTranslations(roleId, updateRoleDto.getTranslations());

        // 4. 获取有效的权限ID列表
        //    校验传入的权限ID是否有效，筛选出有效的权限ID
        Set<Long> effectivePermissionIds = getEffectivePermissionIds(
                updateRoleDto.getPermissionIds()
        );

        // 5. 更新角色与权限的关联关系
        //    比较新旧权限列表，删除不需要的权限关联，新增需要的权限关联
        updateRolePermissionRelation(roleId, effectivePermissionIds);

        // 6. 返回成功响应
        return ResponseVo.success();
    }

    /**
     * 分页查询角色列表
     * 根据查询条件分页获取角色列表
     *
     * @param enquiryRolePageDto 角色分页查询的DTO对象，包含分页参数和查询条件
     * @return 包含角色分页数据的响应对象
     */
    @Transactional(readOnly = true)
    public ResponseVo<PageVo<RolePageVo>> enquiryPage(EnquiryRolePageDto enquiryRolePageDto) {
        // 1. 调用角色服务的分页查询方法
        //    将查询条件传递给服务层，获取分页结果
        PageVo<RolePageVo> rolePageVo = roleService.enquiryPage(enquiryRolePageDto);

        // 2. 封装并返回查询结果
        //    将分页数据包装为统一响应格式
        return ResponseVo.success(rolePageVo);
    }

    /**
     * 查询角色详情
     * 获取指定角色ID的详细信息
     *
     * @param id 要查询的角色ID
     * @return 包含角色详细信息的响应对象
     * @throws BusinessException 当角色不存在时抛出
     */
    @Transactional(readOnly = true)
    public ResponseVo<RoleDetailsVo> enquiryDetails(Long id) {
        // 1. 调用角色服务查询角色详情
        //    根据ID查询角色的详细信息，包括多语言翻译
        RoleDetailsVo roleDetailsVo = roleService.enquiryDetails(id);

        // 2. 校验角色是否存在
        //    如果角色不存在，记录警告日志并抛出业务异常
        if (Objects.isNull(roleDetailsVo)) {
            log.warn("Role [{}] not found when enquiring details", id);
            throw new BusinessException("form.role.roleNotFound");
        }

        // 3. 封装并返回查询结果
        //    将角色详情数据包装为统一响应格式
        return ResponseVo.success(roleDetailsVo);
    }

    /**
     * 查询所有角色列表
     * 获取系统中所有角色的列表
     *
     * @return 包含所有角色列表的响应对象
     */
    @Transactional(readOnly = true)
    public ResponseVo<List<RoleListVo>> enquiryList() {
        // 1. 调用角色服务查询所有启用状态的角色
        //    获取所有可用角色的列表，用于前端下拉选择等场景
        List<RoleListVo> roleList = roleService.enquiryList();

        // 2. 封装并返回查询结果
        //    将角色列表数据包装为统一响应格式
        return ResponseVo.success(roleList);
    }

    /**
     * 更新角色权限关系
     * 比较新旧权限ID列表，删除不再需要的权限关联，添加新的权限关联
     *
     * @param roleId                 角色ID
     * @param effectivePermissionIds 有效的权限ID列表
     */
    private void updateRolePermissionRelation(Long roleId, Set<Long> effectivePermissionIds) {
        // 1. 查询角色当前关联的权限ID列表
        //    获取数据库中已存在的角色-权限关联关系
        Set<Long> oldPermissionIds = rolePermissionService.selectPermissionIdsByRoleId(roleId);

        // 2. 判断新旧权限列表是否有变化
        //    如果新旧列表完全相同，则不需要进行任何更新操作
        if (!CollectionUtils.containsAll(oldPermissionIds, effectivePermissionIds)
                || !CollectionUtils.containsAll(effectivePermissionIds, oldPermissionIds)) {

            // 3. 找出需要删除的权限关联
            //    筛选出在旧列表中存在但在新列表中不存在的权限ID
            Set<Long> deletedPermissionIds = filterDeletedPermissionIds(effectivePermissionIds, oldPermissionIds);

            // 4. 删除不再需要的权限关联
            //    如果有需要删除的权限关联，调用服务删除这些关联记录
            if (CollectionUtils.isNotEmpty(deletedPermissionIds)) {
                rolePermissionService.deleteRolePermissionRelation(roleId, deletedPermissionIds);
            }

            // 5. 找出需要新增的权限关联
            //    筛选出在新列表中存在但在旧列表中不存在的权限ID
            Set<Long> addedPermissionIds = filterAddedPermissionIds(effectivePermissionIds, oldPermissionIds);

            // 6. 创建新的权限关联
            //    如果有需要新增的权限关联，调用服务创建这些关联记录
            if (CollectionUtils.isNotEmpty(addedPermissionIds)) {
                rolePermissionService.createRolePermissionRelation(roleId, addedPermissionIds);
            }
        }
    }

    /**
     * 筛选需要删除的权限ID
     * 通过比较新旧权限ID列表，找出需要删除的权限ID（在旧列表中存在但在新列表中不存在）
     *
     * @param newPermissionIds 新的权限ID列表
     * @param oldPermissionIds 旧的权限ID列表
     * @return 需要删除的权限ID列表
     */
    private Set<Long> filterDeletedPermissionIds(Set<Long> newPermissionIds, Set<Long> oldPermissionIds) {
        return oldPermissionIds.stream()
                .filter(oldPermissionId -> !newPermissionIds.contains(oldPermissionId))
                .collect(Collectors.toSet());
    }

    /**
     * 筛选需要添加的权限ID
     * 通过比较新旧权限ID列表，找出需要添加的权限ID（在新列表中存在但在旧列表中不存在）
     *
     * @param newPermissionIds 新的权限ID列表
     * @param oldPermissionIds 旧的权限ID列表
     * @return 需要添加的权限ID列表
     */
    private Set<Long> filterAddedPermissionIds(Set<Long> newPermissionIds, Set<Long> oldPermissionIds) {
        return newPermissionIds.stream()
                .filter(newPermissionId -> !oldPermissionIds.contains(newPermissionId))
                .collect(Collectors.toSet());
    }

    /**
     * 获取有效的权限ID列表
     * 通过权限服务校验权限ID的有效性，过滤出有效的权限ID
     *
     * @param permissionIds 要校验的权限ID列表
     * @return 有效的权限ID列表
     * @throws FieldValidationException 当没有有效权限时抛出
     */
    private Set<Long> getEffectivePermissionIds(Set<Long> permissionIds) {
        Set<Long> effectivePermissionIds = permissionService.selectEffectivePermissionIds(
                permissionIds
        );

        if (CollectionUtils.isEmpty(effectivePermissionIds)) {
            log.warn("Invalid permission list: no valid permissions found");
            throw new FieldValidationException("permissionIds", "form.role.invalidPermissionList");
        }
        return effectivePermissionIds;
    }

    /**
     * 校验角色信息
     * 校验角色的各项信息，包括角色是否存在、角色名称是否唯一、角色代码是否唯一、角色状态是否有效
     * <p>
     * 校验流程：
     * 1. 如果是更新操作，校验角色是否存在
     * 2. 校验翻译数据的有效性
     * 3. 校验角色状态值是否有效
     * 4. 校验角色名称在各语言中是否唯一
     * 5. 校验角色代码是否唯一
     *
     * @param validateRoleBo 角色校验对象
     * @throws BusinessException        当角色不存在时抛出
     * @throws FieldValidationException 当角色名称已存在或角色代码已存在时抛出
     */
    private void validateRoleInfo(ValidateRoleBo validateRoleBo) {
        // 1. 如果是更新操作，校验角色是否存在
        //    对于更新操作，需要确保要更新的角色记录存在
        Long roleId = validateRoleBo.getId();
        if (Objects.nonNull(roleId)) {
            boolean roleExists = roleService.selectRoleExists(roleId);
            if (!roleExists) {
                log.warn("Role [{}] not found when validating role info", roleId);
                throw new BusinessException("form.role.roleNotFound");
            }
        }

        // 2. 校验翻译数据的有效性
        //    确保所有必需的语言翻译都已提供，且语言代码有效
        TranslationUtils.validateTranslations(
                validateRoleBo.getTranslations(),
                RoleTranslationBo::getLanguageCode
        );

        // 3. 校验角色状态的有效性
        //    校验角色状态值是否在字典中定义，是否为有效值
        dictionaryDataService.validateDictionaryDataValue(
                SystemConstant.DICTIONARY_CODE_ROLE_STATUS,
                validateRoleBo.getRoleStatus(),
                "roleStatus",
                "form.role.invalidRoleStatus"
        );

        // 4. 校验角色名称在各语言中是否唯一
        //    确保不同语言的角色名称都不与现有角色冲突
        ValidateRoleNameUniqueBo validateRoleNameUniqueBo = ValidateRoleNameUniqueBo.of(validateRoleBo);
        Set<String> existingRoleNames = roleTranslationService.selectExistsRoleNames(validateRoleNameUniqueBo);

        if (CollectionUtils.isNotEmpty(existingRoleNames)) {
            log.warn("Role names already exists: [{}]", String.join(", ", existingRoleNames));
            throw new FieldValidationException("translations", "form.role.roleNamesAlreadyExists", String.join(", ", existingRoleNames));
        }

        // 5. 校验角色代码的唯一性
        //    确保角色代码在系统中是唯一的，不与其他角色冲突
        ValidateRoleCodeUniqueBo validateRoleCodeUniqueBo = ValidateRoleCodeUniqueBo.of(validateRoleBo);
        boolean roleCodeExists = roleService.selectRoleCodeExists(validateRoleCodeUniqueBo);

        if (roleCodeExists) {
            log.warn("Role code already exists: [{}]", validateRoleCodeUniqueBo.getRoleCode());
            throw new FieldValidationException("roleCode", "form.role.roleCodeAlreadyExists");
        }
    }

}
