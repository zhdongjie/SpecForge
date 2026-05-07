package org.eu.originalkeen.system.dictionary.type.service.impl;

import com.mybatisflex.core.query.If;
import com.mybatisflex.spring.service.impl.ServiceImpl;
import org.eu.originalkeen.system.dictionary.type.domain.bo.ValidateDictionaryTypeNameUniqueBo;
import org.eu.originalkeen.system.dictionary.type.domain.dto.DictionaryTypeTranslationDto;
import org.eu.originalkeen.system.dictionary.type.domain.entity.DictionaryTypeTranslationEntity;
import org.eu.originalkeen.system.dictionary.type.mapper.DictionaryTypeTranslationMapper;
import org.eu.originalkeen.system.dictionary.type.service.DictionaryTypeTranslationService;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.collections4.CollectionUtils;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.function.Function;
import java.util.stream.Collectors;

import static org.eu.originalkeen.system.dictionary.type.domain.entity.table.DictionaryTypeTranslationTableDef.dictionary_type_translation;

/**
 * 字典类型翻译服务实现类
 * 实现字典类型翻译管理相关的业务逻辑
 * <p>
 * 主要功能：
 * 1. 实现字典类型翻译服务接口定义的所有方法
 * 2. 处理字典类型翻译的查询、创建、更新和删除
 * 3. 提供字典类型名称唯一性校验
 * 4. 管理字典类型的多语言翻译数据
 * <p>
 * 继承自ServiceImpl，自动注入DictionaryTypeTranslationMapper用于数据库操作
 */
@Slf4j
@Service
public class DictionaryTypeTranslationServiceImpl extends ServiceImpl<DictionaryTypeTranslationMapper, DictionaryTypeTranslationEntity> implements DictionaryTypeTranslationService {

    /**
     * 查询字典类型名称是否存在
     * 校验指定的字典类型名称是否已经存在，排除当前字典类型ID
     *
     * @param validateDictionaryTypeNameUniqueBo 字典类型名称唯一性校验对象
     * @return 已存在的字典类型名称列表
     */
    @Override
    public Set<String> selectExistsDictionaryTypeNames(ValidateDictionaryTypeNameUniqueBo validateDictionaryTypeNameUniqueBo) {
        return new HashSet<>(queryChain()
                .select(dictionary_type_translation.dictionary_type_name)
                .from(dictionary_type_translation)
                // 排除当前字典类型ID的翻译记录（如果有ID）
                .where(dictionary_type_translation.dictionary_type_id.ne(validateDictionaryTypeNameUniqueBo.getId(), If::notNull))
                // 筛选匹配的字典类型名称
                .and(dictionary_type_translation.dictionary_type_name.in(validateDictionaryTypeNameUniqueBo.getDictionaryTypeNames()))
                // 执行查询并转换为字符串列表，再转为HashSet
                .listAs(String.class)
        );
    }

    /**
     * 创建字典类型翻译
     * 为指定字典类型创建多语言翻译记录
     * <p>
     * 实现步骤：
     * 1. 将DTO对象转换为实体对象
     * 2. 批量保存翻译实体
     *
     * @param dictionaryTypeId 字典类型ID
     * @param translations     字典类型翻译DTO列表
     */
    @Override
    public void createDictionaryTypeTranslations(Long dictionaryTypeId, List<DictionaryTypeTranslationDto> translations) {
        List<DictionaryTypeTranslationEntity> translationEntities = translations.stream()
                .map(translation -> DictionaryTypeTranslationEntity.of(dictionaryTypeId, translation))
                .toList();

        saveBatch(translationEntities);
    }

    /**
     * 删除字典类型翻译
     * 删除指定字典类型ID列表的所有翻译记录
     * <p>
     * 实现步骤：
     * 1. 构建删除条件
     * 2. 执行批量删除操作
     *
     * @param dictionaryTypeIds 字典类型ID列表
     */
    @Override
    public void deleteDictionaryTypeTranslations(Set<Long> dictionaryTypeIds) {
        remove(dictionary_type_translation.dictionary_type_id.in(dictionaryTypeIds));
    }

    /**
     * 更新字典类型翻译
     * 更新指定字典类型的翻译记录，支持新增、更新和保留操作
     * <p>
     * 实现步骤：
     * 1. 查询现有的翻译记录
     * 2. 将现有记录转换为Map，以语言代码为键
     * 3. 处理更新和新增操作
     * 4. 批量执行更新和新增
     *
     * @param dictionaryTypeId 字典类型ID
     * @param translations     新的字典类型翻译DTO列表
     */
    @Override
    public void updateDictionaryTypeTranslations(Long dictionaryTypeId, List<DictionaryTypeTranslationDto> translations) {
        // 1. 查询所有的翻译记录
        //    查询指定字典类型ID的所有翻译记录
        List<DictionaryTypeTranslationEntity> existingTranslations = queryChain()
                .select()
                .from(dictionary_type_translation)
                .where(dictionary_type_translation.dictionary_type_id.eq(dictionaryTypeId))
                .list();

        // 2. 创建一个Map，以语言代码为键，以现有翻译实体为值
        //    便于快速查找和更新现有记录
        Map<String, DictionaryTypeTranslationEntity> existingTranslationsMap = existingTranslations.stream()
                .collect(Collectors.toMap(DictionaryTypeTranslationEntity::getLanguageCode, Function.identity()));

        // 3. 处理更新和新增
        //    分别收集需要更新和新增的记录
        List<DictionaryTypeTranslationEntity> toUpdate = new ArrayList<>();
        List<DictionaryTypeTranslationEntity> toInsert = new ArrayList<>();

        for (DictionaryTypeTranslationDto translationDto : translations) {
            String languageCode = translationDto.getLanguageCode();
            if (existingTranslationsMap.containsKey(languageCode)) {
                // 3.1 更新记录
                //    更新已存在的翻译记录字段
                DictionaryTypeTranslationEntity existingEntity = existingTranslationsMap.get(languageCode);
                existingEntity.setDictionaryTypeName(translationDto.getDictionaryTypeName());
                existingEntity.setRemark(translationDto.getRemark());
                toUpdate.add(existingEntity);
            } else {
                // 3.2 新增记录
                //    创建新的翻译记录
                toInsert.add(DictionaryTypeTranslationEntity.of(dictionaryTypeId, translationDto));
            }
        }

        // 4. 批量更新和新增
        //    分别执行批量更新和批量新增操作
        if (CollectionUtils.isNotEmpty(toUpdate)) {
            // 4.1 批量更新
            //    更新已存在的翻译记录
            updateBatch(toUpdate);
        }

        if (CollectionUtils.isNotEmpty(toInsert)) {
            // 4.2 批量新增
            //    插入新的翻译记录
            saveBatch(toInsert);
        }
    }

}
