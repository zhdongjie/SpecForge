package org.eu.originalkeen.system.user.domain.dto;

import com.fasterxml.jackson.annotation.JsonFormat;
import org.eu.originalkeen.core.constant.RegexpConstant;
import jakarta.validation.constraints.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.validator.constraints.Length;

import java.io.Serial;
import java.io.Serializable;
import java.util.Date;
import java.util.Set;

/**
 * 更新用户数据传输对象
 * 用于接收和校验更新用户的请求数据
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class UpdateUserDto implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -1120706075634712900L;

    /**
     * 用户ID
     * 要更新的用户的唯一标识
     */
    @NotNull(message = "{form.common.idIsRequired}")
    private Long id;

    /**
     * 用户名
     * 用户的登录账号，长度在2-8个字符之间
     */
    @NotBlank(message = "{form.user.usernameIsRequired}")
    @Length(min = 2, max = 8, message = "{form.user.invalidUsernameLength}")
    private String username;

    /**
     * 角色ID列表
     * 用户关联的角色ID列表
     */
    @NotEmpty(message = "{form.user.roleListIsRequired}")
    private Set<Long> roleIds;

}
