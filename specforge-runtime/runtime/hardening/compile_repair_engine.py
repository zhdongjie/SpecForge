from __future__ import annotations

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
