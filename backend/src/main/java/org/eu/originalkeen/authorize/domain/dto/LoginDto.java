package org.eu.originalkeen.authorize.domain.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;

/**
 * 登录数据传输对象
 * 用于接收和校验用户登录请求的数据
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class LoginDto implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -7452153568642728140L;

    /**
     * 用户名
     * 用户的登录账号
     */
    @NotBlank(message = "{form.user.usernameIsRequired}")
    private String username;

    /**
     * 密码
     * 用户的登录密码
     */
    @NotBlank(message = "{form.user.passwordIsRequired}")
    private String password;

}
