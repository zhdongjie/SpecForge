package org.eu.originalkeen.business.personal.resource;

import org.eu.originalkeen.business.personal.domain.dto.ChangePasswordDto;
import org.eu.originalkeen.business.personal.domain.vo.MeVo;
import org.eu.originalkeen.business.personal.manager.PersonalManager;
import org.eu.originalkeen.core.domain.vo.ResponseVo;
import org.eu.originalkeen.system.user.domain.dto.ValidateUsernameUniqueDto;
import org.eu.originalkeen.system.user.manager.UserManager;
import jakarta.annotation.Resource;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

/**
 * 个人中心资源控制器
 * 提供个人中心相关的REST API接口
 */
@CrossOrigin
@RestController
@RequestMapping("/v1/business/personal")
public class PersonalResource {

    /**
     * 个人中心管理器
     * 提供个人中心相关的业务处理功能，包括获取用户信息和修改密码等
     */
    @Resource
    private PersonalManager personalManager;

    /**
     * 用户管理器
     * 提供用户相关的业务处理功能，用于校验用户名唯一性
     */
    @Resource
    private UserManager userManager;

    /**
     * 校验用户名唯一性
     * 校验用户名是否已被使用
     *
     * @param validateUsernameUniqueDto 用户名校验数据传输对象
     * @return 校验结果响应实体，true表示可用，false表示已存在
     */
    @GetMapping("/username/unique")
    @PreAuthorize("hasAuthority('business:personal:validate-username')")
    public ResponseEntity<ResponseVo<Boolean>> validateUsernameUnique(
            @Validated ValidateUsernameUniqueDto validateUsernameUniqueDto
    ) {
        return ResponseEntity.ok(userManager.validateUsernameUnique(validateUsernameUniqueDto));
    }

    /**
     * 获取当前登录的用户信息
     * 通过AccessToken获取当前登录用户的详细信息
     *
     * @return 用户信息响应实体，包含用户基本信息和权限信息
     */
    @GetMapping("/me")
    @PreAuthorize("hasAuthority('business:personal:me')")
    public ResponseEntity<ResponseVo<MeVo>> me() {
        return ResponseEntity.ok(personalManager.me());
    }

    /**
     * 修改登录密码
     * 修改当前登录用户的密码，需要提供旧密码进行校验
     *
     * @param changePasswordDto 修改密码数据传输对象，包含旧密码和新密码
     * @return 修改结果响应实体
     */
    @PatchMapping("/password")
    @PreAuthorize("hasAuthority('business:personal:change-password')")
    public ResponseEntity<ResponseVo<Void>> changeLoginPassword(
            @RequestBody @Validated ChangePasswordDto changePasswordDto) {
        return ResponseEntity.ok(personalManager.changeLoginPassword(changePasswordDto));
    }

}
