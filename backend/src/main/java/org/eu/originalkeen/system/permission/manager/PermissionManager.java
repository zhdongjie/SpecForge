package org.eu.originalkeen.system.permission.manager;

import org.eu.originalkeen.core.constant.SystemConstant;
import org.eu.originalkeen.core.domain.vo.ResponseVo;
import org.eu.originalkeen.core.exception.BusinessException;
import org.eu.originalkeen.core.exception.business.FieldValidationException;
import org.eu.originalkeen.core.utils.TranslationUtils;
import org.eu.originalkeen.system.dictionary.data.service.DictionaryDataService;
import org.eu.originalkeen.system.permission.domain.bo.*;
import org.eu.originalkeen.system.permission.domain.dto.CreatePermissionDto;
import org.eu.originalkeen.system.permission.domain.dto.UpdatePermissionDto;
import org.eu.originalkeen.system.permission.domain.dto.ValidateAuthorityUniqueDto;
import org.eu.originalkeen.system.permission.domain.dto.ValidatePermissionNameUniqueDto;
import org.eu.originalkeen.system.permission.domain.entity.PermissionEntity;
import org.eu.originalkeen.system.permission.domain.vo.PermissionDetailsVo;
import org.eu.originalkeen.system.permission.domain.vo.PermissionNodeVo;
import org.eu.originalkeen.system.permission.service.PermissionService;
import org.eu.originalkeen.system.permission.service.PermissionTranslationService;
import org.eu.originalkeen.system.permission.service.RolePermissionService;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.collections4.CollectionUtils;
import org.apache.commons.lang3.StringUtils;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Objects;
import java.util.Set;

import static org.eu.originalkeen.system.permission.domain.entity.table.PermissionTableDef.permission;

/**
 * 权限管理器
 * 提供权限相关的业务处理功能，整合权限服务、权限翻译服务和角色权限服务等
 * <p>
 * 主要功能：
 * 1. 权限的创建、更新、删除和查询
 * 2. 权限树形结构的管理
 * 3. 权限信息的校验逻辑
 * 4. 权限翻译信息的管理
 * <p>
 * 使用@Slf4j注解提供日志记录功能
 */
@Slf4j
@Component
public class PermissionManager {

    /**
     * 权限服务
     * 提供权限的基本CRUD操作和查询功能
     */
    @Resource
    private PermissionService permissionService;

    /**
     * 角色权限关联服务
     * 管理角色与权限之间的关联关系
     */
    @Resource
    private RolePermissionService rolePermissionService;

    /**
     * 权限翻译服务
     * 用于管理权限翻译数据信息
     */
    @Resource
    private PermissionTranslationService permissionTranslationService;

    /**
     * 字典数据服务
     * 用于管理字典数据信息和校验
     */
    @Resource
    private DictionaryDataService dictionaryDataService;

    /**
     * 校验权限名称是否唯一
     * 校验指定的权限名称在系统中是否已经存在
     *
     * @param validatePermissionNameUniqueDto 权限名称唯一性校验的DTO对象
     * @return 包含权限名称是否存在的响应对象，true表示已存在，false表示不存在
     */
    @Transactional(readOnly = true)
    public ResponseVo<Boolean> validatePermissionNameUnique(ValidatePermissionNameUniqueDto validatePermissionNameUniqueDto) {
        // 1. 转换DTO为业务对象
        //    将前端传来的DTO转换为内部业务处理对象
        ValidatePermissionNameUniqueBo validatePermissionNameUniqueBo =
                ValidatePermissionNameUniqueBo.of(validatePermissionNameUniqueDto);

        // 2. 查询权限名称是否存在
        //    校验数据库中是否已存在相同的权限名称（排除当前权限ID）
        Set<String> existsPermissionNames = permissionTranslationService.selectExistsPermissionNames(validatePermissionNameUniqueBo);

        // 3. 返回校验结果
        //    如果列表不为空，表示权限名称已存在
        return ResponseVo.success(CollectionUtils.isNotEmpty(existsPermissionNames));
    }

    /**
     * 校验权限标识是否唯一
     * 校验指定的权限标识在系统中是否已经存在
     *
     * @param validateAuthorityUniqueDto 权限标识唯一性校验的DTO对象
     * @return 包含权限标识是否存在的响应对象，true表示已存在，false表示不存在
     */
    @Transactional(readOnly = true)
    public ResponseVo<Boolean> validateAuthorityUnique(ValidateAuthorityUniqueDto validateAuthorityUniqueDto) {
        // 1. 转换DTO为业务对象
        //    将前端传来的DTO转换为内部业务处理对象
        ValidateAuthorityUniqueBo validateAuthorityUniqueBo =
                ValidateAuthorityUniqueBo.of(validateAuthorityUniqueDto);

        // 2. 查询权限标识是否存在
        //    校验数据库中是否已存在相同的权限标识（排除当前权限ID）
        boolean exists = permissionService.selectAuthorityExists(validateAuthorityUniqueBo);

        // 3. 返回校验结果
        //    返回权限标识是否存在的布尔值
        return ResponseVo.success(exists);
    }

    /**
     * 创建新的权限
     * 在系统中创建一个新的权限记录，并保存权限翻译信息
     *
     * @param createPermissionDto 创建权限的DTO对象，包含权限的各项属性
     * @return 创建结果的响应对象
     * @throws BusinessException        当权限名称或标识已存在时抛出
     * @throws FieldValidationException 当权限属性校验失败时抛出
     */
    @Transactional
    public ResponseVo<Void> create(CreatePermissionDto createPermissionDto) {
        // 1. 校验权限信息：校验权限名称唯一性、权限标识唯一性、权限类型有效性等
        //    校验权限提交的各项属性是否符合业务规则
        ValidatePermissionBo validatePermissionBo = ValidatePermissionBo.of(createPermissionDto);
        validatePermissionInfo(validatePermissionBo);

        // 2. 创建权限实体
        //    根据DTO构建实体对象，准备保存到数据库
        PermissionEntity permissionEntity = PermissionEntity.of(createPermissionDto);

        // 3. 校验权限类型是否有效
        //    如果权限实体为null，表示权限类型无效
        if (Objects.isNull(permissionEntity)) {
            throw new FieldValidationException("permissionType", "form.permission.invalidPermissionType");
        }

        // 4. 保存权限基本信息到数据库
        //    此时会生成权限ID，后续关联操作需要使用此ID
        permissionService.save(permissionEntity);

        // 5. 保存权限翻译信息
        //    为权限创建不同语言的名称和描述翻译记录
        permissionTranslationService.createPermissionTranslations(
                permissionEntity.getId(),
                createPermissionDto.getTranslations()
        );

        // 6. 返回成功响应
        return ResponseVo.success();
    }

    /**
     * 删除权限节点
     * 删除指定的权限节点及其所有子节点
     *
     * @param permissionId 要删除的权限节点ID
     * @return 删除结果的响应对象
     * @throws BusinessException 当权限节点或其子节点正在被角色使用时抛出
     */
    @Transactional
    public ResponseVo<Void> deleteNode(Long permissionId) {
        // 1. 查询权限节点及其所有子节点
        //    获取要删除的权限节点的完整树形结构
        PermissionNodeBo permissionNodeBo = permissionService.selectPermissionNodes(permissionId);

        if (Objects.nonNull(permissionNodeBo)) {
            // 2. 获取所有需要删除的节点ID
            //    包括当前节点及其所有子节点的ID列表
            Set<Long> allNodeIds = permissionNodeBo.getAllNodeIds();

            // 3. 校验权限节点是否正在被角色使用
            //    查询角色权限关联表，确定要删除的权限是否已分配给角色
            Set<Long> usedPermissionIds = rolePermissionService.selectUsedPermissionIds(allNodeIds);

            if (CollectionUtils.isNotEmpty(usedPermissionIds)) {
                // 4. 如果权限正在被使用，查询权限名称并抛出业务异常阻止删除
                //    获取被使用的权限名称，用于错误提示
                Set<String> usedPermissionNames = permissionTranslationService.selectUsedPermissionNames(usedPermissionIds);

                String permissionNameList = String.join(", ", usedPermissionNames);

                log.warn("Unable delete permission. Permission or its child node is already in use: {}", usedPermissionNames);

                throw new BusinessException("form.permission.unableDeletePermission", permissionNameList);
            }

            // 5. 删除权限节点及其子节点
            //    从数据库中删除所有相关的权限记录
            permissionService.removeByIds(allNodeIds);

            // 6. 删除权限翻译信息
            //    从数据库中删除权限的多语言翻译记录
            permissionTranslationService.deletePermissionTranslations(allNodeIds);
        }

        // 7. 返回成功响应
        return ResponseVo.success();
    }

    /**
     * 更新权限信息
     * 更新指定权限的各项属性，并更新权限翻译信息
     *
     * @param updatePermissionDto 更新权限的DTO对象，包含要更新的权限属性
     * @return 更新结果的响应对象
     * @throws BusinessException        当权限不存在，或权限名称与其他权限冲突时抛出
     * @throws FieldValidationException 当权限属性校验失败时抛出
     */
    @Transactional
    public ResponseVo<Void> update(UpdatePermissionDto updatePermissionDto) {
        // 1. 校验权限信息：校验权限是否存在、权限名称唯一性、权限标识唯一性等
        //    校验权限提交的各项属性是否符合业务规则
        ValidatePermissionBo validatePermissionBo = ValidatePermissionBo.of(updatePermissionDto);
        validatePermissionInfo(validatePermissionBo);

        // 2. 创建权限实体并更新
        //    根据DTO构建实体对象，准备更新到数据库
        PermissionEntity permissionEntity = PermissionEntity.of(updatePermissionDto);
        Long permissionId = updatePermissionDto.getId();
        permissionService.update(permissionEntity, permission.id.eq(permissionId));

        // 3. 更新权限翻译信息
        //    更新权限的多语言名称和描述翻译记录
        permissionTranslationService.updatePermissionTranslations(permissionId, updatePermissionDto.getTranslations());

        // 4. 返回成功响应
        return ResponseVo.success();
    }

    /**
     * 查询权限详情
     * 获取指定权限ID的详细信息
     *
     * @param id 要查询的权限ID
     * @return 包含权限详细信息的响应对象
     * @throws BusinessException 当权限不存在时抛出
     */
    @Transactional(readOnly = true)
    public ResponseVo<PermissionDetailsVo> enquiryDetails(Long id) {
        // 1. 查询权限详情
        //    根据ID获取权限的完整信息，包括基本属性和翻译数据
        PermissionDetailsVo permissionDetailsVo = permissionService.enquiryDetails(id);

        // 2. 校验权限是否存在
        //    如果查询结果为空，表示权限不存在，抛出异常
        if (Objects.isNull(permissionDetailsVo)) {
            log.warn("Permission [{}] not found when enquiring details", id);
            throw new BusinessException("form.permission.permissionNotFound");
        }

        // 3. 返回权限详情
        //    包装为响应对象返回给调用方
        return ResponseVo.success(permissionDetailsVo);
    }

    /**
     * 查询权限树
     * 获取权限的树形结构
     *
     * @return 包含权限树的响应对象
     */
    @Transactional(readOnly = true)
    public ResponseVo<List<PermissionNodeVo>> enquiryTree() {
        // 1. 查询权限树
        //    获取系统中所有权限的树形结构表示
        List<PermissionNodeVo> permissionTree = permissionService.enquiryTree();

        // 2. 返回权限树
        //    包装为响应对象返回给调用方
        return ResponseVo.success(permissionTree);
    }

    /**
     * 校验权限信息
     * 校验权限的各项信息，包括权限是否存在、父节点是否存在、权限名称是否唯一、权限标识是否唯一等
     * <p>
     * 校验流程：
     * 1. 如果是更新操作，校验权限是否存在
     * 2. 校验父节点是否存在
     * 3. 校验翻译数据的有效性
     * 4. 校验权限类型值是否有效
     * 5. 如果是链接类型，校验链接目标值是否有效
     * 6. 校验权限状态值是否有效
     * 7. 校验权限名称在各语言中是否唯一
     * 8. 校验权限标识是否唯一
     *
     * @param validatePermissionBo 权限校验对象
     * @throws BusinessException        当权限不存在或父节点不存在时抛出
     * @throws FieldValidationException 当权限属性校验失败时抛出
     */
    private void validatePermissionInfo(ValidatePermissionBo validatePermissionBo) {
        // 1. 如果是更新操作，校验权限是否存在
        //    更新操作时需要确认要更新的权限记录存在于数据库中
        Long permissionId = validatePermissionBo.getId();
        if (Objects.nonNull(permissionId)) {
            boolean permissionExists = permissionService.selectPermissionExists(permissionId);
            if (!permissionExists) {
                log.warn("Permission [{}] does not exist", permissionId);
                throw new BusinessException("form.permission.permissionNotFound");
            }
        }

        // 2. 校验父节点是否存在
        //    校验指定的父节点ID是否存在于数据库中，确保树形结构的完整性
        boolean parentNodeExists = permissionService.selectPermissionExists(validatePermissionBo.getParentId());
        if (!parentNodeExists) {
            log.warn("Invalid parent ID [{}]: parent node does not exist", validatePermissionBo.getParentId());
            throw new FieldValidationException("parentId", "form.permission.invalidParentId");
        }

        // 3. 校验翻译数据
        //    校验翻译数据列表中的语言代码是否有效，确保多语言支持的正确性
        TranslationUtils.validateTranslations(
                validatePermissionBo.getTranslations(),
                PermissionTranslationBo::getLanguageCode
        );

        // 4. 校验权限类型
        //    校验权限类型值是否在字典中定义，确保类型值的有效性
        dictionaryDataService.validateDictionaryDataValue(
                SystemConstant.DICTIONARY_CODE_PERMISSION_TYPE,
                validatePermissionBo.getPermissionType(),
                "permissionType",
                "form.permission.invalidPermissionType"
        );

        // 5. 如果是链接类型，校验链接目标
        //    对于链接类型的权限，需要额外校验链接目标值的有效性
        if (StringUtils.equals(SystemConstant.PERMISSION_TYPE_LINK, validatePermissionBo.getPermissionType())) {
            // 校验权限链接目标
            dictionaryDataService.validateDictionaryDataValue(
                    SystemConstant.DICTIONARY_CODE_PERMISSION_LINK_TARGET,
                    validatePermissionBo.getLinkTarget(),
                    "linkTarget",
                    "form.permission.invalidLinkTarget"
            );
        }

        // 6. 校验权限状态
        //    校验权限状态值是否在字典中定义，确保状态值的有效性
        dictionaryDataService.validateDictionaryDataValue(
                SystemConstant.DICTIONARY_CODE_PERMISSION_STATUS,
                validatePermissionBo.getPermissionStatus(),
                "permissionStatus",
                "form.permission.invalidPermissionStatus"
        );

        // 7. 校验权限名称唯一性
        //    确保不同语言的权限名称在系统中是唯一的，避免命名冲突
        ValidatePermissionNameUniqueBo validatePermissionNameUniqueBo =
                ValidatePermissionNameUniqueBo.of(validatePermissionBo);
        Set<String> existingPermissionNames = permissionTranslationService.selectExistsPermissionNames(
                validatePermissionNameUniqueBo
        );

        if (CollectionUtils.isNotEmpty(existingPermissionNames)) {
            log.warn("Permission names already exists: [{}]", String.join(", ", existingPermissionNames));
            throw new FieldValidationException(
                    "translations",
                    "form.permission.permissionNamesAlreadyExists",
                    String.join(", ", existingPermissionNames)
            );
        }

        // 8. 校验权限标识字符串唯一性
        //    确保权限标识在系统中是唯一的，避免授权冲突
        ValidateAuthorityUniqueBo validateAuthorityUniqueBo =
                ValidateAuthorityUniqueBo.of(validatePermissionBo);
        boolean authorityExists = permissionService.selectAuthorityExists(validateAuthorityUniqueBo);

        if (authorityExists) {
            log.warn("Authority [{}] already exists", validateAuthorityUniqueBo.getAuthority());
            throw new FieldValidationException("authority", "form.permission.authorityAlreadyExists");
        }
    }

}
