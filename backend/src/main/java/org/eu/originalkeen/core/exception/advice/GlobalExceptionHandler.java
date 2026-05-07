package org.eu.originalkeen.core.exception.advice;

import org.eu.originalkeen.core.domain.vo.FieldErrorVo;
import org.eu.originalkeen.core.domain.vo.ResponseVo;
import org.eu.originalkeen.core.exception.BusinessException;
import org.eu.originalkeen.core.exception.SystemException;
import org.eu.originalkeen.core.exception.business.FieldValidationException;
import org.eu.originalkeen.core.utils.MessageUtils;
import jakarta.validation.ConstraintViolationException;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.validation.FieldError;
import org.springframework.web.HttpRequestMethodNotSupportedException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.MissingServletRequestParameterException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.servlet.resource.NoResourceFoundException;

import java.io.IOException;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

/**
 * 全局异常处理器
 * 统一处理应用中的各类异常，转换为标准的响应格式
 */
@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    /**
     * 处理业务异常
     * 将业务异常转换为带有错误消息或字段错误的响应
     *
     * @param exception 业务异常
     * @return 包含错误信息的响应实体
     */
    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ResponseVo<Void>> handlerBusinessException(BusinessException exception) {
        if (exception instanceof FieldValidationException fieldValidationException) {
            return ResponseEntity.ok(
                    ResponseVo.fail(List.of(FieldErrorVo.of(fieldValidationException.getField(), Set.of(exception.getMessage()))))
            );
        }
        return ResponseEntity.ok(ResponseVo.fail(exception.getMessage()));
    }

    /**
     * 处理系统异常
     * 将系统异常转换为服务器错误响应，并记录错误日志
     *
     * @param exception 系统异常
     * @return 服务器错误响应实体
     */
    @ExceptionHandler(SystemException.class)
    public ResponseEntity<ResponseVo<Void>> handlerSystemException(SystemException exception) {
        log.error("System exception: {}", exception.getMessage(), exception);
        return ResponseEntity.ok(ResponseVo.error());
    }

    /**
     * 处理方法参数校验异常
     * 处理请求参数校验失败的异常，将校验错误转换为字段错误列表
     *
     * @param e 方法参数校验异常
     * @return 包含字段错误列表的响应实体
     */
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ResponseVo<Void>> handlerMethodArgumentNotValidException(
            MethodArgumentNotValidException e
    ) {
        List<FieldErrorVo> errors = e.getFieldErrors().stream()
                .collect(Collectors.groupingBy(
                        FieldError::getField,
                        Collectors.mapping(
                                FieldError::getDefaultMessage,
                                Collectors.toSet()
                        )
                ))
                .entrySet().stream()
                .map(entry -> new FieldErrorVo(entry.getKey(), entry.getValue()))
                .toList();
        return ResponseEntity.ok(ResponseVo.fail(errors));
    }

    /**
     * 处理约束违反异常
     * 处理请求参数约束校验失败的异常，将校验错误转换为字段错误列表
     *
     * @param exception 约束违反异常
     * @return 包含字段错误列表的响应实体
     */
    @ExceptionHandler(ConstraintViolationException.class)
    public ResponseEntity<ResponseVo<Void>> handleConstraintViolation(ConstraintViolationException exception) {
        List<FieldErrorVo> errors = exception.getConstraintViolations().stream()
                .map(violation -> {
                    String fieldPath = violation.getPropertyPath().toString();
                    String field = fieldPath.contains(".")
                            ? fieldPath.substring(fieldPath.lastIndexOf('.') + 1)
                            : fieldPath;
                    String message = violation.getMessage();
                    return new FieldErrorVo(field, Set.of(message));
                })
                .collect(Collectors.groupingBy(
                        FieldErrorVo::getField,
                        Collectors.flatMapping(
                                error -> error.getErrors().stream(),
                                Collectors.toSet()
                        )
                ))
                .entrySet().stream()
                .map(entry -> new FieldErrorVo(entry.getKey(), entry.getValue()))
                .toList();

        return ResponseEntity.ok(ResponseVo.fail(errors));
    }

    /**
     * 处理缺失请求参数异常
     * 处理请求缺少必要参数的异常
     *
     * @param exception 缺失请求参数异常
     * @return 包含错误信息的响应实体
     */
    @ExceptionHandler(MissingServletRequestParameterException.class)
    public ResponseEntity<ResponseVo<Void>> handleMissingServletRequestParameterException(
            MissingServletRequestParameterException exception) {
        log.warn("Missing servlet request parameter exception: {}", exception.getMessage());
        return ResponseEntity.ok(ResponseVo.fail(
                MessageUtils.message("common.parameterIsRequired", exception.getParameterName()))
        );
    }

    /**
     * 处理HTTP请求方法不支持异常
     * 处理请求使用了不支持的HTTP方法的异常
     *
     * @param exception HTTP请求方法不支持异常
     * @return 包含错误信息的响应实体
     */
    @ExceptionHandler(HttpRequestMethodNotSupportedException.class)
    public ResponseEntity<ResponseVo<Void>> handlerHttpRequestMethodNotSupportedException(
            HttpRequestMethodNotSupportedException exception) {
        log.warn("Http request method not supported exception: {}", exception.getMessage());
        return ResponseEntity.ok(ResponseVo.fail(MessageUtils.message(
                "common.methodNotAllowed",
                exception.getMethod()
        )));
    }

    /**
     * 处理资源未找到异常
     * 处理请求的资源不存在的异常
     *
     * @param exception 资源未找到异常
     * @return 404响应实体
     */
    @ExceptionHandler(NoResourceFoundException.class)
    public ResponseEntity<ResponseVo<Void>> handlerNoResourceFoundException(NoResourceFoundException exception) {
        log.warn("No resource found exception: {}", exception.getMessage());
        return ResponseEntity.notFound().build();
    }

    /**
     * 处理IO异常
     * 处理输入输出操作中的异常，如文件读写错误
     *
     * @param exception IO异常
     * @return 服务器错误响应实体
     */
    @ExceptionHandler(IOException.class)
    public ResponseEntity<ResponseVo<Void>> handlerIOException(IOException exception) {
        log.error("IO exception: {}", exception.getMessage(), exception);
        return ResponseEntity.ok(ResponseVo.error());
    }

    /**
     * 处理访问拒绝异常
     * 处理用户没有权限访问资源的异常
     *
     * @param exception 访问拒绝异常
     * @throws AccessDeniedException 访问拒绝异常
     */
    @ExceptionHandler(AccessDeniedException.class)
    public ResponseEntity<ResponseVo<Void>> handlerAccessDeniedException(AccessDeniedException exception) {
        log.error("Access denied exception: {}", exception.getMessage(), exception);
        throw exception;
    }

    /**
     * 处理未捕获的异常
     * 处理所有其他未特别处理的异常，作为最后的安全网
     *
     * @param exception 未捕获的异常
     * @return 服务器错误响应实体
     */
    @ExceptionHandler({RuntimeException.class, Exception.class})
    public ResponseEntity<ResponseVo<Void>> handlerException(Exception exception) {
        log.error("Unhandled exception: {}", exception.getMessage(), exception);
        return ResponseEntity.ok(ResponseVo.error());
    }

}
