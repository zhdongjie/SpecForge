package org.eu.originalkeen.core.config;

import org.eu.originalkeen.core.config.properties.OriginalProperties;
import org.eu.originalkeen.core.config.security.JwtAuthenticationTokenFilter;
import org.eu.originalkeen.core.config.security.RestAccessDeniedHandler;
import org.eu.originalkeen.core.config.security.RestAuthenticationEntryPoint;
import jakarta.annotation.Resource;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.argon2.Argon2PasswordEncoder;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.DelegatingPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.crypto.password.Pbkdf2PasswordEncoder;
import org.springframework.security.crypto.scrypt.SCryptPasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

import java.util.Map;

/**
 * Spring Security配置类
 * 负责配置应用的安全认证和授权相关的功能
 */
@Configuration
@EnableWebSecurity
@EnableMethodSecurity
public class SecurityConfiguration {

    /**
     * 未认证处理器
     * 处理未登录用户访问受保护资源的情况
     */
    @Resource
    private RestAuthenticationEntryPoint restAuthenticationEntryPoint;

    /**
     * 访问拒绝处理器
     * 处理已登录但没有权限的用户访问受保护资源的情况
     */
    @Resource
    private RestAccessDeniedHandler restAccessDeniedHandler;

    /**
     * 系统配置属性
     * 用于获取认证相关的配置信息
     */
    @Resource
    private OriginalProperties originalProperties;

    /**
     * JWT认证过滤器
     * 用于处理JWT令牌的认证
     */
    @Resource
    private JwtAuthenticationTokenFilter jwtAuthenticationTokenFilter;

    /**
     * 安全过滤链配置
     * 配置应用的安全过滤链，包括访问控制、认证、会话管理等
     *
     * @param http HttpSecurity对象
     * @return 配置好的SecurityFilterChain
     * @throws Exception 配置过程中的异常
     */
    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        return http
                .authorizeHttpRequests(configurer -> configurer
                        .requestMatchers(originalProperties
                                .authorize()
                                .whiteList()
                                .toArray(new String[0])
                        ).permitAll()
                        .anyRequest().authenticated()
                )
                .addFilterAt(
                        jwtAuthenticationTokenFilter,
                        UsernamePasswordAuthenticationFilter.class
                )
                .exceptionHandling(configurer -> configurer
                        .authenticationEntryPoint(restAuthenticationEntryPoint)
                        .accessDeniedHandler(restAccessDeniedHandler))
                .sessionManagement(configurer -> configurer
                        .sessionCreationPolicy(SessionCreationPolicy.STATELESS)
                )
                .cors(Customizer.withDefaults())
                .formLogin(AbstractHttpConfigurer::disable)
                .logout(AbstractHttpConfigurer::disable)
                .httpBasic(AbstractHttpConfigurer::disable)
                .csrf(AbstractHttpConfigurer::disable)
                .build();
    }

    /**
     * 密码编码器配置
     * 配置密码的加密方式，使用委托模式支持多种加密算法
     *
     * @return 密码编码器
     */
    @Bean
    public PasswordEncoder passwordEncoder() {
        String idForEncode = "pbkdf2";
        Map<String, PasswordEncoder> encoders = Map.of(
                "bcrypt", new BCryptPasswordEncoder(),
                "pbkdf2", Pbkdf2PasswordEncoder.defaultsForSpringSecurity_v5_8(),
                "scrypt", SCryptPasswordEncoder.defaultsForSpringSecurity_v5_8(),
                "argon2", Argon2PasswordEncoder.defaultsForSpringSecurity_v5_8()
        );

        return new DelegatingPasswordEncoder(idForEncode, encoders);
    }

    /**
     * 认证管理器配置
     * 提供认证管理器实例，用于处理用户认证
     *
     * @param authenticationConfiguration 认证配置
     * @return 认证管理器
     * @throws Exception 获取认证管理器时的异常
     */
    @Bean
    public AuthenticationManager authenticationManager(
            AuthenticationConfiguration authenticationConfiguration) throws Exception {
        return authenticationConfiguration.getAuthenticationManager();
    }

}
