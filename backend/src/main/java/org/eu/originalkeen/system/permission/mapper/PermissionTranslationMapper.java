package org.eu.originalkeen.system.permission.mapper;

import com.mybatisflex.core.BaseMapper;
import org.eu.originalkeen.system.permission.domain.entity.PermissionTranslationEntity;
import org.apache.ibatis.annotations.Mapper;

/**
 * 权限翻译数据访问接口
 * 提供权限翻译实体的数据库访问操作
 */
@Mapper
public interface PermissionTranslationMapper extends BaseMapper<PermissionTranslationEntity> {
}
