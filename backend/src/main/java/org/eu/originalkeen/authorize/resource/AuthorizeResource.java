package org.eu.originalkeen.authorize.resource;

import org.eu.originalkeen.authorize.domain.dto.LoginDto;
import org.eu.originalkeen.authorize.domain.dto.RefreshTokenDto;
import org.eu.originalkeen.authorize.domain.dto.RegisterDto;
import org.eu.originalkeen.authorize.domain.vo.TokenVo;
import org.eu.originalkeen.authorize.manager.AuthorizeManager;
import org.eu.originalkeen.core.annotation.AccessLog;
import org.eu.originalkeen.core.domain.vo.ResponseVo;
import org.eu.originalkeen.core.enums.AccessType;
import org.eu.originalkeen.system.user.domain.dto.CreateUserDto;
import org.eu.originalkeen.system.user.domain.dto.ValidateUsernameUniqueDto;
import org.eu.originalkeen.system.user.manager.UserManager;
import jakarta.annotation.Resource;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

/**
 * 授权资源控制器
 * 提供用户注册、登录等授权相关的REST API接口
 */
@CrossOrigin
@RestController
@RequestMapping("/v1/authorize")
public class AuthorizeResource {

    /**
     * 授权管理器
     * 提供授权相关的业务处理功能，包括登录认证和令牌刷新
     */
    @Resource
    private AuthorizeManager authorizeManager;

    /**
     * 用户管理器
     * 提供用户相关的业务处理功能，包括用户名校验和用户创建
     */
    @Resource
    private UserManager userManager;

    /**
     * 校验用户名唯一性
     * 校验用户名是否已被使用，用于注册前的用户名可用性校验
     *
     * @param validateUsernameUniqueDto 用户名校验数据传输对象
     * @return 校验结果响应实体，true表示已存在（不可用），false表示不存在（可用）
     */
    @GetMapping("/username/unique")
    public ResponseEntity<ResponseVo<Boolean>> validateUsernameUnique(
            @Validated ValidateUsernameUniqueDto validateUsernameUniqueDto
    ) {
        return ResponseEntity.ok(userManager.validateUsernameUnique(validateUsernameUniqueDto));
    }

    /**
     * 用户注册
     * 处理新用户注册请求，创建新用户账号
     * 使用AccessLog注解记录注册操作日志
     *
     * @param registerDto 注册数据传输对象，包含用户名、密码等注册信息
     * @return 注册结果响应实体，成功时返回空内容和成功状态码
     */
    @AccessLog(AccessType.REGISTER)
    @PostMapping("/register")
    public ResponseEntity<ResponseVo<Void>> register(@RequestBody @Validated RegisterDto registerDto) {
        return ResponseEntity.ok(userManager.create(CreateUserDto.of(registerDto)));
    }

    /**
     * 用户登录
     * 处理用户登录请求，校验用户身份并返回访问令牌和刷新令牌
     * 使用AccessLog注解记录登录操作日志
     *
     * @param loginDto 登录数据传输对象，包含用户名和密码
     * @return 登录结果响应实体，成功时返回包含访问令牌和刷新令牌的TokenVo对象
     */
    @AccessLog(AccessType.LOGIN)
    @PostMapping("/login")
    public ResponseEntity<ResponseVo<TokenVo>> login(@RequestBody @Validated LoginDto loginDto) {
        return ResponseEntity.ok(authorizeManager.login(loginDto));
    }

    /**
     * 刷新令牌
     * 使用刷新令牌获取新的访问令牌和刷新令牌，延长用户会话有效期
     * 当访问令牌过期但刷新令牌仍有效时，可通过此接口获取新令牌
     *
     * @param refreshTokenDto 刷新令牌数据传输对象，包含访问令牌和刷新令牌
     * @return 刷新结果响应实体，成功时返回包含新的访问令牌和刷新令牌的TokenVo对象
     */
    @PutMapping("/refresh-token")
    public ResponseEntity<ResponseVo<TokenVo>> refreshToken(@RequestBody @Validated RefreshTokenDto refreshTokenDto) {
        return ResponseEntity.ok(authorizeManager.refreshToken(refreshTokenDto));
    }

}
