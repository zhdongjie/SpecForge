package org.eu.originalkeen.authorize.manager;

import org.eu.originalkeen.authorize.domain.dto.LoginDto;
import org.eu.originalkeen.authorize.domain.dto.RefreshTokenDto;
import org.eu.originalkeen.authorize.domain.vo.TokenVo;
import org.eu.originalkeen.core.config.properties.OriginalProperties;
import org.eu.originalkeen.core.constant.SystemConstant;
import org.eu.originalkeen.core.domain.bo.UserBo;
import org.eu.originalkeen.core.domain.vo.ResponseVo;
import org.eu.originalkeen.core.exception.BusinessException;
import org.eu.originalkeen.core.exception.business.FieldValidationException;
import org.eu.originalkeen.core.utils.JwtUtils;
import org.eu.originalkeen.core.utils.LocaleUtils;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.jose4j.jwt.JwtClaims;
import org.jose4j.jwt.MalformedClaimException;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import java.util.concurrent.TimeUnit;

/**
 * 授权管理器
 * 负责处理用户认证和令牌管理相关的业务逻辑
 * <p>
 * 主要功能：
 * 1. 用户登录认证
 * 2. 令牌生成和刷新
 * 3. 用户信息缓存管理
 */
@Slf4j
@Component
public class AuthorizeManager {

    /**
     * Spring Security认证管理器
     * 用于处理用户认证
     */
    @Resource
    private AuthenticationManager authenticationManager;

    /**
     * Redis模板
     * 用于缓存用户登录信息
     */
    @Resource
    private RedisTemplate<String, UserBo> redisTemplate;

    /**
     * 系统配置属性
     * 用于获取认证相关的配置信息
     */
    @Resource
    private OriginalProperties properties;

    /**
     * 用户登录实现
     * 1. 调用Spring Security进行认证
     * 2. 将用户信息存入Redis
     * 3. 生成访问令牌和刷新令牌
     *
     * @param loginDto 登录信息
     * @return 登录结果，包含令牌信息
     * @throws BusinessException 用户名或密码错误时抛出
     */
    @Transactional(readOnly = true)
    public ResponseVo<TokenVo> login(LoginDto loginDto) {
        Authentication authentication;
        String username = loginDto.getUsername();
        String password = loginDto.getPassword();
        try {
            // 1. 创建认证令牌
            //    使用用户名和密码创建未认证的认证令牌
            UsernamePasswordAuthenticationToken authenticationToken =
                    new UsernamePasswordAuthenticationToken(username, password);

            // 2. 设置安全上下文
            // 将认证令牌设置到当前线程的安全上下文中
            SecurityContextHolder.getContext().setAuthentication(authenticationToken);

            // 3. 执行认证
            //    调用认证管理器执行实际的认证过程，包括用户查询和密码校验
            //    如果认证失败，将抛出BadCredentialsException异常
            authentication = authenticationManager.authenticate(authenticationToken);
        } catch (BadCredentialsException exception) {
            // 4. 处理认证失败
            //    记录认证失败日志，并抛出字段校验异常
            log.warn("Invalid login attempt for user [{}]", username, exception);
            throw new FieldValidationException("password", "authorize.login.usernameOrPasswordError");
        } finally {
            // 5. 清理安全上下文
            //    无论认证成功还是失败，都清理当前线程的安全上下文
            SecurityContextHolder.clearContext();
        }

        // 6. 获取认证用户信息
        //    从认证结果中获取用户业务对象
        UserBo loginUserBo = (UserBo) authentication.getPrincipal();

        // 6.1 获取当前语言代码，初始化多语言缓存
        String currentLangCode = LocaleUtils.getLangCode();
        loginUserBo.addLangData(
                currentLangCode,
                loginUserBo.getRoles(),
                loginUserBo.getPermissions()
        );

        // 7. 缓存用户信息到Redis
        //    使用用户ID作为键，将用户信息存入Redis
        //    过期时间设置为配置的刷新令牌过期时间
        redisTemplate.opsForValue().set(
                // 键: 登录前缀 + 用户ID
                SystemConstant.REDIS_PREFIX_LOGIN + loginUserBo.getId(),
                // 值: 用户业务对象
                loginUserBo,
                // 过期时间: 刷新令牌过期时间
                properties.authorize().refreshTokenExpireTime(),
                // 时间单位: 分钟
                TimeUnit.MINUTES
        );

        // 8. 生成令牌
        //    使用用户ID生成访问令牌和刷新令牌
        TokenVo tokenVo = TokenVo.of(
                // 生成访问令牌，主体为用户ID
                JwtUtils.generateAccessJwt(String.valueOf(loginUserBo.getId())),
                // 生成刷新令牌，主体为用户ID
                JwtUtils.generateRefreshJwt(String.valueOf(loginUserBo.getId()))
        );

        // 10. 记录登录成功日志
        log.info("User [{}] login successful", loginUserBo.getUsername());

        // 11. 返回登录结果
        //     包装令牌信息到响应对象
        return ResponseVo.success(tokenVo);
    }

    /**
     * 刷新令牌实现
     * 1. 解析并校验访问令牌和刷新令牌
     * 2. 校验两个令牌的主体一致性
     * 3. 更新Redis中用户的过期时间
     * 4. 生成新的访问令牌和刷新令牌
     *
     * @param refreshTokenDto 刷新令牌请求DTO，包含访问令牌和刷新令牌
     * @return 刷新结果响应对象，包含新的令牌信息
     * @throws BusinessException 当令牌解析失败、校验失败或主体不一致时抛出
     */
    @Transactional(readOnly = true)
    public ResponseVo<TokenVo> refreshToken(RefreshTokenDto refreshTokenDto) {
        // 定义令牌刷新失败的错误消息键
        String tokenRefreshFailedMessage = "authorize.refreshToken.tokenRefreshFailed";

        // 1. 解析并校验访问令牌
        //    注意：这里不要求访问令牌必须有效（参数false），因为可能是因为访问令牌过期才需要刷新
        JwtClaims payloadAccessToken = JwtUtils
                .parseAccessJwt(refreshTokenDto.getAccessToken(), false)
                .orElseThrow(() -> {
                    // 访问令牌解析失败，记录警告日志并抛出业务异常
                    log.warn("Failed to parse access token during refresh token attempt");
                    return new BusinessException(tokenRefreshFailedMessage);
                });

        // 2. 解析并校验刷新令牌
        //    刷新令牌必须有效（参数true），否则无法刷新
        JwtClaims payloadRefreshToken = JwtUtils
                .parseRefreshJwt(refreshTokenDto.getRefreshToken(), true)
                .orElseThrow(() -> {
                    // 刷新令牌解析失败或已过期，记录警告日志并抛出业务异常
                    log.warn("Failed to parse refresh token during refresh token attempt");
                    return new BusinessException(tokenRefreshFailedMessage);
                });

        String accessTokenSubject;
        String refreshTokenSubject;
        try {
            // 3. 提取令牌主体
            //    从两个令牌中提取主体（用户ID）
            accessTokenSubject = payloadAccessToken.getSubject();
            refreshTokenSubject = payloadRefreshToken.getSubject();

            // 4. 校验令牌主体一致性
            //    确保两个令牌属于同一用户
            if (!StringUtils.equals(accessTokenSubject, refreshTokenSubject)) {
                // 主体不一致，记录警告日志并抛出业务异常
                log.warn("Token subject mismatch: access token subject [{}], refresh token subject [{}]",
                        accessTokenSubject, refreshTokenSubject);
                throw new BusinessException(tokenRefreshFailedMessage);
            }

            // 5. 更新Redis中用户信息的过期时间
            //    延长用户登录状态的有效期
            redisTemplate
                    .expire(
                            // 键: 登录前缀 + 用户ID
                            SystemConstant.REDIS_PREFIX_LOGIN + accessTokenSubject,
                            // 过期时间: 刷新令牌过期时间
                            properties.authorize().refreshTokenExpireTime(),
                            // 时间单位: 分钟
                            TimeUnit.MINUTES
                    );
        } catch (MalformedClaimException exception) {
            // 6. 处理令牌主体提取异常
            //    令牌格式错误，无法提取主体
            log.error("Failed to extract subject from token: {}", exception.getMessage(), exception);
            throw new BusinessException(tokenRefreshFailedMessage);
        }

        // 7. 生成新的令牌
        //    使用相同的用户ID生成新的访问令牌和刷新令牌
        TokenVo tokenVo = TokenVo.of(
                // 生成新的访问令牌
                JwtUtils.generateAccessJwt(accessTokenSubject),
                // 生成新的刷新令牌
                JwtUtils.generateRefreshJwt(refreshTokenSubject)
        );

        // 9. 记录令牌刷新成功日志
        log.info("Token refresh successful for user [{}]", accessTokenSubject);

        // 9. 返回刷新结果
        //    包装新的令牌信息到响应对象
        return ResponseVo.success(tokenVo);
    }

}
