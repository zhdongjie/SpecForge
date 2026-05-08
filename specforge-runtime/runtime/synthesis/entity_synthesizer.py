from __future__ import annotations

from pathlib import Path
from typing import Any

from runtime.codegen.common import write_text


class EntitySynthesizer:
    def emit(self, context: dict[str, Any]) -> dict[str, Any]:
        artifacts: list[str] = []
        for entity_name, entity_spec in sorted(context["schema"].get("entities", {}).items()):
            source = self._build_entity_source(context, entity_name, entity_spec)
            package_name = f"{context['package_root']}.domain.entity"
            destination = (
                context["output_root"]
                / "src"
                / "main"
                / "java"
                / Path(*package_name.split("."))
                / f"{entity_name}.java"
            )
            write_text(destination, source)
            artifacts.append(str(destination))
        return {"artifact_count": len(artifacts), "artifacts": artifacts}

    def _build_entity_source(self, context: dict[str, Any], entity_name: str, entity_spec: dict[str, Any]) -> str:
        field_type_system = context["field_type_system"]
        imports = {
            "com.mybatisflex.annotation.Table",
            "org.eu.originalkeen.core.domain.entity.PrimaryKeyEntity",
            f"{context['package_root']}.domain.dto.Create{entity_name}Dto",
            f"{context['package_root']}.domain.dto.Update{entity_name}Dto",
            "lombok.AllArgsConstructor",
            "lombok.Data",
            "lombok.EqualsAndHashCode",
            "lombok.NoArgsConstructor",
            "java.io.Serial",
            "java.io.Serializable",
            "java.util.Date",
        }
        field_lines: list[str] = []
        for field in entity_spec.get("fields", []):
            if field.get("primary_key"):
                continue
            definition = field_type_system.resolve(field)
            imports.update(definition.imports)
            field_lines.append(f"    private {definition.java_type} {field['name']};")

        audit_fields = [
            ("Date", "createdTime"),
            ("Long", "createdBy"),
            ("Date", "lastModifiedTime"),
            ("Long", "lastModifiedBy"),
            ("Boolean", "deleted"),
        ]
        for java_type, field_name in audit_fields:
            field_lines.append(f"    private {java_type} {field_name};")

        create_method_args = ",\n                ".join(f"createDto.get{field['name'][:1].upper() + field['name'][1:]}()" for field in entity_spec.get("fields", []) if not field.get("primary_key"))
        update_method_args = ",\n                ".join(f"updateDto.get{field['name'][:1].upper() + field['name'][1:]}()" for field in entity_spec.get("fields", []) if not field.get("primary_key"))
        imports_text = "\n".join(f"import {value};" for value in sorted(imports))
        field_text = "\n\n".join(field_lines)
        return (
            f"package {context['package_root']}.domain.entity;\n\n"
            f"{imports_text}\n\n"
            f"@Data\n"
            f"@NoArgsConstructor\n"
            f"@AllArgsConstructor\n"
            f'@Table("{entity_spec["table"]}")\n'
            f"@EqualsAndHashCode(callSuper = true)\n"
            f"public class {entity_name} extends PrimaryKeyEntity implements Serializable {{\n\n"
            f"    @Serial\n"
            f"    private static final long serialVersionUID = 1L;\n\n"
            f"{field_text}\n\n"
            f"    public static {entity_name} of(Create{entity_name}Dto createDto) {{\n"
            f"        return new {entity_name}(\n"
            f"                {create_method_args},\n"
            f"                null,\n"
            f"                null,\n"
            f"                null,\n"
            f"                null,\n"
            f"                Boolean.FALSE\n"
            f"        );\n"
            f"    }}\n\n"
            f"    public static {entity_name} of(Update{entity_name}Dto updateDto) {{\n"
            f"        {entity_name} entity = new {entity_name}(\n"
            f"                {update_method_args},\n"
            f"                null,\n"
            f"                null,\n"
            f"                null,\n"
            f"                null,\n"
            f"                Boolean.FALSE\n"
            f"        );\n"
            f"        entity.setId(updateDto.getId());\n"
            f"        return entity;\n"
            f"    }}\n"
            f"}}\n"
        )
