package org.eu.originalkeen.system.role.domain.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;

/**
 * 校验角色名称唯一性数据传输对象
 * 用于接收校验角色名称唯一性的请求数据
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ValidateRoleNameUniqueDto implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -7211728294862833543L;

    /**
     * 角色ID
     * 当前角色ID，用于更新时排除自身
     */
    private Long id;

    /**
     * 角色名称
     * 要校验的角色名称
     */
    @NotBlank(message = "{form.role.roleNameIsRequired}")
    private String roleName;

}
