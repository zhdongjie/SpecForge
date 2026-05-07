package org.eu.originalkeen.authorize.domain.vo;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;

/**
 * 令牌视图对象
 * 用于返回用户登录后的访问令牌和刷新令牌
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class TokenVo implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -5106107344406811062L;

    /**
     * 访问令牌
     * 用于访问受保护资源的JWT令牌
     */
    private String accessToken;

    /**
     * 刷新令牌
     * 用于获取新的访问令牌的JWT令牌
     */
    private String refreshToken;

    /**
     * 创建TokenVo对象
     * 工厂方法，用于创建令牌视图对象
     *
     * @param accessToken  访问令牌
     * @param refreshToken 刷新令牌
     * @return TokenVo对象
     */
    public static TokenVo of(String accessToken, String refreshToken) {
        return new TokenVo(accessToken, refreshToken);
    }

}
