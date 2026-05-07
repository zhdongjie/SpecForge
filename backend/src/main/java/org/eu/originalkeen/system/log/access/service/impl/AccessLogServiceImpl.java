package org.eu.originalkeen.system.log.access.service.impl;

import com.mybatisflex.spring.service.impl.ServiceImpl;
import org.eu.originalkeen.system.log.access.domain.entity.AccessLogEntity;
import org.eu.originalkeen.system.log.access.mapper.AccessLogMapper;
import org.eu.originalkeen.system.log.access.service.AccessLogService;
import org.springframework.stereotype.Service;

/**
 * 访问日志服务实现类
 * 实现访问日志管理相关的业务逻辑，如登录、注册等访问日志的记录和查询
 */
@Service
public class AccessLogServiceImpl extends ServiceImpl<AccessLogMapper, AccessLogEntity> implements AccessLogService {
}
