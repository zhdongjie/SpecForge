package org.eu.originalkeen.business.personal.domain.dto;

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
 * 修改密码数据传输对象
 * 用于接收和校验用户修改密码的请求数据
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@ConfirmPasswordValidate(passwordField = "newPassword")
public class ChangePasswordDto implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -4532263551360627918L;

    /**
     * 旧密码
     * 用户当前的登录密码
     */
    @NotBlank(message = "{business.personal.changePassword.oldPasswordIsRequired}")
    private String oldPassword;

    /**
     * 新密码
     * 用户要设置的新密码，需要符合密码规则
     */
    @NotBlank(message = "{business.personal.changePassword.newPasswordIsRequired}")
    @Length(min = 8, max = 16, message = "{form.user.invalidPasswordLength}")
    @Pattern(regexp = RegexpConstant.LOGIN_PASSWORD_PATTERN, message = "{form.user.invalidPasswordFormat}")
    private String newPassword;

    /**
     * 确认密码
     * 用于确认新密码输入是否一致
     */
    @NotBlank(message = "{authorize.register.confirmPasswordIsRequired}")
    private String confirmPassword;

}
