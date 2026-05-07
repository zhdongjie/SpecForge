package org.eu.originalkeen.system.log.operate.mapper;

import com.mybatisflex.core.BaseMapper;
import org.eu.originalkeen.system.log.operate.domain.entity.OperateLogEntity;
import org.apache.ibatis.annotations.Mapper;

/**
 * 操作日志映射器
 * 提供操作日志实体的数据库操作方法
 */
@Mapper
public interface OperateLogMapper extends BaseMapper<OperateLogEntity> {
}
