package org.eu.originalkeen.system.dictionary.type.mapper;

import com.mybatisflex.core.BaseMapper;
import org.eu.originalkeen.system.dictionary.type.domain.entity.DictionaryTypeEntity;
import org.apache.ibatis.annotations.Mapper;

/**
 * 字典类型映射器
 * 提供字典类型实体的数据库操作方法
 */
@Mapper
public interface DictionaryTypeMapper extends BaseMapper<DictionaryTypeEntity> {
}
