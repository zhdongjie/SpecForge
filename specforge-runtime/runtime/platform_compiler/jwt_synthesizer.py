from __future__ import annotations

from pathlib import Path

from runtime.codegen.common import write_text


class JwtSynthesizer:
    def emit(self, context: dict[str, object]) -> dict[str, object]:
        package_name = f"{context['platform_package']}.core.security.jwt"
        filter_path = context["output_root"] / "src" / "main" / "java" / Path(*package_name.split(".")) / "JwtAuthenticationFilter.java"
        provider_path = context["output_root"] / "src" / "main" / "java" / Path(*package_name.split(".")) / "JwtTokenProvider.java"
        write_text(filter_path, self._filter_source(package_name))
        write_text(provider_path, self._provider_source(package_name))
        return {"artifact_count": 2, "artifacts": [str(filter_path), str(provider_path)]}

    def _filter_source(self, package_name: str) -> str:
        return (
            f"package {package_name};\n\n"
            f"import jakarta.servlet.FilterChain;\n"
            f"import jakarta.servlet.ServletException;\n"
            f"import jakarta.servlet.http.HttpServletRequest;\n"
            f"import jakarta.servlet.http.HttpServletResponse;\n"
            f"import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;\n"
            f"import org.springframework.security.core.authority.AuthorityUtils;\n"
            f"import org.springframework.security.core.context.SecurityContextHolder;\n"
            f"import org.springframework.stereotype.Component;\n"
            f"import org.springframework.util.StringUtils;\n"
            f"import org.springframework.web.filter.OncePerRequestFilter;\n\n"
            f"import java.io.IOException;\n\n"
            f"@Component\n"
            f"public class JwtAuthenticationFilter extends OncePerRequestFilter {{\n\n"
            f"    private final JwtTokenProvider tokenProvider;\n\n"
            f"    public JwtAuthenticationFilter(JwtTokenProvider tokenProvider) {{\n"
            f"        this.tokenProvider = tokenProvider;\n"
            f"    }}\n\n"
            f"    @Override\n"
            f"    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain) throws ServletException, IOException {{\n"
            f"        String header = request.getHeader(\"Authorization\");\n"
            f"        if (StringUtils.hasText(header) && header.startsWith(\"Bearer \")) {{\n"
            f"            String token = header.substring(7);\n"
            f"            if (tokenProvider.validateToken(token)) {{\n"
            f"                String subject = tokenProvider.resolveSubject(token);\n"
            f"                UsernamePasswordAuthenticationToken authenticationToken = new UsernamePasswordAuthenticationToken(\n"
            f"                        subject,\n"
            f"                        token,\n"
            f"                        AuthorityUtils.NO_AUTHORITIES\n"
            f"                );\n"
            f"                SecurityContextHolder.getContext().setAuthentication(authenticationToken);\n"
            f"            }}\n"
            f"        }}\n"
            f"        filterChain.doFilter(request, response);\n"
            f"    }}\n"
            f"}}\n"
        )

    def _provider_source(self, package_name: str) -> str:
        return (
            f"package {package_name};\n\n"
            f"import org.springframework.beans.factory.annotation.Value;\n"
            f"import org.springframework.stereotype.Component;\n"
            f"import org.springframework.util.StringUtils;\n\n"
            f"@Component\n"
            f"public class JwtTokenProvider {{\n\n"
            f"    @Value(\"${{specforge.security.jwt.secret:specforge-secret-key}}\")\n"
            f"    private String secret;\n\n"
            f"    public String generateAccessToken(String subject) {{\n"
            f"        return subject + \".\" + secret.hashCode();\n"
            f"    }}\n\n"
            f"    public boolean validateToken(String token) {{\n"
            f"        return StringUtils.hasText(token);\n"
            f"    }}\n\n"
            f"    public String resolveSubject(String token) {{\n"
            f"        int index = token.indexOf('.');\n"
            f"        return index > 0 ? token.substring(0, index) : token;\n"
            f"    }}\n"
            f"}}\n"
        )
