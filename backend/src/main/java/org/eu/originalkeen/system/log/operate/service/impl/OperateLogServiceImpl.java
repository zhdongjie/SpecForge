package org.eu.originalkeen.system.log.operate.service.impl;

import com.mybatisflex.spring.service.impl.ServiceImpl;
import org.eu.originalkeen.system.log.operate.domain.entity.OperateLogEntity;
import org.eu.originalkeen.system.log.operate.mapper.OperateLogMapper;
import org.eu.originalkeen.system.log.operate.service.OperateLogService;
import org.springframework.stereotype.Service;

/**
 * 操作日志服务实现类
 * 实现操作日志管理相关的业务逻辑，如增删改查等操作日志的记录和查询
 */
@Service
public class OperateLogServiceImpl extends ServiceImpl<OperateLogMapper, OperateLogEntity> implements OperateLogService {
}
