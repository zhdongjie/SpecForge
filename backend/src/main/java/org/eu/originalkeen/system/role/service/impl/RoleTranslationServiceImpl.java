package org.eu.originalkeen.system.role.service.impl;

import com.mybatisflex.core.query.If;
import com.mybatisflex.spring.service.impl.ServiceImpl;
import org.eu.originalkeen.system.role.domain.bo.ValidateRoleNameUniqueBo;
import org.eu.originalkeen.system.role.domain.dto.RoleTranslationDto;
import org.eu.originalkeen.system.role.domain.entity.RoleTranslationEntity;
import org.eu.originalkeen.system.role.mapper.RoleTranslationMapper;
import org.eu.originalkeen.system.role.service.RoleTranslationService;
import org.apache.commons.collections4.CollectionUtils;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.function.Function;
import java.util.stream.Collectors;

import static org.eu.originalkeen.system.role.domain.entity.table.RoleTranslationTableDef.role_translation;

/**
 * 角色翻译服务实现类
 * 实现角色翻译的业务逻辑方法
 * <p>
 * 主要功能：
 * 1. 角色名称的多语言管理
 * 2. 角色翻译的增删改查
 * 3. 角色名称唯一性校验
 * <p>
 * 继承自ServiceImpl，自动注入RoleTranslationMapper用于数据库操作
 */
@Service
public class RoleTranslationServiceImpl extends ServiceImpl<RoleTranslationMapper, RoleTranslationEntity> implements RoleTranslationService {

    /**
     * 校验角色名称是否存在
     * 校验指定的角色名称是否已经存在，排除当前角色ID
     *
     * @param validateRoleNameUniqueBo 角色名称唯一性校验对象
     * @return 如果角色名称已存在返回true，否则返回false
     */
    @Override
    public Set<String> selectExistsRoleNames(ValidateRoleNameUniqueBo validateRoleNameUniqueBo) {
        return new HashSet<>(queryChain()
                .select(role_translation.role_name)
                .from(role_translation)
                .where(role_translation.role_id.ne(validateRoleNameUniqueBo.getId(), If::notNull))
                .and(role_translation.role_name.in(validateRoleNameUniqueBo.getRoleNames()))
                .listAs(String.class)
        );
    }

    /**
     * 创建角色翻译
     * 为指定角色创建翻译记录
     *
     * @param roleId       角色ID
     * @param translations 角色翻译DTO列表
     */
    @Override
    public void createRoleTranslations(Long roleId, List<RoleTranslationDto> translations) {
        List<RoleTranslationEntity> translationEntities = translations.stream()
                .map(translation -> RoleTranslationEntity.of(roleId, translation))
                .toList();

        saveBatch(translationEntities);
    }

    /**
     * 删除角色翻译
     * 删除指定角色的所有翻译记录
     *
     * @param roleIds 角色ID列表
     */
    @Override
    public void deleteRoleTranslations(Set<Long> roleIds) {
        remove(role_translation.role_id.in(roleIds));
    }

    /**
     * 更新角色翻译
     * 更新指定角色的翻译记录，分为更新已有记录和新增不存在的记录两部分
     * <p>
     * 处理流程：
     * 1. 查询该角色已有的所有翻译记录
     * 2. 根据语言代码将已有记录构建成Map
     * 3. 遍历新提交的翻译DTO，对已存在的语言进行更新，对不存在的语言进行新增
     * 4. 分别进行批量更新和批量插入操作
     *
     * @param roleId       角色ID
     * @param translations 新的角色翻译DTO列表
     */
    @Override
    public void updateRoleTranslations(Long roleId, List<RoleTranslationDto> translations) {
        // 1. 查询该角色已有的所有翻译记录
        //    根据角色ID查询数据库中已存在的翻译记录
        List<RoleTranslationEntity> existingTranslations = queryChain()
                .select()
                .from(role_translation)
                .where(role_translation.role_id.eq(roleId))
                .list();

        // 2. 创建一个Map，以语言代码为键，以现有翻译实体为值
        //    便于后续快速查找特定语言的翻译记录
        Map<String, RoleTranslationEntity> existingTranslationsMap = existingTranslations.stream()
                .collect(Collectors.toMap(RoleTranslationEntity::getLanguageCode, Function.identity()));

        // 3. 处理更新和新增
        //    区分需要更新的记录和需要新增的记录
        List<RoleTranslationEntity> toUpdate = new ArrayList<>();
        List<RoleTranslationEntity> toInsert = new ArrayList<>();

        for (RoleTranslationDto translationDto : translations) {
            String languageCode = translationDto.getLanguageCode();
            if (existingTranslationsMap.containsKey(languageCode)) {
                // 3.1 更新已存在的记录
                //     设置新的角色名称和备注
                RoleTranslationEntity existingEntity = existingTranslationsMap.get(languageCode);
                existingEntity.setRoleName(translationDto.getRoleName());
                existingEntity.setRemark(translationDto.getRemark());
                toUpdate.add(existingEntity);
            } else {
                // 3.2 创建新的翻译记录
                //     为不存在的语言创建新的翻译实体
                toInsert.add(RoleTranslationEntity.of(roleId, translationDto));
            }
        }

        // 4. 批量执行更新和新增操作
        //    如果有需要更新的记录，则执行批量更新
        if (CollectionUtils.isNotEmpty(toUpdate)) {
            updateBatch(toUpdate);
        }

        // 5. 批量执行新增操作
        //    如果有需要新增的记录，则执行批量新增
        if (CollectionUtils.isNotEmpty(toInsert)) {
            saveBatch(toInsert);
        }
    }

    /**
     * 查询已被使用的角色名称
     * 根据角色ID列表查询对应的角色名称
     *
     * @param usedRoleIds 已被使用的角色ID列表
     * @return 已被使用的角色名称列表
     */
    @Override
    public Set<String> selectUsedRoleNames(Set<Long> usedRoleIds) {
        return new HashSet<>(queryChain()
                .select(role_translation.role_name)
                .from(role_translation)
                .where(role_translation.role_id.in(usedRoleIds))
                .listAs(String.class));
    }

}
