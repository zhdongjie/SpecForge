package org.eu.originalkeen.core.aspectj;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.ObjectWriter;
import org.eu.originalkeen.core.annotation.OperateLog;
import org.eu.originalkeen.core.domain.vo.ResponseVo;
import org.eu.originalkeen.core.enums.OperateStatus;
import org.eu.originalkeen.core.manager.AsyncManager;
import org.eu.originalkeen.core.manager.factory.AsyncFactory;
import org.eu.originalkeen.core.utils.AddressUtils;
import org.eu.originalkeen.core.utils.IpUtils;
import org.eu.originalkeen.core.utils.SecurityUtils;
import org.eu.originalkeen.core.utils.ServletUtils;
import org.eu.originalkeen.system.log.operate.domain.entity.OperateLogEntity;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.collections4.MapUtils;
import org.apache.commons.lang3.ArrayUtils;
import org.apache.commons.lang3.StringUtils;
import org.aspectj.lang.JoinPoint;
import org.aspectj.lang.annotation.AfterReturning;
import org.aspectj.lang.annotation.AfterThrowing;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.annotation.Before;
import org.springframework.core.NamedThreadLocal;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Component;
import org.springframework.validation.BindingResult;
import org.springframework.web.multipart.MultipartFile;

import java.util.Collection;
import java.util.Date;
import java.util.Map;
import java.util.Objects;

/**
 * 操作日志切面
 * 用于拦截带有@OperateLog注解的方法，自动记录操作日志
 */
@Slf4j
@Aspect
@Component
public class OperateLogAspect {

    /**
     * 排除的属性
     * 默认不记录到日志中的敏感属性，如密码等
     */
    private static final String[] EXCLUDE_PROPERTIES = {"password", "oldPassword", "newPassword", "confirmPassword"};

    /**
     * 线程本地变量，用于记录响应时间
     * 存储请求开始时间，用于计算请求响应时间
     */
    private static final ThreadLocal<Long> TIME_THREADLOCAL = new NamedThreadLocal<>("Response Duration");

    /**
     * 前置通知
     * 在带有@OperateLog注解的方法执行前记录开始时间
     */
    @Before(value = "@annotation(org.eu.originalkeen.core.annotation.OperateLog)")
    public void boBefore() {
        TIME_THREADLOCAL.set(System.currentTimeMillis());
    }

    /**
     * 返回后通知
     * 在带有@OperateLog注解的方法正常返回后记录操作日志
     *
     * @param joinPoint      连接点
     * @param controllerLog  控制器日志注解
     * @param responseResult 响应结果
     */
    @AfterReturning(pointcut = "@annotation(controllerLog)", returning = "responseResult")
    public void doAfterReturning(JoinPoint joinPoint, OperateLog controllerLog, ResponseEntity<?> responseResult) {
        handlerLog(joinPoint, controllerLog, null, responseResult);
    }

    /**
     * 异常后通知
     * 在带有@OperateLog注解的方法抛出异常后记录操作日志
     *
     * @param joinPoint     连接点
     * @param controllerLog 控制器日志注解
     * @param exception     异常信息
     */
    @AfterThrowing(value = "@annotation(controllerLog)", throwing = "exception")
    public void doAfterThrowing(JoinPoint joinPoint, OperateLog controllerLog, Exception exception) {
        handlerLog(joinPoint, controllerLog, exception, null);
    }

    /**
     * 处理日志
     * 根据请求信息和响应结果构建操作日志并异步保存
     *
     * @param joinPoint      连接点
     * @param controllerLog  控制器日志注解
     * @param e              异常信息，如果有的话
     * @param responseResult 响应结果，如果有的话
     */
    private void handlerLog(JoinPoint joinPoint, OperateLog controllerLog, Exception e, ResponseEntity<?> responseResult) {
        try {
            OperateLogEntity operateLogEntity = new OperateLogEntity();

            operateLogEntity.setOperateBy(SecurityUtils.getUserId());

            operateLogEntity.setOperateTime(new Date(TIME_THREADLOCAL.get()));

            operateLogEntity.setOperateIp(IpUtils.extractClientIp());

            String operateIp = operateLogEntity.getOperateIp();
            String realAddress = AddressUtils.getRealAddressByIP(operateIp);
            operateLogEntity.setOperateLocation(realAddress);

            operateLogEntity.setOperateStatus(OperateStatus.SUCCESS.name());

            operateLogEntity.setRequestUrl(ServletUtils.getRequest().getRequestURI());

            if (Objects.nonNull(e)) {
                operateLogEntity.setOperateStatus(OperateStatus.FAILED.name());

                operateLogEntity.setErrorMessage(e.getMessage());
            }

            String className = joinPoint.getTarget().getClass().getName();
            String methodName = joinPoint.getSignature().getName();
            operateLogEntity.setExecuteMethod(className + "." + methodName + "()");

            operateLogEntity.setRequestMethod(ServletUtils.getRequest().getMethod());

            handlerLogParam(joinPoint, controllerLog, operateLogEntity, responseResult);

            operateLogEntity.setResponseDuration(System.currentTimeMillis() - TIME_THREADLOCAL.get());

            AsyncManager.instance().execute(AsyncFactory.recordOperate(operateLogEntity));
        } finally {
            if (Objects.nonNull(TIME_THREADLOCAL.get())) {
                TIME_THREADLOCAL.remove();
                log.info("ThreadLocal cleared successfully");
            }
        }
    }

    /**
     * 处理日志参数
     * 设置操作日志实体的标题、操作类型、请求参数和响应结果等信息
     *
     * @param joinPoint        连接点
     * @param controllerLog    控制器日志注解
     * @param operateLogEntity 操作日志实体
     * @param responseResult   响应结果
     */
    private void handlerLogParam(
            JoinPoint joinPoint,
            OperateLog controllerLog,
            OperateLogEntity operateLogEntity,
            Object responseResult
    ) {
        log.debug("Starting to handle log parameters for method: {}", operateLogEntity.getExecuteMethod());

        operateLogEntity.setTitle(controllerLog.title());

        operateLogEntity.setOperateType(controllerLog.operateType().name());

        if (controllerLog.isSaveRequestParam()) {
            setRequestParam(joinPoint, operateLogEntity, controllerLog.excludeParamNames());
        }

        if (controllerLog.isSaveResponseResult() && Objects.nonNull(responseResult)) {
            ObjectMapper objectMapper = new ObjectMapper();
            String responseResultStr = null;
            try {
                responseResultStr = objectMapper.writeValueAsString(ResponseVo.success(responseResult));
            } catch (JsonProcessingException exception) {
                log.error("Error serializing response result. Exception: {}, Response: {}",
                        exception.getMessage(), responseResult, exception);
            }

            operateLogEntity.setResponseResult(responseResultStr);
        }

        log.debug("Finished handling log parameters for method: {}", operateLogEntity.getExecuteMethod());
    }

    /**
     * 设置请求参数
     * 根据请求方法类型和参数获取请求参数，并设置到操作日志实体中
     *
     * @param joinPoint         连接点
     * @param operateLogEntity  操作日志实体
     * @param excludeParamNames 需要排除的参数名称数组
     */
    private void setRequestParam(
            JoinPoint joinPoint,
            OperateLogEntity operateLogEntity,
            String[] excludeParamNames) {
        Map<?, ?> paramsMap = ServletUtils.getParamMap(ServletUtils.getRequest());

        String requestMethod = operateLogEntity.getRequestMethod();

        boolean isNotGetMethod = StringUtils.equalsAny(
                requestMethod,
                HttpMethod.PUT.name(),
                HttpMethod.POST.name(),
                HttpMethod.DELETE.name(),
                HttpMethod.PATCH.name()
        );
        ObjectMapper objectMapper = getWithoutSensitiveAttributeObjectMapper(excludeParamNames);
        if (MapUtils.isEmpty(paramsMap) && isNotGetMethod) {
            String params = argsArrayToString(joinPoint.getArgs(), objectMapper);
            operateLogEntity.setRequestParam(params);
        } else {
            String requestParam = null;
            try {
                requestParam = objectMapper.writeValueAsString(paramsMap);
            } catch (JsonProcessingException exception) {
                log.error("Error serializing request parameters. Exception: {}, Parameter: {}",
                        exception.getMessage(), paramsMap, exception);
            }
            operateLogEntity.setRequestParam(requestParam);
        }
    }

    /**
     * 将参数数组转换为字符串
     * 将方法参数数组转换为JSON字符串，过滤掉敏感信息
     *
     * @param paramsArray                           参数数组
     * @param withoutSensitiveAttributeObjectMapper 不包含敏感属性的ObjectMapper
     * @return 参数字符串
     */
    private String argsArrayToString(Object[] paramsArray, ObjectMapper withoutSensitiveAttributeObjectMapper) {
        if (ArrayUtils.isEmpty(paramsArray) || paramsArray.length == 0) {
            return null;
        }

        StringBuilder params = new StringBuilder();

        for (Object o : paramsArray) {
            if (Objects.nonNull(o) && !isFilterObject(o)) {
                String json;
                try {
                    json = withoutSensitiveAttributeObjectMapper.writeValueAsString(o);
                } catch (JsonProcessingException exception) {
                    log.error("Error serializing parameter: {}", o, exception);
                    continue;
                }
                params.append(json).append(" ");
            }
        }

        return params.toString().trim();
    }

    /**
     * 获取不包含敏感属性的ObjectMapper
     * 创建一个ObjectMapper，配置为不序列化指定的敏感属性
     *
     * @param excludeParamNames 需要排除的参数名称数组
     * @return 配置好的ObjectMapper
     */
    private ObjectMapper getWithoutSensitiveAttributeObjectMapper(String[] excludeParamNames) {
        ObjectMapper objectMapper = new ObjectMapper();
        String[] allExcludeParamNames = ArrayUtils.addAll(EXCLUDE_PROPERTIES, excludeParamNames);
        ObjectWriter writer = objectMapper.writer();

        for (String excludeParamName : allExcludeParamNames) {
            writer.withoutAttribute(excludeParamName);
        }

        return objectMapper;
    }

    /**
     * 判断对象是否需要过滤
     * 校验对象是否属于不应该被记录到日志中的类型
     *
     * @param o 待校验的对象
     * @return 如果对象需要被过滤则返回true，否则返回false
     */
    public boolean isFilterObject(Object o) {
        if (Objects.isNull(o)) {
            return true;
        }
        Class<?> clazz = o.getClass();

        return isArrayOfFiles(clazz) || isCollectionOfFiles(o) || isMapOfFiles(o) || isCommonExcludedType(o);
    }

    /**
     * 判断是否为文件数组
     * 校验给定的类是否为MultipartFile数组
     *
     * @param clazz 待校验的类
     * @return 如果是文件数组则返回true，否则返回false
     */
    private boolean isArrayOfFiles(Class<?> clazz) {
        return clazz.isArray() && clazz.getComponentType().isAssignableFrom(MultipartFile.class);
    }

    /**
     * 判断是否为文件列表
     * 校验给定的对象是否为包含MultipartFile的列表
     *
     * @param o 待校验的对象
     * @return 如果是文件列表则返回true，否则返回false
     */
    private boolean isCollectionOfFiles(Object o) {
        return o instanceof Collection && ((Collection<?>) o).stream().anyMatch(MultipartFile.class::isInstance);
    }

    /**
     * 判断是否为文件映射
     * 校验给定的对象是否为包含MultipartFile的Map
     *
     * @param o 待校验的对象
     * @return 如果是文件映射则返回true，否则返回false
     */
    private boolean isMapOfFiles(Object o) {
        return o instanceof Map && ((Map<?, ?>) o).values().stream().anyMatch(MultipartFile.class::isInstance);
    }

    /**
     * 判断是否为常见的需要排除的类型
     * 校验对象是否为常见的不应记录到日志中的类型，如MultipartFile、HttpServletRequest等
     *
     * @param o 待校验的对象
     * @return 如果是常见的需要排除的类型则返回true，否则返回false
     */
    private boolean isCommonExcludedType(Object o) {
        return o instanceof MultipartFile
                || o instanceof HttpServletRequest
                || o instanceof HttpServletResponse
                || o instanceof BindingResult;
    }

}
