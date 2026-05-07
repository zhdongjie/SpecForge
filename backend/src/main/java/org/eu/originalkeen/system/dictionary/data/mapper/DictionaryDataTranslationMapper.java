package org.eu.originalkeen.system.dictionary.data.mapper;

import com.mybatisflex.core.BaseMapper;
import org.eu.originalkeen.system.dictionary.data.domain.entity.DictionaryDataTranslationEntity;
import org.apache.ibatis.annotations.Mapper;

/**
 * 字典数据翻译Mapper接口
 * 提供字典数据翻译表的数据访问方法
 */
@Mapper
public interface DictionaryDataTranslationMapper extends BaseMapper<DictionaryDataTranslationEntity> {
}
