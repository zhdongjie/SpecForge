package org.eu.originalkeen.core.utils;

import org.eu.originalkeen.core.constant.SystemConstant;
import org.eu.originalkeen.core.domain.bo.UserBo;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContext;
import org.springframework.security.core.context.SecurityContextHolder;

import java.util.Objects;

/**
 * 安全工具类
 * 提供获取当前登录用户信息和认证信息的工具方法
 */
@Slf4j
public class SecurityUtils {

    /**
     * 获取当前用户ID
     * 从当前登录用户中获取用户ID，如果是匿名用户则返回null
     *
     * @return 当前用户ID，如果是匿名用户则返回null
     */
    public static Long getUserId() {
        return isAnonymousUser() ? null : getLoginUser().getId();
    }

    /**
     * 获取当前登录用户
     * 从安全上下文中获取当前登录的用户信息
     *
     * @return 当前登录的用户信息对象
     * @throws IllegalStateException 如果当前用户未登录或主体不是UserBo类型则抛出异常
     */
    public static UserBo getLoginUser() {
        Object principal = getAuthentication().getPrincipal();
        if (principal instanceof UserBo userBo) {
            return userBo;
        }
        log.warn("Failed to retrieve login user: principal is {}", principal);
        throw new IllegalStateException("Current user is not logged in or principal is not of type UserBo");
    }

    /**
     * 判断当前用户是否为匿名用户
     * 校验当前用户是否为未登录的匿名用户
     *
     * @return 如果是匿名用户则返回true，否则返回false
     */
    public static boolean isAnonymousUser() {
        Authentication authentication = getAuthentication();
        Object principal = authentication.getPrincipal();
        if (Objects.isNull(principal)) {
            return true;
        }

        return StringUtils.equals(SystemConstant.SECURITY_ANONYMOUS_USER, String.valueOf(principal));
    }

    /**
     * 获取当前认证信息
     * 从安全上下文中获取当前的认证信息
     *
     * @return 当前的认证信息对象
     * @throws IllegalStateException 如果无法获取安全上下文或认证信息则抛出异常
     */
    public static Authentication getAuthentication() {
        SecurityContext securityContext = SecurityContextHolder.getContext();
        if (Objects.isNull(securityContext)) {
            throw new IllegalStateException("Failed to get security context");
        }
        Authentication authentication = securityContext.getAuthentication();
        if (Objects.isNull(authentication)) {
            throw new IllegalStateException("Failed to get security authentication");
        }
        return authentication;
    }

    /**
     * 私有构造函数
     * 防止实例化工具类
     */
    private SecurityUtils() {
    }

}
