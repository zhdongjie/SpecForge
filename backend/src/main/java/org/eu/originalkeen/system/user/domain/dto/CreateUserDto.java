package org.eu.originalkeen.system.user.domain.dto;

import com.fasterxml.jackson.annotation.JsonFormat;
import org.eu.originalkeen.authorize.domain.dto.RegisterDto;
import org.eu.originalkeen.core.constant.RegexpConstant;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.PastOrPresent;
import jakarta.validation.constraints.Pattern;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.validator.constraints.Length;

import java.io.Serial;
import java.io.Serializable;
import java.util.Date;
import java.util.Set;

/**
 * 创建用户数据传输对象
 * 用于接收和校验创建用户的请求数据
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class CreateUserDto implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = 8777175056345943524L;

    /**
     * 用户名
     * 用户的登录账号，长度在2-8个字符之间
     */
    @NotBlank(message = "{form.user.usernameIsRequired}")
    @Length(min = 2, max = 8, message = "{form.user.invalidUsernameLength}")
    private String username;

    /**
     * 密码
     * 用户的登录密码，长度在8-16个字符之间，需要符合密码规则
     */
    @NotBlank(message = "{form.user.passwordIsRequired}")
    @Length(min = 8, max = 16, message = "{form.user.invalidPasswordLength}")
    @Pattern(regexp = RegexpConstant.LOGIN_PASSWORD_PATTERN, message = "{form.user.invalidPasswordFormat}")
    private String password;

    /**
     * 角色ID列表
     * 用户关联的角色ID列表
     */
    @NotEmpty(message = "{form.user.roleListIsRequired}")
    private Set<Long> roleIds;

    /**
     * 从RegisterDto创建CreateUserDto实例
     * 将注册数据转换为创建用户数据
     *
     * @param registerDto 注册数据传输对象
     * @return CreateUserDto实例
     */
    public static CreateUserDto of(RegisterDto registerDto) {
        return new CreateUserDto(
                registerDto.getUsername(),
                registerDto.getPassword(),
                null
        );
    }

}
