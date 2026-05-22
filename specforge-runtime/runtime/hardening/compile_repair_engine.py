from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from runtime.codegen.common import dump_yaml, read_text, write_text

from .bean_conflict_resolver import BeanConflictResolver
from .dependency_resolver import DependencyResolver
from .import_resolver import ImportResolver
from .package_resolver import PackageResolver


class CompileRepairEngine:
    def __init__(self, project_root: Path, logs_root: Path) -> None:
        self.project_root = project_root
        self.logs_root = logs_root
        self.import_resolver = ImportResolver()
        self.package_resolver = PackageResolver()
        self.dependency_resolver = DependencyResolver(project_root, logs_root)
        self.bean_conflict_resolver = BeanConflictResolver()

    def apply(self, diagnostics: dict[str, Any], max_passes: int = 5) -> dict[str, Any]:
        all_repairs: list[dict[str, Any]] = []
        passes: list[dict[str, Any]] = []
        findings = list(diagnostics.get("compile_errors", []))
        for pass_index in range(1, max_passes + 1):
            repairs = self._apply_single_pass(findings)
            if not repairs:
                passes.append({"pass": pass_index, "status": "NO_ACTION", "repairs": []})
                break
            passes.append({"pass": pass_index, "status": "REPAIRED", "repairs": repairs})
            all_repairs.extend(repairs)
            break
        dependency_report = self.dependency_resolver.resolve(findings)
        effective_repairs = [repair for repair in all_repairs if repair.get("status") != "NO_OP"]
        report = {
            "status": "PASS" if effective_repairs else "NO_ACTION",
            "repair_passes": passes,
            "repairs": all_repairs,
            "dependency_resolution_status": dependency_report["status"],
        }
        dump_yaml(self.logs_root / "compile-repair-report.yaml", report)
        return report

    def _apply_single_pass(self, findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
        repairs: list[dict[str, Any]] = []
        repairs.extend(self.package_resolver.normalize(findings))
        repairs.extend(self.bean_conflict_resolver.repair(findings))
        if any(
            finding.get("category") in {"unknown_compile_failure", "unresolved_symbol"}
            for finding in findings
        ):
            repairs.extend(self._repair_table_def_imports_by_scan())
            repairs.extend(self._repair_permission_constants_by_scan())
        if any(
            finding.get("category") in {"unknown_compile_failure", "duplicate_constructor"}
            for finding in findings
        ):
            repairs.extend(self._repair_empty_enquiry_dtos_by_scan())
        for finding in findings:
            category = finding.get("category")
            file_path = self._resolve_file_path(finding.get("file"))
            if category == "unresolved_symbol" and file_path is not None:
                repair = self.import_resolver.repair_permission_constant_symbol(file_path, finding.get("symbol"))
                if repair is not None:
                    repairs.append(repair)
            elif category == "duplicate_constructor" and file_path is not None:
                repair = self._repair_empty_enquiry_dto(file_path)
                if repair is not None:
                    repairs.append(repair)
        return repairs

    def _resolve_file_path(self, raw_path: str | None) -> Path | None:
        if not raw_path:
            return None
        normalized = raw_path
        if len(normalized) > 3 and normalized[0] == "/" and normalized[2] == ":":
            normalized = normalized[1:]
        candidate = Path(normalized)
        if candidate.exists():
            return candidate
        if candidate.is_absolute():
            return None
        joined = self.project_root / normalized
        if joined.exists():
            return joined
        return None

    def _repair_empty_enquiry_dto(self, file_path: Path) -> dict[str, Any] | None:
        source = read_text(file_path)
        if "@AllArgsConstructor" not in source or "class Enquiry" not in source:
            return None
        body_has_fields = "private " in source.split("serialVersionUID", 1)[-1]
        if body_has_fields:
            return None
        updated = source.replace("import lombok.AllArgsConstructor;\n", "")
        updated = updated.replace("@AllArgsConstructor\n", "")
        if updated == source:
            return None
        write_text(file_path, updated)
        return {
            "repair_type": "empty_query_dto_constructor_alignment",
            "file": str(file_path),
            "removed_annotation": "@AllArgsConstructor",
        }


    def normalize_generated_table_def_imports(self) -> list[dict[str, Any]]:
        return self._repair_table_def_imports_by_scan()

    def _repair_table_def_imports_by_scan(self) -> list[dict[str, Any]]:
        table_defs = {
            path.stem: path
            for path in sorted((self.project_root / "target" / "generated-sources" / "annotations").rglob("*TableDef.java"))
        }
        table_def_fields = {class_name: self._read_table_def_static_field(path) for class_name, path in table_defs.items()}
        table_def_columns = {class_name: self._read_table_def_columns(path) for class_name, path in table_defs.items()}
        if not table_defs:
            return []
        repairs: list[dict[str, Any]] = []
        pattern = re.compile(
            r"static (?P<pkg>[A-Za-z0-9_.]+\.domain\.entity\.table\.)"
            r"(?P<class>[A-Za-z0-9_]+TableDef)\.(?P<field>[A-Za-z0-9_]+)"
        )
        for file_path in sorted((self.project_root / "src" / "main" / "java").rglob("*.java")):
            source = read_text(file_path)
            repair_count_before_file = len(repairs)
            field_replacements: dict[str, str] = {}
            column_replacements: dict[str, set[str]] = {}

            def replace(match: re.Match[str]) -> str:
                class_name = match.group("class")
                field_name = match.group("field")
                target_class = class_name
                target_field = field_name
                if class_name not in table_defs:
                    entity_class = f"{class_name[:-len('TableDef')]}EntityTableDef"
                    if entity_class not in table_defs:
                        return match.group(0)
                    target_class = entity_class
                actual_field = table_def_fields.get(target_class)
                if actual_field:
                    target_field = actual_field
                column_replacements[target_field] = table_def_columns.get(target_class, set())
                if target_class == class_name and target_field == field_name:
                    return match.group(0)
                field_replacements[field_name] = target_field
                repairs.append(
                    {
                        "repair_type": "mybatis_flex_table_def_entity_suffix_alignment",
                        "file": str(file_path),
                        "from": f"{class_name}.{field_name}",
                        "to": f"{target_class}.{target_field}",
                    }
                )
                return f"static {match.group('pkg')}{target_class}.{target_field}"

            updated = pattern.sub(replace, source)
            if field_replacements or column_replacements:
                updated_lines: list[str] = []
                for line in updated.splitlines(keepends=True):
                    stripped = line.lstrip()
                    if stripped.startswith(("package ", "import ")):
                        updated_lines.append(line)
                        continue
                    for old_field, new_field in sorted(field_replacements.items(), key=lambda item: len(item[0]), reverse=True):
                        line = re.sub(rf"\b{re.escape(old_field)}\b", new_field, line)
                    for table_field, columns in column_replacements.items():
                        line = self._replace_table_def_columns(line, table_field, columns)
                    updated_lines.append(line)
                updated = "".join(updated_lines)
            if updated != source:
                write_text(file_path, updated)
                if len(repairs) == repair_count_before_file:
                    repairs.append(
                        {
                            "repair_type": "mybatis_flex_table_def_column_case_alignment",
                            "file": str(file_path),
                        }
                    )
        return repairs

    def _read_table_def_static_field(self, table_def_path: Path) -> str | None:
        source = read_text(table_def_path)
        match = re.search(
            r"public static final\s+[A-Za-z0-9_]+TableDef\s+(?P<field>[A-Z0-9_]+)\s*=",
            source,
        )
        return match.group("field") if match else None

    def _read_table_def_columns(self, table_def_path: Path) -> set[str]:
        source = read_text(table_def_path)
        return set(re.findall(r"public final QueryColumn\s+([A-Z0-9_]+)\s*=", source))

    def _replace_table_def_columns(self, line: str, table_field: str, columns: set[str]) -> str:
        if not columns:
            return line

        def replace(match: re.Match[str]) -> str:
            column = match.group("column")
            normalized = column.upper()
            return f"{table_field}.{normalized}" if normalized in columns else match.group(0)

        return re.sub(rf"\b{re.escape(table_field)}\.(?P<column>[a-z][A-Za-z0-9_]*)\b", replace, line)

    def _repair_permission_constants_by_scan(self) -> list[dict[str, Any]]:
        repairs: list[dict[str, Any]] = []
        for file_path in sorted(self.project_root.rglob("*Resource.java")):
            repair = self.import_resolver.repair_permission_constant_symbol(file_path, None)
            if repair is not None:
                repairs.append(repair)
        return repairs

    def _repair_empty_enquiry_dtos_by_scan(self) -> list[dict[str, Any]]:
        repairs: list[dict[str, Any]] = []
        for file_path in sorted(self.project_root.rglob("Enquiry*PageDto.java")):
            repair = self._repair_empty_enquiry_dto(file_path)
            if repair is not None:
                repairs.append(repair)
        return repairs
