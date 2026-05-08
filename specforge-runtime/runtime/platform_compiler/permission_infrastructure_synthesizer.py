from __future__ import annotations

from pathlib import Path

from runtime.codegen.common import write_text


class PermissionInfrastructureSynthesizer:
    def emit(self, context: dict[str, object]) -> dict[str, object]:
        package_name = f"{context['platform_package']}.core.security.permission"
        destination = context["output_root"] / "src" / "main" / "java" / Path(*package_name.split(".")) / "AuthorityNames.java"
        write_text(destination, self._source(package_name))
        return {"artifact_count": 1, "artifacts": [str(destination)]}

    def _source(self, package_name: str) -> str:
        return (
            f"package {package_name};\n\n"
            f"public final class AuthorityNames {{\n\n"
            f"    private AuthorityNames() {{\n"
            f"    }}\n\n"
            f"    public static String normalize(String authority) {{\n"
            f"        return authority == null ? \"\" : authority.trim();\n"
            f"    }}\n"
            f"}}\n"
        )
