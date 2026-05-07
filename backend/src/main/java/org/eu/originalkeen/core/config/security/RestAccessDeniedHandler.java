package org.eu.originalkeen.core.config.security;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.eu.originalkeen.core.domain.vo.ResponseVo;
import org.eu.originalkeen.core.enums.ContentType;
import org.eu.originalkeen.core.utils.ServletUtils;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.web.access.AccessDeniedHandler;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.nio.charset.StandardCharsets;

/**
 * REST访问拒绝处理器
 * 处理已经登录但没有足够权限的用户访问受保护资源的情况
 */
@Slf4j
@Component
public class RestAccessDeniedHandler implements AccessDeniedHandler {

    /**
     * 处理访问拒绝异常
     * 将访问拒绝异常转换为JSON格式的响应并返回给客户端
     *
     * @param request   HTTP请求
     * @param response  HTTP响应
     * @param exception 访问拒绝异常
     * @throws IOException 写入响应时可能抛出的异常
     */
    @Override
    public void handle(
            HttpServletRequest request,
            HttpServletResponse response,
            AccessDeniedException exception
    ) throws IOException {
        log.warn("Access denied for request: {}", request.getRequestURI());
        ObjectMapper objectMapper = new ObjectMapper();
        String result = objectMapper.writeValueAsString(ResponseVo.forbidden());
        ServletUtils.write(response, result, ContentType.JSON, StandardCharsets.UTF_8);
    }

}
