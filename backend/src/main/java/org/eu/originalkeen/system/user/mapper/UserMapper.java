package org.eu.originalkeen.system.user.mapper;

import com.mybatisflex.core.BaseMapper;
import org.eu.originalkeen.system.user.domain.entity.UserEntity;
import org.apache.ibatis.annotations.Mapper;

/**
 * 用户映射器
 * 提供用户实体的数据库操作方法
 */
@Mapper
public interface UserMapper extends BaseMapper<UserEntity> {
}
