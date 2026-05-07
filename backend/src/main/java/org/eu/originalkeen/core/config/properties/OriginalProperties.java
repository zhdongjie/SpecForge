package org.eu.originalkeen.core.config.properties;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.context.properties.bind.DefaultValue;

import java.util.Set;

/**
 * 系统配置属性类
 * 用于绑定配置文件中的 original 前缀的属性，包含授权和上传等配置
 */
@ConfigurationProperties(prefix = "original")
public record OriginalProperties(
        // 授权相关配置，包含JWT令牌、密钥和过期时间等配置
        @DefaultValue
        Authorize authorize
) {

    /**
     * 授权配置类
     * 定义与授权认证相关的配置属性
     */
    public record Authorize(

            // 授权请求头名称，用于指定包含认证令牌的HTTP请求头
            @DefaultValue("Authorization")
            String header,

            // 授权令牌前缀，用于指定认证令牌的前缀，默认为"Bearer "
            @DefaultValue("Bearer ")
            String prefix,

            // 访问令牌过期时间（分钟），访问令牌的有效期，默认为30分钟
            @DefaultValue("30")
            Integer accessTokenExpireTime,

            // 刷新令牌过期时间（分钟），刷新令牌的有效期，默认为10080分钟（7天）
            @DefaultValue("10080") Integer refreshTokenExpireTime,

            // JWK密钥目录，存放JWK密钥文件的目录，默认为".jwk"
            @DefaultValue(".jwk")
            String jwkDirectory,

            // 访问令牌公钥文件名，用于校验访问令牌的公钥文件名
            @DefaultValue("access-token-public-key.json")
            String accessTokenPublicKeyName,

            // 访问令牌私钥文件名，用于签发访问令牌的私钥文件名
            @DefaultValue("access-token-private-key.json")
            String accessTokenPrivateKeyName,

            // 刷新令牌公钥文件名，用于校验刷新令牌的公钥文件名
            @DefaultValue("refresh-token-public-key.json")
            String refreshTokenPublicKeyName,

            // 刷新令牌私钥文件名，用于签发刷新令牌的私钥文件名
            @DefaultValue("refresh-token-private-key.json")
            String refreshTokenPrivateKeyName,

            // 白名单路径，不需要进行认证的URL路径列表
            @DefaultValue("{}")
            Set<String> whiteList
    ) {
    }

}
