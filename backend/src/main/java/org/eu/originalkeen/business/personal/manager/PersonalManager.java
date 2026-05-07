package org.eu.originalkeen.business.personal.manager;

import org.eu.originalkeen.business.personal.domain.dto.ChangePasswordDto;
import org.eu.originalkeen.business.personal.domain.vo.MeVo;
import org.eu.originalkeen.core.constant.SystemConstant;
import org.eu.originalkeen.core.domain.bo.PermissionBo;
import org.eu.originalkeen.core.domain.bo.UserBo;
import org.eu.originalkeen.core.domain.vo.ResponseVo;
import org.eu.originalkeen.core.exception.BusinessException;
import org.eu.originalkeen.core.exception.business.FieldValidationException;
import org.eu.originalkeen.core.utils.LocaleUtils;
import org.eu.originalkeen.core.utils.SecurityUtils;
import org.eu.originalkeen.system.permission.service.PermissionService;
import org.eu.originalkeen.system.role.domain.bo.RoleBo;
import org.eu.originalkeen.system.role.service.RoleService;
import org.eu.originalkeen.system.user.service.UserService;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

/**
 * 个人中心管理器
 * 提供个人中心相关的业务处理功能，整合用户服务和安全工具类等
 * <p>
 * 主要功能：
 * 1. 获取当前登录用户信息
 * 2. 修改用户密码
 * 3. 校验用户密码
 * <p>
 * 使用@Slf4j注解提供日志记录功能
 */
@Slf4j
@Component
public class PersonalManager {

    /**
     * 用户服务
     * 用于处理用户相关的操作，包括密码更新和用户信息查询
     */
    @Resource
    private UserService userService;

    /**
     * 密码编码器
     * 用于密码的加密和比较，确保密码安全性
     */
    @Resource
    private PasswordEncoder passwordEncoder;

    /**
     * 用户角色服务
     * 用于查询特定语言下的用户角色
     */
    @Resource
    private RoleService roleService;

    /**
     * 权限服务
     * 用于查询特定语言下的用户权限
     */
    @Resource
    private PermissionService permissionService;

    /**
     * Redis模板
     * 用于缓存用户信息
     */
    @Resource
    private RedisTemplate<String, UserBo> redisTemplate;

    /**
     * 获取当前登录的用户信息
     * 从安全上下文中获取当前登录用户信息，并转换为视图对象
     * 同时处理多语言加载逻辑
     *
     * @return 用户信息响应对象
     */
    @Transactional(readOnly = true)
    public ResponseVo<MeVo> me() {
        // 1. 从安全上下文中获取当前登录用户信息
        // 通过SecurityUtils工具类获取已认证的用户详情
        UserBo loginUserBo = SecurityUtils.getLoginUser();
        Long userId = loginUserBo.getId();

        // 2. 获取当前请求的语言代码
        String currentLangCode = LocaleUtils.getLangCode();

        // 3. 校验是否需要加载当前语言的角色和权限名称
        if (loginUserBo.needLoadLang(currentLangCode)) {
            // 3.1 查询该语言的角色和权限信息
            List<RoleBo> roles = roleService.selectUserRoles(userId);
            List<PermissionBo> permissions = permissionService.selectUserPermissionsForLanguage(userId);

            // 3.2 将查询结果添加到用户对象中
            loginUserBo.addLangData(currentLangCode, roles, permissions);

            // 3.3 更新Redis缓存，但不刷新过期时间
            String redisKey = SystemConstant.REDIS_PREFIX_LOGIN + userId;
            redisTemplate.opsForValue().set(
                    redisKey,
                    loginUserBo
            );
        }

        // 4. 切换到当前语言
        loginUserBo.switchToLang(currentLangCode);

        // 5. 将用户信息转换为视图对象
        // 使用工厂方法创建视图对象，仅包含需要展示的信息
        MeVo meVo = MeVo.of(loginUserBo);

        // 6. 返回成功响应，携带用户信息
        return ResponseVo.success(meVo);
    }

    /**
     * 修改登录密码
     * 校验旧密码正确性，并更新为新密码
     *
     * @param changePasswordDto 修改密码DTO
     * @return 修改结果响应对象
     * @throws BusinessException 旧密码不正确或用户不存在时抛出
     */
    @Transactional
    public ResponseVo<Void> changeLoginPassword(ChangePasswordDto changePasswordDto) {
        // 1. 获取当前登录用户ID
        // 从安全上下文中获取用户标识
        Long userId = SecurityUtils.getUserId();

        // 2. 校验旧密码是否正确
        // 比较用户输入的旧密码与数据库中存储的密码是否匹配
        boolean passwordIsCorrect = validatePasswordIsCorrect(userId, changePasswordDto.getOldPassword());

        // 3. 如果旧密码不正确，记录警告日志并抛出异常
        if (!passwordIsCorrect) {
            log.warn("Invalid old password for user [{}]", userId);
            throw new FieldValidationException("oldPassword", "business.personal.changePassword.oldPasswordError");
        }

        // 4. 加密新密码
        // 使用密码编码器对新密码进行单向加密
        String encodedNewPassword = passwordEncoder.encode(changePasswordDto.getNewPassword());

        // 5. 更新用户密码
        // 调用用户服务更新数据库中的密码记录
        userService.updatePassword(userId, encodedNewPassword);

        // 6. 返回成功响应
        return ResponseVo.success();
    }

    /**
     * 校验密码是否正确
     * 通过密码编码器比较输入密码和数据库中的加密密码
     *
     * @param userId   用户ID
     * @param password 要校验的密码
     * @return 密码是否正确
     */
    private boolean validatePasswordIsCorrect(Long userId, String password) {
        // 1. 查询用户的加密密码
        // 从数据库获取用户当前的加密密码
        String encodedPassword = selectEncodedPassword(userId);

        // 2. 使用密码编码器比较明文密码和加密密码
        // 返回比较结果，表示密码是否匹配
        return passwordEncoder.matches(password, encodedPassword);
    }

    /**
     * 查询用户的加密密码
     * 调用用户服务获取指定用户的加密密码
     *
     * @param userId 用户ID
     * @return 加密后的密码字符串
     * @throws BusinessException 当用户不存在时抛出
     */
    private String selectEncodedPassword(Long userId) {
        // 1. 调用用户服务查询加密密码
        // 根据用户ID获取数据库中存储的加密密码
        String encodedPassword = userService.selectEncodedPassword(userId);

        // 2. 校验密码是否存在
        // 如果密码为空，表示用户不存在，记录警告日志并抛出异常
        if (StringUtils.isEmpty(encodedPassword)) {
            log.warn("User [{}] not found", userId);
            throw new BusinessException("form.user.userNotFound");
        }

        // 3. 返回加密密码
        return encodedPassword;
    }

}
