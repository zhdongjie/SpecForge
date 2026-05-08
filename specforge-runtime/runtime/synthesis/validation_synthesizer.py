from __future__ import annotations

from typing import Any


class ValidationSynthesizer:
    def field_annotations(self, field: dict[str, Any], include_id: bool = False) -> list[str]:
        if field.get("primary_key") and not include_id:
            return []
        annotations: list[str] = []
        java_type = str(field.get("type", "string")).lower()
        field_name = field["name"]
        message_prefix = f"field.{field_name}"
        required = bool(field.get("required"))
        if required:
            if java_type == "string":
                annotations.append(f'@NotBlank(message = "{{{message_prefix}.required}}")')
            else:
                annotations.append(f'@NotNull(message = "{{{message_prefix}.required}}")')
        if java_type == "string" and field.get("max_length"):
            annotations.append(
                f'@Size(max = {int(field["max_length"])}, message = "{{{message_prefix}.length}}")'
            )
        if java_type == "enum" and field.get("enum_values"):
            enum_pattern = "|".join(str(value) for value in field["enum_values"])
            annotations.append(
                f'@Pattern(regexp = "^({enum_pattern})$", message = "{{{message_prefix}.enum}}")'
            )
        return annotations

    def imports(self, fields: list[dict[str, Any]], include_id: bool = False) -> list[str]:
        imports: set[str] = set()
        for field in fields:
            for annotation in self.field_annotations(field, include_id=include_id):
                if annotation.startswith("@NotBlank"):
                    imports.add("jakarta.validation.constraints.NotBlank")
                elif annotation.startswith("@NotNull"):
                    imports.add("jakarta.validation.constraints.NotNull")
                elif annotation.startswith("@Size"):
                    imports.add("jakarta.validation.constraints.Size")
                elif annotation.startswith("@Pattern"):
                    imports.add("jakarta.validation.constraints.Pattern")
        return sorted(imports)
