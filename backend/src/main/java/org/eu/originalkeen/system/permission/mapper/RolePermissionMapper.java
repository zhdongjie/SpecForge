package org.eu.originalkeen.system.permission.mapper;

import com.mybatisflex.core.BaseMapper;
import org.eu.originalkeen.system.permission.domain.entity.RolePermissionEntity;
import org.apache.ibatis.annotations.Mapper;

/**
 * 角色权限关系映射器
 * 提供角色权限关系实体的数据库操作方法
 */
@Mapper
public interface RolePermissionMapper extends BaseMapper<RolePermissionEntity> {
}
