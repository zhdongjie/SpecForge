from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from runtime.codegen.common import dump_yaml, parse_package_name, read_text


class SynthesisValidator:
    def __init__(self, context: dict[str, Any]) -> None:
        self.context = context
        self.generated_java_root = context["output_root"] / "src" / "main" / "java"

    def validate(self) -> dict[str, Any]:
        findings: list[dict[str, Any]] = []
        route_values: list[str] = []
        permission_values: list[str] = []
        package_root = self.context["package_root"]
        semantic_role = self.context["schema"].get("module", {}).get("semantic_role", "")

        if semantic_role == "business-domain" and not package_root.startswith("org.eu.originalkeen.business."):
            findings.append(
                {
                    "code": "business_domain_package_root_violation",
                    "status": "FAIL",
                    "details": f"Business-domain synthesis package root must stay under org.eu.originalkeen.business.*, got {package_root}",
                }
            )

        for source_file in sorted(self.generated_java_root.rglob("*.java")):
            source = read_text(source_file)
            package_name = parse_package_name(source)
            if not package_name.startswith(package_root):
                continue
            route_values.extend(re.findall(r'@RequestMapping\("([^"]+)"\)', source))
            permission_values.extend(re.findall(r'hasAuthority\(\'" \+ .*?\.([A-Z_]+) \+ "\'\)', source))

        findings.extend(self._duplicates(route_values, "route-duplication"))
        findings.extend(self._duplicates(self.context["schema"].get("permissions", []), "permission-duplication"))
        findings.extend(self._relation_findings())

        report = {
            "status": "PASS" if not findings else "FAIL",
            "finding_count": len(findings),
            "findings": findings,
        }
        dump_yaml(self.context["output_root"] / "logs" / "synthesis-validation.yaml", report)
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
            dump_yaml(self.context["output_root"] / "logs" / "compile-check.yaml", result)
            return result

        with tempfile.TemporaryDirectory(prefix="specforge-synthesis-compile-") as temp_dir:
            temp_backend = Path(temp_dir) / "backend"
            shutil.copytree(self.context["backend_root"], temp_backend)
            for source_file in sorted(self.generated_java_root.rglob("*.java")):
                relative_path = source_file.relative_to(self.generated_java_root)
                destination = temp_backend / "src" / "main" / "java" / relative_path
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source_file, destination)

            generated_resource_root = self.context["output_root"] / "src" / "main" / "resources"
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
        dump_yaml(self.context["output_root"] / "logs" / "compile-check.yaml", result)
        return result

    def _relation_findings(self) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []
        entities = self.context["schema"].get("entities", {})
        for entity_name, relations in sorted(self.context["relations"].items()):
            entity_fields = {field["name"] for field in entities[entity_name].get("fields", [])}
            for relation in relations:
                if relation["self_field"] not in entity_fields and relation["self_field"] != "id":
                    findings.append(
                        {
                            "code": "relation-self-field-missing",
                            "status": "FAIL",
                            "details": f"{entity_name}.{relation['self_field']} is missing",
                        }
                    )
        return findings

    def _duplicates(self, values: list[str], code: str) -> list[dict[str, Any]]:
        duplicates = sorted({value for value in values if values.count(value) > 1})
        return [
            {
                "code": code,
                "status": "FAIL",
                "details": f"Duplicate semantic binding detected: {value}",
            }
            for value in duplicates
        ]

    def _classify_compile_failure(self, result: dict[str, Any]) -> dict[str, Any]:
        combined_output = f"{result.get('stdout', '')}\n{result.get('stderr', '')}"
        paths = re.findall(r"/([A-Za-z]:/[^:\n]+?\.java)", combined_output)
        normalized_paths = [path.replace("/", "\\") for path in paths]
        module_marker = self.context["package_root"].replace(".", "\\")
        related_paths = [path for path in normalized_paths if module_marker in path]
        if related_paths:
            return {
                **result,
                "status": "FAIL",
                "failure_scope": "synthesized-module",
                "related_source_paths": related_paths,
            }
        return {
            **result,
            "status": "BLOCKED",
            "failure_scope": "external-baseline",
            "details": "Backend template contains unrelated compile failures outside synthesized module scope.",
            "related_source_paths": normalized_paths,
        }
