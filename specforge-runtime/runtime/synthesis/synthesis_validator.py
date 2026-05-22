from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from runtime.codegen.common import dump_yaml, parse_package_name, read_text
from runtime.toolchain import resolve_toolchain


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
        findings.extend(self._controller_contract_findings(semantic_role))

        report = {
            "status": "PASS" if not findings else "FAIL",
            "finding_count": len(findings),
            "findings": findings,
        }
        dump_yaml(self.context["output_root"] / "logs" / "synthesis-validation.yaml", report)
        return report

    def compile_check(self) -> dict[str, Any]:
        toolchain = resolve_toolchain()
        mvn_command = toolchain["maven_command"]
        if mvn_command is None:
            result = {
                "status": "SKIPPED",
                "reason": "maven-not-found",
                "environment_binding": toolchain["binding"],
            }
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
                encoding="utf-8",
                errors="replace",
                check=False,
                env=toolchain["env"],
            )

        result = {
            "status": "PASS" if completed.returncode == 0 else "FAIL",
            "return_code": completed.returncode,
            "command": mvn_command,
            "environment_binding": toolchain["binding"],
            "stdout": completed.stdout[-4000:],
            "stderr": completed.stderr[-4000:],
        }
        if completed.returncode != 0:
            result = self._classify_compile_failure(result)
        dump_yaml(self.context["output_root"] / "logs" / "compile-check.yaml", result)
        return result

    def _controller_contract_findings(self, semantic_role: str) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []
        controller_result = next(
            (item for item in self.context.get("emitter_results", []) if item.get("emitter") == "controller-synthesizer"),
            {},
        )
        skipped_entities = controller_result.get("skipped_entities", [])
        partial_contract_skips = [
            item
            for item in skipped_entities
            if 0 < len(item.get("missing", [])) < 2
        ]
        if partial_contract_skips:
            findings.append(
                {
                    "code": "controller-entity-partial-route-contract",
                    "status": "FAIL",
                    "details": f"Controller synthesis skipped entities with partial route contracts: {partial_contract_skips}",
                }
            )

        if semantic_role != "business-domain" or not self.context["schema"].get("permissions"):
            return findings

        resource_root = self.generated_java_root / Path(*self.context["package_root"].split(".")) / "resource"
        resource_files = sorted(resource_root.glob("*Resource.java"))
        if not resource_files:
            findings.append(
                {
                    "code": "business-controller-missing",
                    "status": "FAIL",
                    "details": "Business-domain module with permissions must emit at least one Resource class.",
                }
            )
            return findings

        source = "\n".join(read_text(path) for path in resource_files)
        expected_methods = {
            "create": "@PostMapping",
            "update": "@PutMapping",
            "delete": "@DeleteMapping",
            "page_or_list": ["@GetMapping(\"/page\")", "@GetMapping(\"/list\")"],
            "details": "@GetMapping(\"/{id}\")",
        }
        missing = []
        for name, marker in expected_methods.items():
            if isinstance(marker, list):
                if not any(item in source for item in marker):
                    missing.append(name)
            elif marker not in source:
                missing.append(name)
        if missing:
            findings.append(
                {
                    "code": "business-crud-surface-incomplete",
                    "status": "FAIL",
                    "details": f"Business Resource CRUD surface is incomplete: {', '.join(missing)}",
                }
            )
        return findings

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
