package org.eu.originalkeen.system.dictionary.data.service;

import com.mybatisflex.core.service.IService;
import org.eu.originalkeen.system.dictionary.data.domain.bo.ValidateDictionaryDataLabelUniqueBo;
import org.eu.originalkeen.system.dictionary.data.domain.dto.DictionaryDataTranslationDto;
import org.eu.originalkeen.system.dictionary.data.domain.entity.DictionaryDataTranslationEntity;

import java.util.List;
import java.util.Set;

/**
 * 字典数据翻译服务接口
 * 提供字典数据翻译管理相关的业务逻辑方法
 */
public interface DictionaryDataTranslationService extends IService<DictionaryDataTranslationEntity> {

    /**
     * 批量保存字典数据翻译
     * 批量保存字典数据的多语言翻译信息
     *
     * @param dictionaryDataId 字典数据ID
     * @param translations     字典数据翻译DTO列表
     */
    void batchSave(Long dictionaryDataId, List<DictionaryDataTranslationDto> translations);

    /**
     * 批量更新字典数据翻译
     * 批量更新字典数据的多语言翻译信息
     *
     * @param dictionaryDataId 字典数据ID
     * @param translations     字典数据翻译DTO列表
     */
    void batchUpdate(Long dictionaryDataId, List<DictionaryDataTranslationDto> translations);

    /**
     * 根据字典数据ID列表删除字典数据翻译
     * 批量删除多个字典数据的所有翻译信息
     *
     * @param dictionaryDataIds 字典数据ID列表
     */
    void deleteByDictionaryDataIds(Set<Long> dictionaryDataIds);

    /**
     * 查询字典数据标签是否存在
     * 查询指定的字典数据标签是否已经存在，排除当前字典数据ID
     *
     * @param validateDictionaryDataLabelUniqueBo 字典数据标签唯一性校验业务对象
     * @return 已存在的字典数据标签列表
     */
    Set<String> selectExistsDictionaryDataLabels(ValidateDictionaryDataLabelUniqueBo validateDictionaryDataLabelUniqueBo);

}
