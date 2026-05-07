package org.eu.originalkeen.authorize.domain.dto;

import org.eu.originalkeen.core.annotation.validate.ConfirmPasswordValidate;
import org.eu.originalkeen.core.constant.RegexpConstant;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.validator.constraints.Length;

import java.io.Serial;
import java.io.Serializable;

/**
 * 注册数据传输对象
 * 用于接收和校验用户注册请求的数据
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@ConfirmPasswordValidate
public class RegisterDto implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = 3320667208366446510L;

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
     * 确认密码
     * 用于确认密码输入是否一致
     */
    @NotBlank(message = "{authorize.register.confirmPasswordIsRequired}")
    private String confirmPassword;

}
