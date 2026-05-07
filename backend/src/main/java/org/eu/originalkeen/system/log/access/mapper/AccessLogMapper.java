package org.eu.originalkeen.system.log.access.mapper;

import com.mybatisflex.core.BaseMapper;
import org.eu.originalkeen.system.log.access.domain.entity.AccessLogEntity;
import org.apache.ibatis.annotations.Mapper;

/**
 * 访问日志映射器
 * 提供访问日志实体的数据库操作方法
 */
@Mapper
public interface AccessLogMapper extends BaseMapper<AccessLogEntity> {
}
