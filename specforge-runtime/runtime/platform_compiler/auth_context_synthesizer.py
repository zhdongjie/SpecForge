from __future__ import annotations

from pathlib import Path

from runtime.codegen.common import write_text


class AuthContextSynthesizer:
    def emit(self, context: dict[str, object]) -> dict[str, object]:
        package_name = f"{context['platform_package']}.core.security"
        destination = context["output_root"] / "src" / "main" / "java" / Path(*package_name.split(".")) / "AuthContext.java"
        write_text(destination, self._source(package_name))
        return {"artifact_count": 1, "artifacts": [str(destination)]}

    def _source(self, package_name: str) -> str:
        return (
            f"package {package_name};\n\n"
            f"import org.springframework.security.core.Authentication;\n"
            f"import org.springframework.security.core.context.SecurityContextHolder;\n\n"
            f"public final class AuthContext {{\n\n"
            f"    private AuthContext() {{\n"
            f"    }}\n\n"
            f"    public static String currentPrincipal() {{\n"
            f"        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();\n"
            f"        if (authentication == null || authentication.getPrincipal() == null) {{\n"
            f"            return \"anonymous\";\n"
            f"        }}\n"
            f"        return String.valueOf(authentication.getPrincipal());\n"
            f"    }}\n"
            f"}}\n"
        )
