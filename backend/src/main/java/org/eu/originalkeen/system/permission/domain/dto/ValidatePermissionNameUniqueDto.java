package org.eu.originalkeen.system.permission.domain.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;

/**
 * 校验权限名称唯一性数据传输对象
 * 用于接收校验权限名称唯一性的请求数据
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ValidatePermissionNameUniqueDto implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = 3705998752250915806L;

    /**
     * 权限ID
     * 当前权限ID，用于更新时排除自身
     */
    private Long id;

    /**
     * 权限名称
     * 要校验的权限名称
     */
    @NotBlank(message = "{form.permission.permissionNameIsRequired}")
    private String permissionName;

}
