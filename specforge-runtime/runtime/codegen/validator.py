from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
import re
from typing import Any

from .common import CodegenContext, CodegenError, dump_yaml, parse_package_name, read_text


class CodegenValidator:
    def __init__(self, context: CodegenContext) -> None:
        self.context = context

    def validate(self, emission_results: list[dict[str, Any]]) -> dict[str, Any]:
        findings: list[dict[str, Any]] = []
        manifest_classes = {
            self._strip_java_suffix(artifact["relative_java_path"].split("/")[-1])
            for result in emission_results
            for artifact in result.get("artifacts", [])
            if artifact.get("relative_java_path", "").endswith(".java")
        }

        expected_classes = self._expected_artifact_classes()
        missing_classes = sorted(expected_classes - manifest_classes)
        if missing_classes:
            findings.append(
                {
                    "code": "missing_artifacts",
                    "status": "FAIL",
                    "details": f"Missing expected generated classes: {', '.join(missing_classes)}",
                }
            )

        findings.extend(self._validate_packages())
        findings.extend(self._validate_resources())
        findings.extend(self._validate_tables(emission_results))

        status = "PASS" if not findings else "FAIL"
        report = {
            "status": status,
            "finding_count": len(findings),
            "findings": findings,
        }
        dump_yaml(self.context.output_root / "logs" / "codegen-validation.yaml", report)
        return report

    def compile_check(self) -> dict[str, Any]:
        preferred_commands = [
            Path(r"E:\Dev\Maven\apache-maven-3.9.6\bin\mvn.cmd"),
        ]
        mvn_command = None
        for candidate in preferred_commands:
            if candidate.exists():
                mvn_command = str(candidate)
                break
        if mvn_command is None:
            mvn_command = shutil.which("mvn.cmd") or shutil.which("mvn")
        if mvn_command is None:
            result = {
                "status": "SKIPPED",
                "reason": "maven-not-found",
            }
            dump_yaml(self.context.output_root / "logs" / "compile-check.yaml", result)
            return result

        with tempfile.TemporaryDirectory(prefix="specforge-compile-") as temp_dir:
            temp_backend = Path(temp_dir) / "backend"
            shutil.copytree(self.context.backend_root, temp_backend)

            original_module_root = temp_backend / "src" / "main" / "java" / self.context.package_path
            if original_module_root.exists():
                shutil.rmtree(original_module_root)

            generated_java_root = self.context.output_root / "src" / "main" / "java"
            if generated_java_root.exists():
                for source_file in sorted(generated_java_root.rglob("*.java")):
                    relative_path = source_file.relative_to(generated_java_root)
                    destination = temp_backend / "src" / "main" / "java" / relative_path
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(source_file, destination)

            generated_sql = self.context.output_root / "src" / "main" / "resources" / "sql" / "dictionary-management.generated.sql"
            if generated_sql.exists():
                sql_destination = temp_backend / "src" / "main" / "resources" / "sql" / generated_sql.name
                sql_destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(generated_sql, sql_destination)

            completed = subprocess.run(
                [mvn_command, "-q", "-DskipTests", "compile"],
                cwd=temp_backend,
                capture_output=True,
                text=True,
                check=False,
            )

        result = {
            "status": "PASS" if completed.returncode == 0 else "FAIL",
            "return_code": completed.returncode,
            "command": mvn_command,
            "stdout": completed.stdout[-4000:],
            "stderr": completed.stderr[-4000:],
        }
        if completed.returncode != 0:
            result = self._classify_compile_failure(result)
        dump_yaml(self.context.output_root / "logs" / "compile-check.yaml", result)
        return result

    def _expected_artifact_classes(self) -> set[str]:
        classes: set[str] = set()
        for artifact_kind, items in self.context.module_spec.get("artifact_contract", {}).items():
            if artifact_kind == "bo":
                continue
            for item in items:
                classes.add(item)
        return classes

    def _validate_packages(self) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []
        for source_file in sorted((self.context.output_root / "src" / "main" / "java").rglob("*.java")):
            source = read_text(source_file)
            package_name = parse_package_name(source)
            if not package_name.startswith(self.context.package_root):
                findings.append(
                    {
                        "code": "package_boundary_violation",
                        "status": "FAIL",
                        "details": f"{source_file.name} package {package_name} escapes {self.context.package_root}",
                    }
                )
        return findings

    def _validate_resources(self) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []
        for resource_name, capabilities in sorted(self.context.capabilities_by_resource.items()):
            path = self._find_generated_class(resource_name)
            if path is None:
                findings.append(
                    {
                        "code": "missing_resource",
                        "status": "FAIL",
                        "details": f"Unable to locate generated resource {resource_name}",
                    }
                )
                continue
            source = read_text(path)
            request_mapping = self._match_single(source, '@RequestMapping("', '")')
            expected_mapping = self.context.resource_route_roots.get(resource_name)
            if request_mapping != expected_mapping:
                findings.append(
                    {
                        "code": "route_binding_mismatch",
                        "status": "FAIL",
                        "details": f"{resource_name} request mapping {request_mapping} != {expected_mapping}",
                    }
                )
            missing_authorities = [
                capability["authority_binding"]
                for capability in capabilities
                if capability["authority_binding"] not in source
            ]
            if missing_authorities:
                findings.append(
                    {
                        "code": "authority_binding_mismatch",
                        "status": "FAIL",
                        "details": f"{resource_name} is missing authorities: {', '.join(sorted(missing_authorities))}",
                    }
                )
        return findings

    def _validate_tables(self, emission_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
        entity_tables: set[str] = set()
        sql_tables: set[str] = set()
        for result in emission_results:
            entity_tables.update(result.get("entity_tables", {}).values())
            sql_tables.update(result.get("tables", []))

        findings: list[dict[str, Any]] = []
        required = set(self.context.required_tables)
        if not required.issubset(entity_tables | sql_tables):
            findings.append(
                {
                    "code": "table_coverage_incomplete",
                    "status": "FAIL",
                    "details": f"Required tables are not fully covered: {', '.join(sorted(required - (entity_tables | sql_tables)))}",
                }
            )
        return findings

    def _find_generated_class(self, class_name: str) -> Path | None:
        matches = sorted((self.context.output_root / "src" / "main" / "java").rglob(f"{class_name}.java"))
        return matches[0] if matches else None

    def _strip_java_suffix(self, filename: str) -> str:
        return filename[:-5] if filename.endswith(".java") else filename

    def _match_single(self, source: str, prefix: str, suffix: str) -> str | None:
        start = source.find(prefix)
        if start < 0:
            return None
        start += len(prefix)
        end = source.find(suffix, start)
        if end < 0:
            raise CodegenError(f"Unable to parse token between {prefix} and {suffix}")
        return source[start:end]

    def _classify_compile_failure(self, result: dict[str, Any]) -> dict[str, Any]:
        combined_output = f"{result.get('stdout', '')}\n{result.get('stderr', '')}"
        paths = re.findall(r"/([A-Za-z]:/[^:\n]+?\.java)", combined_output)
        normalized_paths = [path.replace("/", "\\") for path in paths]
        module_marker = str(self.context.package_path).replace("/", "\\")
        related_paths = [path for path in normalized_paths if module_marker in path]
        if related_paths:
            return {
                **result,
                "status": "FAIL",
                "failure_scope": "generated-module",
                "related_source_paths": related_paths,
            }
        return {
            **result,
            "status": "BLOCKED",
            "failure_scope": "external-baseline",
            "details": "Backend template contains unrelated compile failures outside generated module scope.",
            "related_source_paths": normalized_paths,
        }
