package org.eu.originalkeen.system.dictionary.type.service;

import com.mybatisflex.core.service.IService;
import org.eu.originalkeen.system.dictionary.type.domain.bo.ValidateDictionaryTypeNameUniqueBo;
import org.eu.originalkeen.system.dictionary.type.domain.dto.DictionaryTypeTranslationDto;
import org.eu.originalkeen.system.dictionary.type.domain.entity.DictionaryTypeTranslationEntity;

import java.util.List;
import java.util.Set;

/**
 * 字典类型翻译服务接口
 * 提供字典类型翻译管理相关的业务逻辑方法
 */
public interface DictionaryTypeTranslationService extends IService<DictionaryTypeTranslationEntity> {

    /**
     * 查询字典类型名称是否存在
     * 根据字典类型名称校验是否已存在记录
     *
     * @param validateDictionaryTypeNameUniqueBo 字典类型名称唯一性校验业务对象
     * @return 存在的字典类型名称列表
     */
    Set<String> selectExistsDictionaryTypeNames(ValidateDictionaryTypeNameUniqueBo validateDictionaryTypeNameUniqueBo);

    /**
     * 创建字典类型翻译
     * 创建新的字典类型翻译记录
     *
     * @param dictionaryTypeId 字典类型ID
     * @param translations     字典类型翻译DTO列表
     */
    void createDictionaryTypeTranslations(Long dictionaryTypeId, List<DictionaryTypeTranslationDto> translations);

    /**
     * 删除字典类型翻译
     * 删除指定字典类型ID列表的字典类型翻译记录
     *
     * @param dictionaryTypeIds 字典类型ID列表
     */
    void deleteDictionaryTypeTranslations(Set<Long> dictionaryTypeIds);

    /**
     * 更新字典类型翻译
     * 更新指定字典类型的翻译记录
     *
     * @param dictionaryTypeId 字典类型ID
     * @param translations     字典类型翻译DTO列表
     */
    void updateDictionaryTypeTranslations(Long dictionaryTypeId, List<DictionaryTypeTranslationDto> translations);

} 
