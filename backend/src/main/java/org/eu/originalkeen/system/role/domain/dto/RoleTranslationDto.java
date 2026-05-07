package org.eu.originalkeen.system.role.domain.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.validator.constraints.Length;

import java.io.Serial;
import java.io.Serializable;

/**
 * 角色翻译数据传输对象
 * 用于接收角色翻译的请求数据
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class RoleTranslationDto implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = 3369290908914463501L;

    /**
     * 语言代码
     * 翻译的语言代码，对应 system_language_code 字典数据
     */
    @NotBlank(message = "{form.common.languageCodeIsRequired}")
    private String languageCode;

    /**
     * 角色名称
     * 角色在不同语言下的名称
     */
    @NotBlank(message = "{form.role.roleNameIsRequired}")
    @Length(max = 64, message = "{form.role.invalidRoleNameLength}")
    private String roleName;

    /**
     * 备注信息
     * 角色的备注说明
     */
    @Length(max = 300, message = "{form.common.invalidRemarkLength}")
    private String remark;

}
