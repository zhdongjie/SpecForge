package org.eu.originalkeen.system.role.domain.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;

/**
 * 校验角色代码唯一性数据传输对象
 * 用于接收校验角色代码唯一性的请求数据
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ValidateRoleCodeUniqueDto implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = 8224568657250052712L;

    /**
     * 角色ID
     * 当前角色ID，用于更新时排除自身
     */
    private Long id;

    /**
     * 角色代码
     * 要校验的角色代码
     */
    @NotBlank(message = "{form.role.roleCodeIsRequired}")
    private String roleCode;

}
