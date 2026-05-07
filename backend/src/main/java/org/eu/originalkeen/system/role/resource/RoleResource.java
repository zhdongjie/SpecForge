package org.eu.originalkeen.system.role.resource;

import org.eu.originalkeen.core.annotation.OperateLog;
import org.eu.originalkeen.core.domain.vo.PageVo;
import org.eu.originalkeen.core.domain.vo.ResponseVo;
import org.eu.originalkeen.core.enums.OperateType;
import org.eu.originalkeen.system.role.domain.dto.*;
import org.eu.originalkeen.system.role.domain.vo.RoleDetailsVo;
import org.eu.originalkeen.system.role.domain.vo.RoleListVo;
import org.eu.originalkeen.system.role.domain.vo.RolePageVo;
import org.eu.originalkeen.system.role.manager.RoleManager;
import jakarta.annotation.Resource;
import jakarta.validation.constraints.NotEmpty;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Set;

/**
 * 角色资源控制器
 * 提供角色管理相关的REST API接口
 */
@CrossOrigin
@Validated
@RestController
@RequestMapping("/v1/system/role")
public class RoleResource {

    /**
     * 角色管理器
     * 提供角色相关的业务处理功能，整合角色服务、角色翻译服务和角色权限服务等
     */
    @Resource
    private RoleManager roleManager;

    /**
     * 校验角色名称唯一性
     * 校验角色名称是否已被使用
     *
     * @param validateRoleNameUniqueDto 角色名称校验数据传输对象
     * @return 校验结果响应实体，true表示已存在，false表示不存在
     */
    @GetMapping("/role-name/unique")
    @PreAuthorize("hasAuthority('system:role:validate-role-name')")
    public ResponseEntity<ResponseVo<Boolean>> validateRoleNameUnique(
            @Validated ValidateRoleNameUniqueDto validateRoleNameUniqueDto
    ) {
        return ResponseEntity.ok(roleManager.validateRoleNameUnique(validateRoleNameUniqueDto));
    }

    /**
     * 校验角色代码唯一性
     * 校验角色代码是否已被使用
     *
     * @param validateRoleCodeUniqueDto 角色代码校验数据传输对象
     * @return 校验结果响应实体，true表示已存在，false表示不存在
     */
    @GetMapping("/role-code/unique")
    @PreAuthorize("hasAuthority('system:role:validate-role-code')")
    public ResponseEntity<ResponseVo<Boolean>> validateRoleCodeUnique(
            @Validated ValidateRoleCodeUniqueDto validateRoleCodeUniqueDto
    ) {
        return ResponseEntity.ok(roleManager.validateRoleCodeUnique(validateRoleCodeUniqueDto));
    }

    /**
     * 创建角色
     * 创建新的角色
     *
     * @param createRoleDto 创建角色数据传输对象
     * @return 创建结果响应实体
     */
    @PostMapping
    @PreAuthorize("hasAuthority('system:role:create')")
    @OperateLog(title = "Create Role", operateType = OperateType.INSERT)
    public ResponseEntity<ResponseVo<Void>> create(@RequestBody @Validated CreateRoleDto createRoleDto) {
        return ResponseEntity.ok(roleManager.create(createRoleDto));
    }

    /**
     * 批量删除角色
     * 删除多个角色
     *
     * @param roleIds 要删除的角色ID列表
     * @return 删除结果响应实体
     */
    @DeleteMapping
    @PreAuthorize("hasAuthority('system:role:delete')")
    @OperateLog(title = "Batch Delete Roles", operateType = OperateType.DELETE)
    public ResponseEntity<ResponseVo<Void>> batchDelete(@RequestParam("roleIds") @NotEmpty(message = "{form.role.roleIdListIsRequired}") Set<Long> roleIds) {
        return ResponseEntity.ok(roleManager.batchDelete(roleIds));
    }

    /**
     * 更新角色
     * 更新角色信息
     *
     * @param updateRoleDto 更新角色数据传输对象
     * @return 更新结果响应实体
     */
    @PutMapping
    @PreAuthorize("hasAuthority('system:role:update')")
    @OperateLog(title = "Update Role", operateType = OperateType.UPDATE)
    public ResponseEntity<ResponseVo<Void>> update(@RequestBody @Validated UpdateRoleDto updateRoleDto) {
        return ResponseEntity.ok(roleManager.update(updateRoleDto));
    }

    /**
     * 查询角色分页
     * 分页查询角色列表
     *
     * @param enquiryRolePageDto 查询角色分页数据传输对象
     * @return 角色分页数据响应实体
     */
    @GetMapping("/page")
    @PreAuthorize("hasAuthority('system:role:page')")
    public ResponseEntity<ResponseVo<PageVo<RolePageVo>>> enquiryPage(EnquiryRolePageDto enquiryRolePageDto) {
        return ResponseEntity.ok(roleManager.enquiryPage(enquiryRolePageDto));
    }

    /**
     * 查询角色详情
     * 根据ID查询角色详细信息
     *
     * @param id 角色ID
     * @return 角色详情响应实体
     */
    @GetMapping("/{id}")
    @PreAuthorize("hasAuthority('system:role:details')")
    public ResponseEntity<ResponseVo<RoleDetailsVo>> enquiryDetails(@PathVariable("id") Long id) {
        return ResponseEntity.ok(roleManager.enquiryDetails(id));
    }

    /**
     * 查询角色列表
     * 查询所有角色的列表
     *
     * @return 角色列表响应实体
     */
    @GetMapping("/list")
    @PreAuthorize("hasAuthority('system:role:list')")
    public ResponseEntity<ResponseVo<List<RoleListVo>>> enquiryList() {
        return ResponseEntity.ok(roleManager.enquiryList());
    }

}
