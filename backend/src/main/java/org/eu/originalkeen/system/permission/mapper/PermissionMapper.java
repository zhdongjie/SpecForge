package org.eu.originalkeen.system.permission.mapper;

import com.mybatisflex.core.BaseMapper;
import org.eu.originalkeen.system.permission.domain.entity.PermissionEntity;
import org.apache.ibatis.annotations.Mapper;

/**
 * 权限映射器
 * 提供权限实体的数据库操作方法
 */
@Mapper
public interface PermissionMapper extends BaseMapper<PermissionEntity> {
}
