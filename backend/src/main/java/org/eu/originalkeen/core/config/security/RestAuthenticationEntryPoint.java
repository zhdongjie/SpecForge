package org.eu.originalkeen.core.config.security;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.eu.originalkeen.core.domain.vo.ResponseVo;
import org.eu.originalkeen.core.enums.ContentType;
import org.eu.originalkeen.core.utils.ServletUtils;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.web.AuthenticationEntryPoint;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.nio.charset.StandardCharsets;

/**
 * REST认证入口点
 * 处理未登录用户访问受保护资源的情况，返回JSON格式的未授权响应
 */
@Slf4j
@Component
public class RestAuthenticationEntryPoint implements AuthenticationEntryPoint {

    /**
     * 开始认证过程
     * 当未登录用户访问受保护资源时调用，返回JSON格式的未授权响应
     *
     * @param request   HTTP请求
     * @param response  HTTP响应
     * @param exception 认证异常
     * @throws IOException 写入响应时可能抛出的异常
     */
    @Override
    public void commence(
            HttpServletRequest request,
            HttpServletResponse response,
            AuthenticationException exception
    ) throws IOException {
        log.warn("Unauthorized access attempt: {}", request.getRequestURI());
        ObjectMapper objectMapper = new ObjectMapper();
        String result = objectMapper.writeValueAsString(ResponseVo.unauthorized());
        ServletUtils.write(response, result, ContentType.JSON, StandardCharsets.UTF_8);
    }

}
