from __future__ import annotations

from pathlib import Path
from typing import Any

from runtime.codegen.common import write_text


class DtoSynthesizer:
    def emit(self, context: dict[str, Any]) -> dict[str, Any]:
        artifacts: list[str] = []
        for entity_name, entity_spec in sorted(context["schema"].get("entities", {}).items()):
            artifacts.extend(self._emit_entity_dtos(context, entity_name, entity_spec))
        return {"artifact_count": len(artifacts), "artifacts": artifacts}

    def _emit_entity_dtos(self, context: dict[str, Any], entity_name: str, entity_spec: dict[str, Any]) -> list[str]:
        artifacts: list[str] = []
        artifacts.append(self._write(context, f"Create{entity_name}Dto", "domain.dto", self._create_or_update_dto(context, entity_name, entity_spec, False)))
        artifacts.append(self._write(context, f"Update{entity_name}Dto", "domain.dto", self._create_or_update_dto(context, entity_name, entity_spec, True)))
        artifacts.append(self._write(context, f"Enquiry{entity_name}PageDto", "domain.dto", self._query_dto(context, entity_name, entity_spec)))
        artifacts.append(self._write(context, f"{entity_name}PageVo", "domain.vo", self._vo_source(context, entity_name, entity_spec, "PageVo")))
        artifacts.append(self._write(context, f"{entity_name}ListVo", "domain.vo", self._vo_source(context, entity_name, entity_spec, "ListVo")))
        artifacts.append(self._write(context, f"{entity_name}DetailsVo", "domain.vo", self._details_vo_source(context, entity_name, entity_spec)))
        return artifacts

    def _create_or_update_dto(self, context: dict[str, Any], entity_name: str, entity_spec: dict[str, Any], include_id: bool) -> str:
        type_system = context["field_type_system"]
        validator = context["validation_synthesizer"]
        imports = {
            "lombok.Data",
            "lombok.NoArgsConstructor",
            "java.io.Serial",
            "java.io.Serializable",
        }
        fields: list[str] = []
        source_name = f'{"Update" if include_id else "Create"}{entity_name}Dto'
        working_fields = list(entity_spec.get("fields", []))
        if include_id:
            imports.add("jakarta.validation.constraints.NotNull")
            fields.append('    @NotNull(message = "{field.id.required}")')
            fields.append("    private Long id;")
        for field in working_fields:
            if field.get("primary_key"):
                continue
            definition = type_system.resolve(field)
            imports.update(definition.imports)
            imports.update(validator.imports([field]))
            for annotation in validator.field_annotations(field):
                fields.append(f"    {annotation}")
            fields.append(f"    private {definition.java_type} {field['name']};")
        all_args_import = '\nimport lombok.AllArgsConstructor;' if fields else ""
        all_args_annotation = "@AllArgsConstructor\n" if fields else ""
        imports_text = "\n".join(f"import {value};" for value in sorted(imports))
        field_text = "\n\n".join(fields)
        return (
            f"package {context['package_root']}.domain.dto;\n\n"
            f"{imports_text}{all_args_import}\n\n"
            f"@Data\n"
            f"@NoArgsConstructor\n"
            f"{all_args_annotation}"
            f"public class {source_name} implements Serializable {{\n\n"
            f"    @Serial\n"
            f"    private static final long serialVersionUID = 1L;\n\n"
            f"{field_text}\n"
            f"}}\n"
        )

    def _query_dto(self, context: dict[str, Any], entity_name: str, entity_spec: dict[str, Any]) -> str:
        type_system = context["field_type_system"]
        imports = {
            "org.eu.originalkeen.core.domain.dto.EnquiryPageDto",
            "lombok.Data",
            "lombok.EqualsAndHashCode",
            "lombok.NoArgsConstructor",
            "java.io.Serial",
            "java.io.Serializable",
        }
        fields: list[str] = []
        for field in entity_spec.get("fields", []):
            if field.get("primary_key"):
                continue
            if field.get("unique") or field["name"] in {"status", "remark"} or field["name"].endswith("Name"):
                definition = type_system.resolve(field)
                imports.update(definition.imports)
                fields.append(f"    private {definition.java_type} {field['name']};")
        all_args_import = '\nimport lombok.AllArgsConstructor;' if fields else ""
        all_args_annotation = "@AllArgsConstructor\n" if fields else ""
        imports_text = "\n".join(f"import {value};" for value in sorted(imports))
        field_text = "\n\n".join(fields)
        return (
            f"package {context['package_root']}.domain.dto;\n\n"
            f"{imports_text}{all_args_import}\n\n"
            f"@Data\n"
            f"@NoArgsConstructor\n"
            f"{all_args_annotation}"
            f"@EqualsAndHashCode(callSuper = true)\n"
            f"public class Enquiry{entity_name}PageDto extends EnquiryPageDto implements Serializable {{\n\n"
            f"    @Serial\n"
            f"    private static final long serialVersionUID = 1L;\n\n"
            f"{field_text}\n"
            f"}}\n"
        )

    def _vo_source(self, context: dict[str, Any], entity_name: str, entity_spec: dict[str, Any], suffix: str) -> str:
        type_system = context["field_type_system"]
        imports = {
            f"{context['package_root']}.domain.entity.{entity_name}",
            "lombok.Data",
            "lombok.NoArgsConstructor",
            "java.io.Serial",
            "java.io.Serializable",
        }
        fields: list[str] = []
        setters: list[str] = []
        for field in entity_spec.get("fields", []):
            definition = type_system.resolve(field)
            imports.update(definition.imports)
            fields.append(f"    private {definition.java_type} {field['name']};")
        imports_text = "\n".join(f"import {value};" for value in sorted(imports))
        field_text = "\n\n".join(fields)
        class_name = f"{entity_name}{suffix}"
        all_args_import = '\nimport lombok.AllArgsConstructor;' if fields else ""
        all_args_annotation = "@AllArgsConstructor\n" if fields else ""
        for field in entity_spec.get("fields", []):
            setter_name = field["name"][:1].upper() + field["name"][1:]
            setters.append(f"        vo.set{setter_name}(entity.get{setter_name}());")
        setters_text = "\n".join(setters)
        return (
            f"package {context['package_root']}.domain.vo;\n\n"
            f"{imports_text}{all_args_import}\n\n"
            f"@Data\n"
            f"@NoArgsConstructor\n"
            f"{all_args_annotation}"
            f"public class {class_name} implements Serializable {{\n\n"
            f"    @Serial\n"
            f"    private static final long serialVersionUID = 1L;\n\n"
            f"{field_text}\n\n"
            f"    public static {class_name} fromEntity({entity_name} entity) {{\n"
            f"        if (entity == null) {{\n"
            f"            return null;\n"
            f"        }}\n"
            f"        {class_name} vo = new {class_name}();\n"
            f"{setters_text}\n"
            f"        return vo;\n"
            f"    }}\n"
            f"}}\n"
        )

    def _details_vo_source(self, context: dict[str, Any], entity_name: str, entity_spec: dict[str, Any]) -> str:
        type_system = context["field_type_system"]
        imports = {
            f"{context['package_root']}.domain.entity.{entity_name}",
            "lombok.Data",
            "lombok.NoArgsConstructor",
            "java.io.Serial",
            "java.io.Serializable",
        }
        field_lines: list[str] = []
        setter_lines: list[str] = []
        for field in entity_spec.get("fields", []):
            definition = type_system.resolve(field)
            imports.update(definition.imports)
            field_lines.append(f"    private {definition.java_type} {field['name']};")
            setter_name = field["name"][:1].upper() + field["name"][1:]
            setter_lines.append(f"        vo.set{setter_name}(entity.get{setter_name}());")
        relation_lines: list[str] = []
        relation_imports: set[str] = set(imports)
        for relation in context["relations"].get(entity_name, []):
            target_vo = relation["target_summary_vo"]
            relation_imports.add(f"{context['package_root']}.domain.vo.{target_vo}")
            if relation["type"] == "one_to_many":
                relation_imports.add("com.mybatisflex.annotation.RelationOneToMany")
                relation_imports.add("java.util.List")
                relation_lines.append(
                    "    @RelationOneToMany(\n"
                    f'            selfField = "{relation["self_field"]}",\n'
                    f'            targetField = "{relation["target_field"]}",\n'
                    f'            targetTable = "{relation["target_table"]}",\n'
                    f'            selectColumns = "{relation["select_columns"]}"\n'
                    "    )\n"
                    f"    private List<{target_vo}> {relation['property_name']};"
                )
            elif relation["type"] == "many_to_one":
                relation_imports.add("com.mybatisflex.annotation.RelationOneToOne")
                relation_lines.append(
                    "    @RelationOneToOne(\n"
                    f'            selfField = "{relation["self_field"]}",\n'
                    f'            targetField = "{relation["target_field"]}",\n'
                    f'            targetTable = "{relation["target_table"]}",\n'
                    f'            selectColumns = "{relation["select_columns"]}"\n'
                    "    )\n"
                    f"    private {target_vo} {relation['property_name']};"
                )
        imports_text = "\n".join(f"import {value};" for value in sorted(relation_imports))
        fields_text = "\n\n".join(field_lines + relation_lines)
        setters_text = "\n".join(setter_lines)
        all_args_import = '\nimport lombok.AllArgsConstructor;' if (field_lines or relation_lines) else ""
        all_args_annotation = "@AllArgsConstructor\n" if (field_lines or relation_lines) else ""
        return (
            f"package {context['package_root']}.domain.vo;\n\n"
            f"{imports_text}{all_args_import}\n\n"
            f"@Data\n"
            f"@NoArgsConstructor\n"
            f"{all_args_annotation}"
            f"public class {entity_name}DetailsVo implements Serializable {{\n\n"
            f"    @Serial\n"
            f"    private static final long serialVersionUID = 1L;\n\n"
            f"{fields_text}\n\n"
            f"    public static {entity_name}DetailsVo fromEntity({entity_name} entity) {{\n"
            f"        if (entity == null) {{\n"
            f"            return null;\n"
            f"        }}\n"
            f"        {entity_name}DetailsVo vo = new {entity_name}DetailsVo();\n"
            f"{setters_text}\n"
            f"        return vo;\n"
            f"    }}\n"
            f"}}\n"
        )

    def _write(self, context: dict[str, Any], class_name: str, package_suffix: str, source: str) -> str:
        package_name = f"{context['package_root']}.{package_suffix}"
        destination = (
            context["output_root"]
            / "src"
            / "main"
            / "java"
            / Path(*package_name.split("."))
            / f"{class_name}.java"
        )
        write_text(destination, source)
        return str(destination)
