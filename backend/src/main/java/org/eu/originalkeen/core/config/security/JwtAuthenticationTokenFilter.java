package org.eu.originalkeen.core.config.security;

import org.eu.originalkeen.core.config.properties.OriginalProperties;
import org.eu.originalkeen.core.constant.SystemConstant;
import org.eu.originalkeen.core.domain.bo.UserBo;
import org.eu.originalkeen.core.utils.JwtUtils;
import jakarta.annotation.Resource;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.NonNull;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.jose4j.jwt.JwtClaims;
import org.jose4j.jwt.MalformedClaimException;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.Objects;

/**
 * JWT认证令牌过滤器
 * 用于处理基于JWT的认证过程，校验请求中的JWT令牌并设置安全上下文
 */
@Slf4j
@Component
public class JwtAuthenticationTokenFilter extends OncePerRequestFilter {

    /**
     * 系统配置属性
     * 用于获取认证相关的配置信息
     */
    @Resource
    private OriginalProperties properties;

    /**
     * Redis模板
     * 用于从缓存中获取用户信息
     */
    @Resource
    private RedisTemplate<String, UserBo> redisTemplate;

    /**
     * 过滤器内部处理方法
     * 处理每个请求，校验JWT令牌并设置安全上下文
     *
     * @param request     HTTP请求
     * @param response    HTTP响应
     * @param filterChain 过滤器链
     * @throws ServletException Servlet异常
     * @throws IOException      IO异常
     */
    @Override
    protected void doFilterInternal(
            @NonNull HttpServletRequest request,
            @NonNull HttpServletResponse response,
            @NonNull FilterChain filterChain
    ) throws ServletException, IOException {
        String authenticationHeader = request.getHeader(properties.authorize().header());
        if (verifyAuthenticationHeader(authenticationHeader)) {
            String accessJwt = authenticationHeader
                    .replace(properties.authorize().prefix(), StringUtils.EMPTY);
            JwtUtils.parseAccessJwt(accessJwt, true)
                    .ifPresentOrElse(
                            this::setupAuthentication,
                            SecurityContextHolder::clearContext
                    );
        }

        filterChain.doFilter(request, response);
    }

    /**
     * 设置认证信息
     * 根据JWT令牌中的用户标识从缓存中获取用户信息并设置到安全上下文
     *
     * @param jwtClaims JWT声明对象
     */
    private void setupAuthentication(JwtClaims jwtClaims) {
        UserBo loginUserBo;
        String subject;
        try {
            subject = jwtClaims.getSubject();
            loginUserBo = redisTemplate.opsForValue().get(SystemConstant.REDIS_PREFIX_LOGIN + subject);
        } catch (MalformedClaimException exception) {
            log.error("Failed to fetch user from Redis: {}", exception.getMessage(), exception);
            SecurityContextHolder.clearContext();
            return;
        }
        if (Objects.isNull(loginUserBo)) {
            log.warn("User not found in Redis for subject: {}", subject);
            SecurityContextHolder.clearContext();
        } else {
            Authentication authentication =
                    new UsernamePasswordAuthenticationToken(loginUserBo, null, loginUserBo.getAuthorities());
            SecurityContextHolder.getContext().setAuthentication(authentication);
        }
    }

    /**
     * 校验认证头
     * 校验认证头是否存在且格式正确
     *
     * @param authenticationHeader 认证头字符串
     * @return 如果认证头有效返回true，否则返回false
     */
    private boolean verifyAuthenticationHeader(String authenticationHeader) {
        return StringUtils.isNotEmpty(authenticationHeader) &&
                authenticationHeader.startsWith(properties.authorize().prefix());
    }

}
