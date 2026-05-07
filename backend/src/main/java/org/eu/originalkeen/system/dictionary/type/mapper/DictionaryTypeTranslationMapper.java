package org.eu.originalkeen.system.dictionary.type.mapper;

import com.mybatisflex.core.BaseMapper;
import org.eu.originalkeen.system.dictionary.type.domain.entity.DictionaryTypeTranslationEntity;
import org.apache.ibatis.annotations.Mapper;

/**
 * 字典类型翻译映射器
 * 提供字典类型翻译实体的数据库操作方法
 */
@Mapper
public interface DictionaryTypeTranslationMapper extends BaseMapper<DictionaryTypeTranslationEntity> {
} 
