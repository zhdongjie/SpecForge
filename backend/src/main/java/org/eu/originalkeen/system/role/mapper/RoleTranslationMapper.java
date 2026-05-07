package org.eu.originalkeen.system.role.mapper;

import com.mybatisflex.core.BaseMapper;
import org.eu.originalkeen.system.role.domain.entity.RoleTranslationEntity;
import org.apache.ibatis.annotations.Mapper;

/**
 * 角色翻译数据访问接口
 * 提供角色翻译实体的数据库访问操作
 */
@Mapper
public interface RoleTranslationMapper extends BaseMapper<RoleTranslationEntity> {
}
