package org.eu.originalkeen.core.aspectj;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.eu.originalkeen.core.annotation.AccessLog;
import org.eu.originalkeen.core.enums.AccessStatus;
import org.eu.originalkeen.core.enums.AccessType;
import org.eu.originalkeen.core.manager.AsyncManager;
import org.eu.originalkeen.core.manager.factory.AsyncFactory;
import org.eu.originalkeen.core.utils.AddressUtils;
import org.eu.originalkeen.core.utils.IpUtils;
import org.eu.originalkeen.core.utils.ServletUtils;
import org.eu.originalkeen.system.log.access.domain.entity.AccessLogEntity;
import eu.bitwalker.useragentutils.UserAgent;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.ArrayUtils;
import org.aspectj.lang.JoinPoint;
import org.aspectj.lang.annotation.AfterReturning;
import org.aspectj.lang.annotation.AfterThrowing;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.annotation.Before;
import org.springframework.core.NamedThreadLocal;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Component;

import java.util.Date;
import java.util.Objects;

/**
 * 访问日志切面
 * 用于拦截带有@AccessLog注解的方法，自动记录访问日志
 */
@Slf4j
@Aspect
@Component
public class AccessLogAspect {

    /**
     * 线程本地变量，用于记录响应时间
     * 存储请求开始时间，用于计算请求响应时间
     */
    private static final ThreadLocal<Long> TIME_THREADLOCAL = new NamedThreadLocal<>("Response Duration");

    /**
     * 前置通知
     * 在带有@AccessLog注解的方法执行前记录开始时间
     */
    @Before(value = "@annotation(org.eu.originalkeen.core.annotation.AccessLog)")
    public void boBefore() {
        TIME_THREADLOCAL.set(System.currentTimeMillis());
    }

    /**
     * 返回后通知
     * 在带有@AccessLog注解的方法正常返回后记录访问日志
     *
     * @param joinPoint      连接点
     * @param controllerLog  控制器日志注解
     * @param responseResult 响应结果
     */
    @AfterReturning(pointcut = "@annotation(controllerLog)", returning = "responseResult")
    public void doAfterReturning(JoinPoint joinPoint, AccessLog controllerLog, ResponseEntity<?> responseResult) {
        handlerLog(joinPoint, controllerLog, null, responseResult);
    }

    /**
     * 异常后通知
     * 在带有@AccessLog注解的方法抛出异常后记录访问日志
     *
     * @param joinPoint     连接点
     * @param controllerLog 控制器日志注解
     * @param exception     异常信息
     */
    @AfterThrowing(value = "@annotation(controllerLog)", throwing = "exception")
    public void doAfterThrowing(JoinPoint joinPoint, AccessLog controllerLog, Exception exception) {
        handlerLog(joinPoint, controllerLog, exception, null);
    }

    /**
     * 处理日志
     * 根据请求信息和响应结果构建访问日志并异步保存
     *
     * @param joinPoint      连接点
     * @param controllerLog  控制器日志注解
     * @param e              异常信息，如果有的话
     * @param responseResult 响应结果，如果有的话
     */
    private void handlerLog(JoinPoint joinPoint, AccessLog controllerLog, Exception e, ResponseEntity<?> responseResult) {
        try {
            String userAgentString = ServletUtils.getRequest().getHeader("User-Agent");
            UserAgent userAgent = UserAgent.parseUserAgentString(userAgentString);
            String accessIp = IpUtils.extractClientIp();
            String realAddress = AddressUtils.getRealAddressByIP(accessIp);
            AccessType accessType = controllerLog.value();
            AccessLogEntity accessLogEntity = new AccessLogEntity();

            setUsername(joinPoint, accessLogEntity);

            accessLogEntity.setAccessIp(accessIp);
            accessLogEntity.setAccessLocation(realAddress);
            accessLogEntity.setBrowser(userAgent.getBrowser().getName());
            accessLogEntity.setOperatingSystem(userAgent.getOperatingSystem().getName());
            accessLogEntity.setAccessType(accessType.name());
            AccessStatus accessStatus = null;
            String promptMessage = null;
            if (Objects.nonNull(responseResult)) {
                accessStatus = AccessStatus.SUCCESS;

                ObjectMapper objectMapper = new ObjectMapper();
                JsonNode jsonNode = null;
                try {
                    jsonNode = objectMapper.readTree(objectMapper.writeValueAsString(responseResult.getBody()));
                } catch (JsonProcessingException exception) {
                    log.error("Error serializing response or request parameters. Exception: {}, Response: {}",
                            exception.getMessage(), responseResult, exception);
                }
                if (Objects.nonNull(jsonNode) && jsonNode.hasNonNull("message")) {
                    promptMessage = jsonNode.get("message").textValue();
                }
            }

            if (Objects.nonNull(e)) {
                accessStatus = AccessStatus.FAILED;

                promptMessage = e.getMessage();
            }

            if (Objects.nonNull(accessStatus)) {
                accessLogEntity.setAccessStatus(accessStatus.name());
            }
            accessLogEntity.setPromptMessage(promptMessage);
            accessLogEntity.setAccessTime(new Date(System.currentTimeMillis()));

            log.info("Access OperateLog - IP: {}, Location: {}, Username: {}, Type: {}, Status: {}, Message: {}",
                    accessLogEntity.getAccessIp(),
                    accessLogEntity.getAccessLocation(),
                    accessLogEntity.getUsername(),
                    accessType.name(),
                    Objects.isNull(accessStatus) ? null : accessStatus.name(),
                    accessLogEntity.getPromptMessage()
            );

            AsyncManager.instance().execute(AsyncFactory.recordAccess(accessLogEntity));
        } finally {
            if (Objects.nonNull(TIME_THREADLOCAL.get())) {
                TIME_THREADLOCAL.remove();
                log.info("ThreadLocal cleared");
            }
        }
    }

    /**
     * 设置用户名
     * 从请求参数中提取用户名并设置到访问日志实体中
     *
     * @param joinPoint       连接点
     * @param accessLogEntity 访问日志实体
     */
    private void setUsername(JoinPoint joinPoint, AccessLogEntity accessLogEntity) {
        Object[] paramsArray = joinPoint.getArgs();
        if (ArrayUtils.isEmpty(paramsArray)) {
            return;
        }
        ObjectMapper objectMapper = new ObjectMapper();
        for (Object o : paramsArray) {
            JsonNode jsonNode = null;
            try {
                jsonNode = objectMapper.readTree(objectMapper.writeValueAsString(o));
            } catch (JsonProcessingException exception) {
                log.error("Error serializing parameter: {}", o, exception);
            }

            if (Objects.nonNull(jsonNode) && jsonNode.hasNonNull("username")) {
                accessLogEntity.setUsername(jsonNode.get("username").textValue());
                break;
            }
        }
    }

}
