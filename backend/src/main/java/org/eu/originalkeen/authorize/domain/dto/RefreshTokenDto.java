package org.eu.originalkeen.authorize.domain.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;

/**
 * 刷新令牌数据传输对象
 * 用于接收令牌刷新请求的数据，包含访问令牌和刷新令牌
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class RefreshTokenDto implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = 4194914994300197380L;

    /**
     * 访问令牌
     * 当前的JWT访问令牌，用于校验用户身份
     */
    @NotBlank(message = "{authorize.refreshToken.accessTokenIsRequired}")
    private String accessToken;

    /**
     * 刷新令牌
     * JWT刷新令牌，用于获取新的访问令牌和刷新令牌
     */
    @NotBlank(message = "{authorize.refreshToken.refreshTokenIsRequired}")
    private String refreshToken;

}
