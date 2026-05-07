package org.eu.originalkeen.system.dictionary.data.mapper;

import com.mybatisflex.core.BaseMapper;
import org.eu.originalkeen.system.dictionary.data.domain.entity.DictionaryDataEntity;
import org.apache.ibatis.annotations.Mapper;

/**
 * 字典数据Mapper接口
 * 提供字典数据表的数据访问方法
 */
@Mapper
public interface DictionaryDataMapper extends BaseMapper<DictionaryDataEntity> {
} 
