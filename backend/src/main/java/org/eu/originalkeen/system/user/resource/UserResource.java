package org.eu.originalkeen.system.user.resource;

import org.eu.originalkeen.core.annotation.OperateLog;
import org.eu.originalkeen.core.domain.vo.PageVo;
import org.eu.originalkeen.core.domain.vo.ResponseVo;
import org.eu.originalkeen.core.enums.OperateType;
import org.eu.originalkeen.system.user.domain.dto.CreateUserDto;
import org.eu.originalkeen.system.user.domain.dto.EnquiryUserPageDto;
import org.eu.originalkeen.system.user.domain.dto.UpdateUserDto;
import org.eu.originalkeen.system.user.domain.dto.ValidateUsernameUniqueDto;
import org.eu.originalkeen.system.user.domain.vo.UserDetailsVo;
import org.eu.originalkeen.system.user.domain.vo.UserPageVo;
import org.eu.originalkeen.system.user.manager.UserManager;
import jakarta.annotation.Resource;
import jakarta.validation.constraints.NotEmpty;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import java.util.Set;

/**
 * 用户资源控制器
 * 提供用户管理相关的REST API接口
 */
@CrossOrigin
@Validated
@RestController
@RequestMapping("/v1/system/user")
public class UserResource {

    /**
     * 用户管理器
     * 提供用户相关的业务处理功能，整合用户服务、角色服务和权限服务等
     */
    @Resource
    private UserManager userManager;

    /**
     * 校验用户名唯一性
     * 校验用户名是否已被使用
     *
     * @param validateUsernameUniqueDto 用户名校验数据传输对象
     * @return 校验结果响应实体，true表示已存在，false表示不存在
     */
    @GetMapping("/username/unique")
    @PreAuthorize("hasAuthority('system:user:validate-username')")
    public ResponseEntity<ResponseVo<Boolean>> validateUsernameUnique(
            @Validated ValidateUsernameUniqueDto validateUsernameUniqueDto
    ) {
        return ResponseEntity.ok(userManager.validateUsernameUnique(validateUsernameUniqueDto));
    }

    /**
     * 创建用户
     * 创建新的用户账号
     *
     * @param createUserDto 创建用户数据传输对象
     * @return 创建结果响应实体
     */
    @PostMapping
    @PreAuthorize("hasAuthority('system:user:create')")
    @OperateLog(title = "Create User", operateType = OperateType.INSERT)
    public ResponseEntity<ResponseVo<Void>> create(@RequestBody @Validated CreateUserDto createUserDto) {
        return ResponseEntity.ok(userManager.create(createUserDto));
    }

    /**
     * 批量删除用户
     * 删除多个用户账号
     *
     * @param userIds 要删除的用户ID列表
     * @return 删除结果响应实体
     */
    @DeleteMapping
    @PreAuthorize("hasAuthority('system:user:delete')")
    @OperateLog(title = "Batch Delete Users", operateType = OperateType.DELETE)
    public ResponseEntity<ResponseVo<Void>> batchDelete(@RequestParam("userIds") @NotEmpty(message = "{form.user.userIdListIsRequired}") Set<Long> userIds) {
        return ResponseEntity.ok(userManager.batchDelete(userIds));
    }

    /**
     * 更新用户
     * 更新用户信息
     *
     * @param updateUserDto 更新用户数据传输对象
     * @return 更新结果响应实体
     */
    @PutMapping
    @PreAuthorize("hasAuthority('system:user:update')")
    @OperateLog(title = "Update User", operateType = OperateType.UPDATE)
    public ResponseEntity<ResponseVo<Void>> update(@RequestBody @Validated UpdateUserDto updateUserDto) {
        return ResponseEntity.ok(userManager.update(updateUserDto));
    }

    /**
     * 查询用户分页
     * 分页查询用户列表
     *
     * @param enquiryUserPageDto 查询用户分页数据传输对象
     * @return 用户分页数据响应实体
     */
    @GetMapping("/page")
    @PreAuthorize("hasAuthority('system:user:page')")
    public ResponseEntity<ResponseVo<PageVo<UserPageVo>>> enquiryPage(EnquiryUserPageDto enquiryUserPageDto) {
        return ResponseEntity.ok(userManager.enquiryPage(enquiryUserPageDto));
    }

    /**
     * 查询用户详情
     * 根据ID查询用户详细信息
     *
     * @param id 用户ID
     * @return 用户详情响应实体
     */
    @GetMapping("/{id}")
    @PreAuthorize("hasAuthority('system:user:details')")
    public ResponseEntity<ResponseVo<UserDetailsVo>> enquiryDetails(@PathVariable("id") Long id) {
        return ResponseEntity.ok(userManager.enquiryDetails(id));
    }

}
