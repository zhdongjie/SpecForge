package org.eu.originalkeen.system.permission.domain.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.validator.constraints.Length;

import java.io.Serial;
import java.io.Serializable;

/**
 * 权限翻译数据传输对象
 * 用于接收权限翻译的请求数据
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class PermissionTranslationDto implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = 4022477034586184788L;

    /**
     * 语言代码
     * 翻译的语言代码，对应 system_language_code 字典数据
     */
    @NotBlank(message = "{form.common.languageCodeIsRequired}")
    private String languageCode;

    /**
     * 权限名称
     * 权限在不同语言下的名称
     */
    @NotBlank(message = "{form.permission.permissionNameIsRequired}")
    @Length(max = 64, message = "{form.permission.invalidPermissionNameLength}")
    private String permissionName;

}
