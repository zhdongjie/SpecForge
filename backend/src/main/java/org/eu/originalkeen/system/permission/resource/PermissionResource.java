package org.eu.originalkeen.system.permission.resource;

import org.eu.originalkeen.core.annotation.OperateLog;
import org.eu.originalkeen.core.domain.vo.ResponseVo;
import org.eu.originalkeen.core.enums.OperateType;
import org.eu.originalkeen.system.permission.domain.dto.CreatePermissionDto;
import org.eu.originalkeen.system.permission.domain.dto.UpdatePermissionDto;
import org.eu.originalkeen.system.permission.domain.dto.ValidateAuthorityUniqueDto;
import org.eu.originalkeen.system.permission.domain.dto.ValidatePermissionNameUniqueDto;
import org.eu.originalkeen.system.permission.domain.vo.PermissionDetailsVo;
import org.eu.originalkeen.system.permission.domain.vo.PermissionNodeVo;
import org.eu.originalkeen.system.permission.manager.PermissionManager;
import jakarta.annotation.Resource;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 权限资源控制器
 * 提供权限管理相关的REST API接口
 */
@CrossOrigin
@RestController
@RequestMapping("/v1/system/permission")
public class PermissionResource {

    /**
     * 权限管理器
     * 提供权限相关的业务处理功能，整合权限服务、权限翻译服务和角色权限服务等
     */
    @Resource
    private PermissionManager permissionManager;

    /**
     * 校验权限名称唯一性
     * 校验权限名称是否已被使用
     *
     * @param validatePermissionNameUniqueDto 权限名称校验数据传输对象
     * @return 校验结果响应实体，true表示已存在，false表示不存在
     */
    @GetMapping("/permission-name/unique")
    @PreAuthorize("hasAuthority('system:permission:validate-permission-name')")
    public ResponseEntity<ResponseVo<Boolean>> validatePermissionNameUnique(
            @Validated ValidatePermissionNameUniqueDto validatePermissionNameUniqueDto
    ) {
        return ResponseEntity.ok(permissionManager.validatePermissionNameUnique(validatePermissionNameUniqueDto));
    }

    /**
     * 校验权限标识唯一性
     * 校验权限标识是否已被使用
     *
     * @param validateAuthorityUniqueDto 权限标识校验数据传输对象
     * @return 校验结果响应实体，true表示已存在，false表示不存在
     */
    @GetMapping("/authority/unique")
    @PreAuthorize("hasAuthority('system:permission:validate-authority')")
    public ResponseEntity<ResponseVo<Boolean>> validateAuthorityUnique(
            @Validated ValidateAuthorityUniqueDto validateAuthorityUniqueDto
    ) {
        return ResponseEntity.ok(permissionManager.validateAuthorityUnique(validateAuthorityUniqueDto));
    }

    /**
     * 创建权限
     * 创建新的权限
     *
     * @param createPermissionDto 创建权限数据传输对象
     * @return 创建结果响应实体
     */
    @PostMapping
    @PreAuthorize("hasAuthority('system:permission:create')")
    @OperateLog(title = "Create Permission", operateType = OperateType.INSERT)
    public ResponseEntity<ResponseVo<Void>> create(@RequestBody @Validated CreatePermissionDto createPermissionDto) {
        return ResponseEntity.ok(permissionManager.create(createPermissionDto));
    }

    /**
     * 删除权限节点
     * 删除指定的权限节点
     *
     * @param id 权限节点ID
     * @return 删除结果响应实体
     */
    @DeleteMapping("/node/{id}")
    @PreAuthorize("hasAuthority('system:permission:delete')")
    @OperateLog(title = "Delete Permission Node", operateType = OperateType.DELETE)
    public ResponseEntity<ResponseVo<Void>> deleteNode(@PathVariable("id") Long id) {
        return ResponseEntity.ok(permissionManager.deleteNode(id));
    }

    /**
     * 更新权限
     * 更新权限信息
     *
     * @param updatePermissionDto 更新权限数据传输对象
     * @return 更新结果响应实体
     */
    @PutMapping
    @PreAuthorize("hasAuthority('system:permission:update')")
    @OperateLog(title = "Update Permission", operateType = OperateType.UPDATE)
    public ResponseEntity<ResponseVo<Void>> update(@RequestBody @Validated UpdatePermissionDto updatePermissionDto) {
        return ResponseEntity.ok(permissionManager.update(updatePermissionDto));
    }

    /**
     * 查询权限详情
     * 根据ID查询权限详细信息
     *
     * @param id 权限ID
     * @return 权限详情响应实体
     */
    @GetMapping("/{id}")
    @PreAuthorize("hasAuthority('system:permission:details')")
    public ResponseEntity<ResponseVo<PermissionDetailsVo>> enquiryDetails(@PathVariable("id") Long id) {
        return ResponseEntity.ok(permissionManager.enquiryDetails(id));
    }

    /**
     * 查询权限树
     * 查询权限的树形结构
     *
     * @return 权限树响应实体
     */
    @GetMapping("/tree")
    @PreAuthorize("hasAuthority('system:permission:tree')")
    public ResponseEntity<ResponseVo<List<PermissionNodeVo>>> enquiryTree() {
        return ResponseEntity.ok(permissionManager.enquiryTree());
    }

}
