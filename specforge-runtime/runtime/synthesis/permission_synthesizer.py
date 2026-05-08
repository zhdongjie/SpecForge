from __future__ import annotations

from pathlib import Path
from typing import Any

from runtime.codegen.common import write_text


class PermissionSynthesizer:
    def emit(self, context: dict[str, Any]) -> dict[str, Any]:
        package_root = context["package_root"]
        module_name = context["module_name"]
        permissions = sorted(set(context["schema"].get("permissions", [])))
        class_name = f"{module_name}PermissionConstant"
        package_name = f"{package_root}.constant"
        java_root = context["output_root"] / "src" / "main" / "java"
        destination = java_root / Path(*package_name.split(".")) / f"{class_name}.java"

        fields = "\n".join(
            f'    public static final String {self._constant_name(permission)} = "{permission}";'
            for permission in permissions
        )
        source = (
            f"package {package_name};\n\n"
            f"public final class {class_name} {{\n\n"
            f"    private {class_name}() {{\n"
            f"    }}\n\n"
            f"{fields}\n"
            f"}}\n"
        )
        write_text(destination, source)
        return {
            "artifact_count": 1,
            "artifacts": [str(destination)],
            "permission_class": class_name,
        }

    def _constant_name(self, permission: str) -> str:
        return permission.replace(":", "_").replace("-", "_").upper()
