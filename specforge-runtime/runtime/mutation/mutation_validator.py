from __future__ import annotations

from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from typing import Any

from runtime.codegen.common import dump_yaml, parse_package_name, read_text

from .naming_transformer import NamingTransformer


class MutationValidator:
    def __init__(self, backend_root: Path, output_root: Path, naming_transformer: NamingTransformer) -> None:
        self.backend_root = backend_root
        self.output_root = output_root
        self.naming_transformer = naming_transformer
        self.generated_java_root = output_root / "src" / "main" / "java"

    def validate(self) -> dict[str, Any]:
        findings: list[dict[str, Any]] = []
        java_files = sorted(self.generated_java_root.rglob("*.java"))
        destination_paths: set[str] = set()
        route_values: list[str] = []
        permission_values: list[str] = []
        table_values: list[str] = []

        for source_file in java_files:
            source = read_text(source_file)
            package_name = parse_package_name(source)
            if not package_name.startswith(self.naming_transformer.target_package_root):
                findings.append(
                    {
                        "code": "package-leakage",
                        "status": "FAIL",
                        "details": f"{source_file.name} escaped target package root {self.naming_transformer.target_package_root}",
                    }
                )

            if self.naming_transformer.source_package_root in source:
                findings.append(
                    {
                        "code": "stale-package-reference",
                        "status": "FAIL",
                        "details": f"{source_file.name} still contains source package root",
                    }
                )

            relative_path = source_file.relative_to(self.generated_java_root).as_posix()
            if relative_path in destination_paths:
                findings.append(
                    {
                        "code": "artifact-path-collision",
                        "status": "FAIL",
                        "details": f"Duplicate generated artifact path {relative_path}",
                    }
                )
            destination_paths.add(relative_path)

            route_values.extend(re.findall(r'@RequestMapping\("([^"]+)"\)', source))
            permission_values.extend(re.findall(r"hasAuthority\('([^']+)'\)", source))
            table_values.extend(re.findall(r'@Table\("([^"]+)"\)', source))

        findings.extend(self._check_duplicates(route_values, "route-collision"))
        findings.extend(self._check_duplicates(permission_values, "permission-collision"))
        findings.extend(self._check_duplicates(table_values, "table-duplication"))

        status = "PASS" if not findings else "FAIL"
        report = {
            "status": status,
            "finding_count": len(findings),
            "findings": findings,
        }
        dump_yaml(self.output_root / "logs" / "mutation-validation.yaml", report)
        return report

    def compile_check(self) -> dict[str, Any]:
        preferred_commands = [Path(r"E:\Dev\Maven\apache-maven-3.9.6\bin\mvn.cmd")]
        mvn_command = None
        for candidate in preferred_commands:
            if candidate.exists():
                mvn_command = str(candidate)
                break
        if mvn_command is None:
            mvn_command = shutil.which("mvn.cmd") or shutil.which("mvn")
        if mvn_command is None:
            result = {"status": "SKIPPED", "reason": "maven-not-found"}
            dump_yaml(self.output_root / "logs" / "mutation-compile-check.yaml", result)
            return result

        with tempfile.TemporaryDirectory(prefix="specforge-mutation-compile-") as temp_dir:
            temp_backend = Path(temp_dir) / "backend"
            shutil.copytree(self.backend_root, temp_backend)
            for source_file in sorted(self.generated_java_root.rglob("*.java")):
                relative_path = source_file.relative_to(self.generated_java_root)
                destination = temp_backend / "src" / "main" / "java" / relative_path
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source_file, destination)

            generated_resource_root = self.output_root / "src" / "main" / "resources"
            if generated_resource_root.exists():
                for resource_file in sorted(generated_resource_root.rglob("*")):
                    if not resource_file.is_file():
                        continue
                    relative_path = resource_file.relative_to(generated_resource_root)
                    destination = temp_backend / "src" / "main" / "resources" / relative_path
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(resource_file, destination)

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
        dump_yaml(self.output_root / "logs" / "mutation-compile-check.yaml", result)
        return result

    def _check_duplicates(self, values: list[str], code: str) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []
        duplicates = sorted({value for value in values if values.count(value) > 1})
        for value in duplicates:
            findings.append(
                {
                    "code": code,
                    "status": "FAIL",
                    "details": f"Duplicate semantic binding detected: {value}",
                }
            )
        return findings

    def _classify_compile_failure(self, result: dict[str, Any]) -> dict[str, Any]:
        combined_output = f"{result.get('stdout', '')}\n{result.get('stderr', '')}"
        paths = re.findall(r"/([A-Za-z]:/[^:\n]+?\.java)", combined_output)
        normalized_paths = [path.replace("/", "\\") for path in paths]
        module_marker = self.naming_transformer.target_package_root.replace(".", "\\")
        related_paths = [path for path in normalized_paths if module_marker in path]
        if related_paths:
            return {
                **result,
                "status": "FAIL",
                "failure_scope": "mutated-module",
                "related_source_paths": related_paths,
            }
        return {
            **result,
            "status": "BLOCKED",
            "failure_scope": "external-baseline",
            "details": "Backend template contains unrelated compile failures outside mutated module scope.",
            "related_source_paths": normalized_paths,
        }
