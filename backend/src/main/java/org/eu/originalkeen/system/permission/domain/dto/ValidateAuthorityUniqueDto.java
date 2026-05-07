package org.eu.originalkeen.system.permission.domain.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;

/**
 * 校验权限标识唯一性数据传输对象
 * 用于接收校验权限标识唯一性的请求数据
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ValidateAuthorityUniqueDto implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -4294902643668724621L;

    /**
     * 权限ID
     * 当前权限ID，用于更新时排除自身
     */
    private Long id;

    /**
     * 权限标识
     * 要校验的权限标识字符串
     */
    @NotBlank(message = "{form.permission.authorityIsRequired}")
    private String authority;

}
