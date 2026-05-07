package org.eu.originalkeen.system.role.mapper;

import com.mybatisflex.core.BaseMapper;
import org.eu.originalkeen.system.role.domain.entity.UserRoleEntity;
import org.apache.ibatis.annotations.Mapper;

/**
 * 用户角色关系映射器
 * 提供用户角色关系实体的数据库操作方法
 */
@Mapper
public interface UserRoleMapper extends BaseMapper<UserRoleEntity> {
}
