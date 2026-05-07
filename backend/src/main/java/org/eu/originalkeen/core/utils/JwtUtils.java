package org.eu.originalkeen.core.utils;

import org.eu.originalkeen.core.config.properties.OriginalProperties;
import org.eu.originalkeen.core.exception.system.JwkGenerationException;
import org.eu.originalkeen.core.exception.system.JwtGenerationException;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.jose4j.json.JsonUtil;
import org.jose4j.jwa.AlgorithmConstraints;
import org.jose4j.jwk.JsonWebKey;
import org.jose4j.jwk.RsaJsonWebKey;
import org.jose4j.jwk.RsaJwkGenerator;
import org.jose4j.jws.AlgorithmIdentifiers;
import org.jose4j.jws.JsonWebSignature;
import org.jose4j.jwt.JwtClaims;
import org.jose4j.jwt.consumer.InvalidJwtException;
import org.jose4j.jwt.consumer.JwtConsumer;
import org.jose4j.jwt.consumer.JwtConsumerBuilder;
import org.jose4j.lang.JoseException;

import java.nio.file.Paths;
import java.security.PrivateKey;
import java.security.PublicKey;
import java.util.Objects;
import java.util.Optional;

/**
 * JWT工具类
 * 提供JWT令牌的生成、解析和密钥管理功能
 */
@Slf4j
public class JwtUtils {

    /**
     * 系统配置属性
     * 用于获取认证相关的配置信息
     */
    private static final OriginalProperties properties = SpringUtils.getBean(OriginalProperties.class);

    /**
     * 生成JWK密钥对
     * 生成访问令牌和刷新令牌的JWK密钥对文件，如果文件不存在则创建
     */
    public static void generateJwk() {
        generateJwkFiles(
                properties.authorize().refreshTokenPublicKeyName(),
                properties.authorize().refreshTokenPrivateKeyName()
        );
        generateJwkFiles(
                properties.authorize().accessTokenPublicKeyName(),
                properties.authorize().accessTokenPrivateKeyName()
        );
    }

    /**
     * 生成访问令牌
     * 使用访问令牌私钥生成JWT访问令牌，设置过期时间和主体信息
     *
     * @param subject 令牌主体（通常是用户ID）
     * @return 生成的JWT访问令牌字符串
     * @throws JwtGenerationException 生成令牌过程中发生错误时抛出
     */
    public static String generateAccessJwt(String subject) {
        return generateJwtToken(
                subject,
                properties.authorize().accessTokenExpireTime(),
                properties.authorize().accessTokenPrivateKeyName()
        );
    }

    /**
     * 生成刷新令牌
     * 使用刷新令牌私钥生成JWT刷新令牌，设置过期时间和主体信息
     *
     * @param subject 令牌主体（通常是用户ID）
     * @return 生成的JWT刷新令牌字符串
     * @throws JwtGenerationException 生成令牌过程中发生错误时抛出
     */
    public static String generateRefreshJwt(String subject) {
        return generateJwtToken(
                subject,
                properties.authorize().refreshTokenExpireTime(),
                properties.authorize().refreshTokenPrivateKeyName()
        );
    }

    /**
     * 解析访问令牌
     * 使用访问令牌公钥解析JWT访问令牌，校验签名和令牌结构
     *
     * @param accessJwt          访问令牌字符串
     * @param isVerifyExpireTime 是否校验过期时间
     * @return 解析结果，如果解析成功则返回令牌声明，否则返回空
     */
    public static Optional<JwtClaims> parseAccessJwt(String accessJwt, boolean isVerifyExpireTime) {
        return parseJwt(
                accessJwt,
                properties.authorize().accessTokenPublicKeyName(),
                isVerifyExpireTime
        );
    }

    /**
     * 解析刷新令牌
     * 使用刷新令牌公钥解析JWT刷新令牌，校验签名和令牌结构
     *
     * @param refreshJwt         刷新令牌字符串
     * @param isVerifyExpireTime 是否校验过期时间
     * @return 解析结果，如果解析成功则返回令牌声明，否则返回空
     */
    public static Optional<JwtClaims> parseRefreshJwt(String refreshJwt, boolean isVerifyExpireTime) {
        return parseJwt(
                refreshJwt,
                properties.authorize().refreshTokenPublicKeyName(),
                isVerifyExpireTime
        );
    }

    /**
     * 生成JWK密钥文件
     * 生成并保存RSA公钥和私钥文件，如果文件已存在则不覆盖
     *
     * @param publicKeyName  公钥文件名
     * @param privateKeyName 私钥文件名
     */
    private static void generateJwkFiles(String publicKeyName, String privateKeyName) {
        Jwk jwk = generateRsaJsonWebKey();

        FileUtils.writeTextToFileIfNotExists(getJwkFilePath(publicKeyName), jwk.publicKey());

        FileUtils.writeTextToFileIfNotExists(getJwkFilePath(privateKeyName), jwk.privateKey());
    }

    /**
     * 解析JWT令牌
     * 使用指定的公钥解析JWT令牌，校验签名、过期时间和必要的声明
     *
     * @param jwt                JWT令牌字符串
     * @param publicKeyName      公钥文件名
     * @param isVerifyExpireTime 是否校验过期时间
     * @return 解析结果，如果解析成功则返回令牌声明，否则返回空
     */
    private static Optional<JwtClaims> parseJwt(String jwt, String publicKeyName, boolean isVerifyExpireTime) {
        JwtConsumer jwtConsumer = new JwtConsumerBuilder()
                .setRequireExpirationTime()
                .setRequireSubject()
                .setVerificationKey(getPublicKey(publicKeyName))
                .setJwsAlgorithmConstraints(
                        AlgorithmConstraints.ConstraintType.PERMIT,
                        AlgorithmIdentifiers.RSA_USING_SHA512
                )
                .build();
        try {
            return Optional.of(jwtConsumer.processToClaims(jwt));
        } catch (InvalidJwtException exception) {
            if (exception.hasExpired() && !isVerifyExpireTime) {
                log.warn("JWT has expired (ignoring expiration check): {}", exception.getMessage());
                return Optional.of(exception.getJwtContext().getJwtClaims());
            }
            log.error("Failed to parse JWT: {}", exception.getMessage(), exception);
            return Optional.empty();
        }
    }

    /**
     * 生成JWT令牌
     * 使用指定的私钥生成JWT令牌，设置过期时间、ID和主体信息
     *
     * @param subject           令牌主体（通常是用户ID）
     * @param effectiveDuration 有效时间（分钟）
     * @param privateKeyName    私钥文件名
     * @return 生成的JWT令牌字符串
     * @throws IllegalArgumentException 如果有效时间无效则抛出异常
     * @throws JwtGenerationException   如果生成JWT过程中发生错误则抛出异常
     */
    private static String generateJwtToken(String subject, Integer effectiveDuration, String privateKeyName) {
        if (Objects.isNull(effectiveDuration) || effectiveDuration <= 0) {
            throw new IllegalArgumentException("Invalid effective duration: " + effectiveDuration);
        }

        JwtClaims claims = new JwtClaims();
        claims.setExpirationTimeMinutesInTheFuture(effectiveDuration);
        claims.setGeneratedJwtId();
        claims.setIssuedAtToNow();
        claims.setSubject(subject);

        JsonWebSignature jws = new JsonWebSignature();
        jws.setPayload(claims.toJson());
        jws.setKey(getPrivateKey(privateKeyName));
        jws.setAlgorithmHeaderValue(AlgorithmIdentifiers.RSA_USING_SHA512);

        try {
            return jws.getCompactSerialization();
        } catch (JoseException exception) {
            log.error("Failed to generate JWT: {}", exception.getMessage(), exception);
            throw new JwtGenerationException(exception.getMessage(), exception);
        }
    }

    /**
     * 获取公钥
     * 从公钥文件中读取公钥，并转换为PublicKey对象
     *
     * @param publicKeyName 公钥文件名
     * @return 公钥对象
     * @throws IllegalArgumentException 如果解析公钥过程中发生错误则抛出异常
     */
    private static PublicKey getPublicKey(String publicKeyName) {
        String jwkFilePath = getJwkFilePath(publicKeyName);
        String publicKey = FileUtils.readFileToString(jwkFilePath);

        try {
            return new RsaJsonWebKey(JsonUtil.parseJson(publicKey)).getPublicKey();
        } catch (JoseException exception) {
            log.error("Failed to parse JWK public key [{}]: {}", jwkFilePath, exception.getMessage(), exception);
            throw new IllegalArgumentException(exception.getMessage(), exception);
        }
    }

    /**
     * 获取私钥
     * 从私钥文件中读取私钥，并转换为PrivateKey对象
     *
     * @param privateKeyName 私钥文件名
     * @return 私钥对象
     * @throws IllegalArgumentException 如果解析私钥过程中发生错误则抛出异常
     */
    private static PrivateKey getPrivateKey(String privateKeyName) {
        String jwkFilePath = getJwkFilePath(privateKeyName);
        String privateKey = FileUtils.readFileToString(jwkFilePath);

        try {
            return new RsaJsonWebKey(JsonUtil.parseJson(privateKey)).getPrivateKey();
        } catch (JoseException exception) {
            log.error("Failed to parse JWK private key [{}]: {}", jwkFilePath, exception.getMessage(), exception);
            throw new IllegalArgumentException(exception.getMessage(), exception);
        }
    }

    /**
     * 生成RSA JSON Web Key
     * 生成新的RSA密钥对并转换为JSON格式，使用2048位密钥长度
     *
     * @return 包含公钥和私钥JSON字符串的Jwk对象
     * @throws JwkGenerationException 如果生成JWK过程中发生错误则抛出异常
     */
    private static Jwk generateRsaJsonWebKey() {
        final int keySize = 2048;
        try {
            RsaJsonWebKey rsaJsonWebKey = RsaJwkGenerator.generateJwk(keySize);
            return new Jwk(
                    rsaJsonWebKey.toJson(JsonWebKey.OutputControlLevel.PUBLIC_ONLY),
                    rsaJsonWebKey.toJson(JsonWebKey.OutputControlLevel.INCLUDE_PRIVATE)
            );
        } catch (JoseException exception) {
            log.error("Failed to generate {}-bit RSA JWK: {}", keySize, exception.getMessage(), exception);
            throw new JwkGenerationException(exception.getMessage(), exception);
        }
    }

    /**
     * 获取JWK文件路径
     * 根据密钥文件名生成完整的文件路径，使用系统配置的JWK目录
     *
     * @param fileName 密钥文件名
     * @return 密钥文件的完整路径
     * @throws IllegalArgumentException 如果文件名为空则抛出异常
     */
    private static String getJwkFilePath(String fileName) {
        if (StringUtils.isEmpty(fileName)) {
            throw new IllegalArgumentException("File name cannot be empty");
        }
        return Paths.get(System.getProperty("user.dir"), properties.authorize().jwkDirectory(), fileName).toString();
    }

    /**
     * JWK密钥对记录类
     * 用于存储公钥和私钥的JSON字符串，提供不可变的数据结构
     *
     * @param publicKey  公钥JSON字符串，包含RSA公钥信息
     * @param privateKey 私钥JSON字符串，包含RSA私钥信息
     */
    private record Jwk(String publicKey, String privateKey) {
    }

    /**
     * 私有构造函数
     * 防止实例化工具类，确保所有方法都是静态调用
     */
    private JwtUtils() {
    }

}
