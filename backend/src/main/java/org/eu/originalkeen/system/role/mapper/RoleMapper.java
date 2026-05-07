package org.eu.originalkeen.system.role.mapper;

import com.mybatisflex.core.BaseMapper;
import org.eu.originalkeen.system.role.domain.entity.RoleEntity;
import org.apache.ibatis.annotations.Mapper;

/**
 * 角色映射器
 * 提供角色实体的数据库操作方法
 */
@Mapper
public interface RoleMapper extends BaseMapper<RoleEntity> {
}
