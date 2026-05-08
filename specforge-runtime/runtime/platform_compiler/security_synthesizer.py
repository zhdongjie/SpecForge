from __future__ import annotations

from pathlib import Path
from typing import Any

from runtime.codegen.common import write_text


class SecuritySynthesizer:
    def emit(self, context: dict[str, Any]) -> dict[str, Any]:
        package_name = f"{context['platform_package']}.core.config"
        auth_package = f"{context['platform_package']}.core.config.security"
        config_path = context["output_root"] / "src" / "main" / "java" / Path(*package_name.split(".")) / "SecurityConfiguration.java"
        entry_point_path = context["output_root"] / "src" / "main" / "java" / Path(*auth_package.split(".")) / "RestAuthenticationEntryPoint.java"
        denied_path = context["output_root"] / "src" / "main" / "java" / Path(*auth_package.split(".")) / "RestAccessDeniedHandler.java"
        write_text(config_path, self._security_configuration(context, package_name, auth_package))
        write_text(entry_point_path, self._entry_point(auth_package))
        write_text(denied_path, self._denied_handler(auth_package))
        return {
            "artifact_count": 3,
            "artifacts": [str(config_path), str(entry_point_path), str(denied_path)],
        }

    def _security_configuration(self, context: dict[str, Any], package_name: str, auth_package: str) -> str:
        jwt_package = f"{context['platform_package']}.core.security.jwt"
        return (
            f"package {package_name};\n\n"
            f"import {auth_package}.RestAccessDeniedHandler;\n"
            f"import {auth_package}.RestAuthenticationEntryPoint;\n"
            f"import {jwt_package}.JwtAuthenticationFilter;\n"
            f"import org.springframework.context.annotation.Bean;\n"
            f"import org.springframework.context.annotation.Configuration;\n"
            f"import org.springframework.security.config.Customizer;\n"
            f"import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;\n"
            f"import org.springframework.security.config.annotation.web.builders.HttpSecurity;\n"
            f"import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;\n"
            f"import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;\n"
            f"import org.springframework.security.config.http.SessionCreationPolicy;\n"
            f"import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;\n"
            f"import org.springframework.security.crypto.password.PasswordEncoder;\n"
            f"import org.springframework.security.web.SecurityFilterChain;\n"
            f"import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;\n\n"
            f"@Configuration\n"
            f"@EnableWebSecurity\n"
            f"@EnableMethodSecurity\n"
            f"public class SecurityConfiguration {{\n\n"
            f"    @Bean\n"
            f"    public SecurityFilterChain securityFilterChain(\n"
            f"            HttpSecurity httpSecurity,\n"
            f"            JwtAuthenticationFilter jwtAuthenticationFilter,\n"
            f"            RestAuthenticationEntryPoint authenticationEntryPoint,\n"
            f"            RestAccessDeniedHandler accessDeniedHandler\n"
            f"    ) throws Exception {{\n"
            f"        httpSecurity\n"
            f"                .csrf(AbstractHttpConfigurer::disable)\n"
            f"                .cors(Customizer.withDefaults())\n"
            f"                .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))\n"
            f"                .exceptionHandling(handling -> handling\n"
            f"                        .authenticationEntryPoint(authenticationEntryPoint)\n"
            f"                        .accessDeniedHandler(accessDeniedHandler)\n"
            f"                )\n"
            f"                .authorizeHttpRequests(authorize -> authorize\n"
            f"                        .requestMatchers(\"/error\", \"/actuator/health\").permitAll()\n"
            f"                        .anyRequest().authenticated()\n"
            f"                )\n"
            f"                .addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class);\n"
            f"        return httpSecurity.build();\n"
            f"    }}\n\n"
            f"    @Bean\n"
            f"    public PasswordEncoder passwordEncoder() {{\n"
            f"        return new BCryptPasswordEncoder();\n"
            f"    }}\n"
            f"}}\n"
        )

    def _entry_point(self, package_name: str) -> str:
        return (
            f"package {package_name};\n\n"
            f"import jakarta.servlet.ServletException;\n"
            f"import jakarta.servlet.http.HttpServletRequest;\n"
            f"import jakarta.servlet.http.HttpServletResponse;\n"
            f"import org.springframework.security.core.AuthenticationException;\n"
            f"import org.springframework.security.web.AuthenticationEntryPoint;\n"
            f"import org.springframework.stereotype.Component;\n\n"
            f"import java.io.IOException;\n\n"
            f"@Component\n"
            f"public class RestAuthenticationEntryPoint implements AuthenticationEntryPoint {{\n"
            f"    @Override\n"
            f"    public void commence(HttpServletRequest request, HttpServletResponse response, AuthenticationException authException) throws IOException, ServletException {{\n"
            f"        response.sendError(HttpServletResponse.SC_UNAUTHORIZED, \"Unauthorized\");\n"
            f"    }}\n"
            f"}}\n"
        )

    def _denied_handler(self, package_name: str) -> str:
        return (
            f"package {package_name};\n\n"
            f"import jakarta.servlet.ServletException;\n"
            f"import jakarta.servlet.http.HttpServletRequest;\n"
            f"import jakarta.servlet.http.HttpServletResponse;\n"
            f"import org.springframework.security.access.AccessDeniedException;\n"
            f"import org.springframework.security.web.access.AccessDeniedHandler;\n"
            f"import org.springframework.stereotype.Component;\n\n"
            f"import java.io.IOException;\n\n"
            f"@Component\n"
            f"public class RestAccessDeniedHandler implements AccessDeniedHandler {{\n"
            f"    @Override\n"
            f"    public void handle(HttpServletRequest request, HttpServletResponse response, AccessDeniedException accessDeniedException) throws IOException, ServletException {{\n"
            f"        response.sendError(HttpServletResponse.SC_FORBIDDEN, \"Forbidden\");\n"
            f"    }}\n"
            f"}}\n"
        )
