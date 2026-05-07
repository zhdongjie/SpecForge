package org.eu.originalkeen.system.permission.service.impl;

import com.mybatisflex.core.query.If;
import com.mybatisflex.spring.service.impl.ServiceImpl;
import org.eu.originalkeen.system.permission.domain.bo.ValidatePermissionNameUniqueBo;
import org.eu.originalkeen.system.permission.domain.dto.PermissionTranslationDto;
import org.eu.originalkeen.system.permission.domain.entity.PermissionTranslationEntity;
import org.eu.originalkeen.system.permission.mapper.PermissionTranslationMapper;
import org.eu.originalkeen.system.permission.service.PermissionTranslationService;
import org.apache.commons.collections4.CollectionUtils;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.function.Function;
import java.util.stream.Collectors;

import static org.eu.originalkeen.system.permission.domain.entity.table.PermissionTranslationTableDef.permission_translation;

/**
 * 权限翻译服务实现类
 * 实现权限翻译的业务逻辑方法
 * <p>
 * 主要功能：
 * 1. 校验权限名称的唯一性
 * 2. 创建、更新和删除权限的翻译记录
 * 3. 查询权限的多语言翻译信息
 * <p>
 * 继承自ServiceImpl，自动注入PermissionTranslationMapper用于数据库操作
 */
@Service
public class PermissionTranslationServiceImpl extends ServiceImpl<PermissionTranslationMapper, PermissionTranslationEntity> implements PermissionTranslationService {

    /**
     * 校验权限名称是否存在
     * 校验指定的权限名称是否已经存在，排除当前权限ID
     *
     * @param validatePermissionNameUniqueBo 权限名称唯一性校验对象
     * @return 如果权限名称已存在返回true，否则返回false
     */
    @Override
    public Set<String> selectExistsPermissionNames(ValidatePermissionNameUniqueBo validatePermissionNameUniqueBo) {
        return new HashSet<>(queryChain()
                .select(permission_translation.permission_name)
                .from(permission_translation)
                .where(permission_translation.permission_id.ne(validatePermissionNameUniqueBo.getId(), If::notNull))
                .and(permission_translation.permission_name.in(validatePermissionNameUniqueBo.getPermissionNames()))
                .listAs(String.class)
        );
    }

    /**
     * 创建权限翻译
     * 为指定权限创建翻译记录
     *
     * @param permissionId 权限ID
     * @param translations 权限翻译DTO列表
     */
    @Override
    public void createPermissionTranslations(Long permissionId, List<PermissionTranslationDto> translations) {
        List<PermissionTranslationEntity> translationEntities = translations.stream()
                .map(translation -> PermissionTranslationEntity.of(permissionId, translation))
                .toList();

        saveBatch(translationEntities);
    }

    /**
     * 删除权限翻译
     * 删除指定权限的所有翻译记录
     *
     * @param permissionIds 权限ID列表
     */
    @Override
    public void deletePermissionTranslations(Set<Long> permissionIds) {
        remove(permission_translation.permission_id.in(permissionIds));
    }

    /**
     * 更新权限翻译
     * 更新指定权限的翻译记录
     *
     * @param permissionId 权限ID
     * @param translations 新的权限翻译DTO列表
     */
    @Override
    public void updatePermissionTranslations(Long permissionId, List<PermissionTranslationDto> translations) {
        // 1. 查询所有的翻译记录
        //    获取数据库中已存在的权限翻译
        List<PermissionTranslationEntity> existingTranslations = queryChain()
                .select()
                .from(permission_translation)
                .where(permission_translation.permission_id.eq(permissionId))
                .list();

        // 2. 创建一个Map，以语言代码为键，以现有翻译实体为值
        //    便于快速查找特定语言的翻译
        Map<String, PermissionTranslationEntity> existingTranslationsMap = existingTranslations.stream()
                .collect(Collectors.toMap(PermissionTranslationEntity::getLanguageCode, Function.identity()));

        // 3. 处理更新和新增
        //    区分需要更新的记录和需要新增的记录
        List<PermissionTranslationEntity> toUpdate = new ArrayList<>();
        List<PermissionTranslationEntity> toInsert = new ArrayList<>();

        for (PermissionTranslationDto translationDto : translations) {
            String languageCode = translationDto.getLanguageCode();
            if (existingTranslationsMap.containsKey(languageCode)) {
                // 3.1 更新记录
                //     如果该语言的翻译已存在，则更新其内容
                PermissionTranslationEntity existingEntity = existingTranslationsMap.get(languageCode);
                existingEntity.setPermissionName(translationDto.getPermissionName());
                toUpdate.add(existingEntity);
            } else {
                // 3.2 新增记录
                //     如果该语言的翻译不存在，则创建新记录
                toInsert.add(PermissionTranslationEntity.of(permissionId, translationDto));
            }
        }

        // 4. 批量更新和新增
        //    执行数据库操作，更新和新增翻译记录
        if (CollectionUtils.isNotEmpty(toUpdate)) {
            updateBatch(toUpdate);
        }

        if (CollectionUtils.isNotEmpty(toInsert)) {
            saveBatch(toInsert);
        }
    }

    /**
     * 查询已被使用的权限名称
     * 根据权限ID列表查询对应的权限名称
     *
     * @param usedPermissionIds 已被使用的权限ID列表
     * @return 已被使用的权限名称列表
     */
    @Override
    public Set<String> selectUsedPermissionNames(Set<Long> usedPermissionIds) {
        List<String> permissionNames = queryChain()
                .select(permission_translation.permission_name)
                .from(permission_translation)
                .where(permission_translation.permission_id.in(usedPermissionIds))
                .listAs(String.class);

        return new HashSet<>(permissionNames);
    }

}
