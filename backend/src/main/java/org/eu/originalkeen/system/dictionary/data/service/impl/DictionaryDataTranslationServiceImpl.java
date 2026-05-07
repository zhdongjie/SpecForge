package org.eu.originalkeen.system.dictionary.data.service.impl;

import com.mybatisflex.core.query.If;
import com.mybatisflex.spring.service.impl.ServiceImpl;
import org.eu.originalkeen.system.dictionary.data.domain.bo.ValidateDictionaryDataLabelUniqueBo;
import org.eu.originalkeen.system.dictionary.data.domain.dto.DictionaryDataTranslationDto;
import org.eu.originalkeen.system.dictionary.data.domain.entity.DictionaryDataTranslationEntity;
import org.eu.originalkeen.system.dictionary.data.mapper.DictionaryDataTranslationMapper;
import org.eu.originalkeen.system.dictionary.data.service.DictionaryDataTranslationService;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.collections4.CollectionUtils;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.function.Function;
import java.util.stream.Collectors;

import static org.eu.originalkeen.system.dictionary.data.domain.entity.table.DictionaryDataTableDef.dictionary_data;
import static org.eu.originalkeen.system.dictionary.data.domain.entity.table.DictionaryDataTranslationTableDef.dictionary_data_translation;

/**
 * 字典数据翻译服务实现类
 * 实现字典数据翻译管理相关的业务逻辑
 * <p>
 * 主要功能：
 * 1. 实现字典数据翻译服务接口定义的所有方法
 * 2. 处理字典数据翻译的查询、创建、更新和删除
 * 3. 提供字典数据标签唯一性校验
 * 4. 管理字典数据的多语言翻译数据
 * <p>
 * 继承自ServiceImpl，自动注入DictionaryDataTranslationMapper用于数据库操作
 */
@Slf4j
@Service
public class DictionaryDataTranslationServiceImpl extends ServiceImpl<DictionaryDataTranslationMapper, DictionaryDataTranslationEntity> implements DictionaryDataTranslationService {

    /**
     * 查询字典数据标签是否存在
     * 查询指定的字典数据标签是否已经存在，排除当前字典数据ID
     *
     * @param validateDictionaryDataLabelUniqueBo 字典数据标签唯一性校验业务对象
     * @return 已存在的字典数据标签列表
     */
    @Override
    public Set<String> selectExistsDictionaryDataLabels(ValidateDictionaryDataLabelUniqueBo validateDictionaryDataLabelUniqueBo) {
        return new HashSet<>(queryChain()
                .select(dictionary_data_translation.label)
                .from(dictionary_data_translation)
                .leftJoin(dictionary_data)
                .on(dictionary_data_translation.dictionary_data_id.eq(dictionary_data.id))
                .where(dictionary_data_translation.dictionary_data_id.ne(validateDictionaryDataLabelUniqueBo.getId(), If::notNull))
                .and(dictionary_data.dictionary_type_code.eq(validateDictionaryDataLabelUniqueBo.getDictionaryTypeCode()))
                .and(dictionary_data_translation.label.in(validateDictionaryDataLabelUniqueBo.getLabels()))
                .listAs(String.class)
        );
    }

    /**
     * 批量保存字典数据翻译
     * 批量保存字典数据的多语言翻译信息
     *
     * @param dictionaryDataId 字典数据ID
     * @param translations     字典数据翻译DTO列表
     */
    @Override
    public void batchSave(Long dictionaryDataId, List<DictionaryDataTranslationDto> translations) {
        List<DictionaryDataTranslationEntity> translationEntities = translations.stream()
                .map(translation -> DictionaryDataTranslationEntity.of(dictionaryDataId, translation))
                .toList();

        saveBatch(translationEntities);
    }

    /**
     * 批量更新字典数据翻译
     * 批量更新字典数据的多语言翻译信息
     *
     * @param dictionaryDataId 字典数据ID
     * @param translations     字典数据翻译DTO列表
     */
    @Override
    public void batchUpdate(Long dictionaryDataId, List<DictionaryDataTranslationDto> translations) {
        // 1. 查询字典数据ID下所有现有的翻译记录
        // 获取数据库中该字典数据已有的所有语言翻译
        List<DictionaryDataTranslationEntity> existingTranslations = queryChain()
                .select()
                .from(dictionary_data_translation)
                .where(dictionary_data_translation.dictionary_data_id.eq(dictionaryDataId))
                .list();

        // 2. 将现有翻译记录按语言代码分类
        // 创建Map以便快速查找和更新现有翻译
        Map<String, DictionaryDataTranslationEntity> existingTranslationsMap = existingTranslations.stream()
                .collect(Collectors.toMap(DictionaryDataTranslationEntity::getLanguageCode, Function.identity()));

        // 3. 准备更新和新增的列表
        // 分别收集需要更新的现有记录和需要新增的记录
        List<DictionaryDataTranslationEntity> toUpdate = new ArrayList<>();
        List<DictionaryDataTranslationEntity> toInsert = new ArrayList<>();

        // 4. 处理每个翻译DTO，区分更新和新增操作
        for (DictionaryDataTranslationDto translationDto : translations) {
            String languageCode = translationDto.getLanguageCode();
            if (existingTranslationsMap.containsKey(languageCode)) {
                // 5. 更新现有记录：设置新的标签和备注
                DictionaryDataTranslationEntity existingEntity = existingTranslationsMap.get(languageCode);
                existingEntity.setLabel(translationDto.getLabel());
                existingEntity.setRemark(translationDto.getRemark());
                toUpdate.add(existingEntity);
            } else {
                // 6. 新增记录：创建新的翻译实体
                toInsert.add(DictionaryDataTranslationEntity.of(dictionaryDataId, translationDto));
            }
        }

        // 7. 批量执行更新操作
        // 如果有需要更新的记录，批量更新提高效率
        if (CollectionUtils.isNotEmpty(toUpdate)) {
            updateBatch(toUpdate);
        }

        // 8. 批量执行新增操作
        // 如果有需要新增的记录，批量保存提高效率
        if (CollectionUtils.isNotEmpty(toInsert)) {
            saveBatch(toInsert);
        }
    }

    /**
     * 根据字典数据ID列表删除字典数据翻译
     * 批量删除多个字典数据的所有翻译信息
     *
     * @param dictionaryDataIds 字典数据ID列表
     */
    @Override
    public void deleteByDictionaryDataIds(Set<Long> dictionaryDataIds) {
        remove(dictionary_data_translation.dictionary_data_id.in(dictionaryDataIds));
    }

} 
