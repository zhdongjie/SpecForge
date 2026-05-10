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
        package_root = self.context["package_root"]
        semantic_role = self.context["schema"].get("module", {}).get("semantic_role", "")
        route_index: list[dict[str, Any]] = []
        permission_index: list[dict[str, Any]] = []

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
            if source_file.name.endswith("Resource.java") and self._is_rest_resource(source_file, source):
                request_mapping = self._match_single(source, '@RequestMapping("', '")')
                methods = self._parse_http_methods(source)
                if request_mapping:
                    route_values.append(request_mapping)
                route_index.append(
                    {
                        "class_name": source_file.stem,
                        "package_name": package_name,
                        "request_mapping": request_mapping,
                        "method_count": len(methods),
                        "methods": methods,
                    }
                )
            if source_file.name.endswith("PermissionConstant.java"):
                constants = self._parse_permission_constants(source)
                permission_index.append(
                    {
                        "class_name": source_file.stem,
                        "package_name": package_name,
                        "constant_count": len(constants),
                        "constants": constants,
                    }
                )

        findings.extend(self._duplicates(route_values, "route-duplication"))
        findings.extend(self._duplicates(self.context["schema"].get("permissions", []), "permission-duplication"))
        findings.extend(self._relation_findings())
        findings.extend(self._business_domain_findings(route_index, permission_index, semantic_role))

        report = {
            "status": "PASS" if not findings else "FAIL",
            "finding_count": len(findings),
            "findings": findings,
            "business_route_count": len(route_index),
            "business_permission_constant_count": len(permission_index),
        }
        dump_yaml(self.context["output_root"] / "logs" / "business-route-index.yaml", {"routes": route_index})
        dump_yaml(self.context["output_root"] / "logs" / "business-permission-index.yaml", {"permission_constants": permission_index})
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

    def _is_rest_resource(self, source_file: Path, source: str) -> bool:
        return source_file.parent.name == "resource" or "@RestController" in source

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

    def _business_domain_findings(
        self,
        route_index: list[dict[str, Any]],
        permission_index: list[dict[str, Any]],
        semantic_role: str,
    ) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []
        if semantic_role != "business-domain":
            return findings

        if not route_index:
            findings.append(
                {
                    "code": "business-resource-missing",
                    "status": "FAIL",
                    "details": "Business-domain synthesis must emit at least one Resource route",
                }
            )
        for route_entry in route_index:
            if not route_entry.get("request_mapping"):
                findings.append(
                    {
                        "code": "business-resource-request-mapping-missing",
                        "status": "FAIL",
                        "details": f"{route_entry['class_name']} is missing @RequestMapping",
                    }
                )
            if not route_entry.get("methods"):
                findings.append(
                    {
                        "code": "business-resource-method-binding-missing",
                        "status": "FAIL",
                        "details": f"{route_entry['class_name']} does not expose HTTP methods",
                    }
                )

        if not permission_index:
            findings.append(
                {
                    "code": "business-permission-constant-missing",
                    "status": "FAIL",
                    "details": "Business-domain synthesis must emit at least one PermissionConstant class",
                }
            )
        for permission_entry in permission_index:
            if permission_entry["constant_count"] == 0:
                findings.append(
                    {
                        "code": "business-permission-constant-empty",
                        "status": "FAIL",
                        "details": f"{permission_entry['class_name']} contains no permission constants",
                    }
                )
        return findings

    def _parse_http_methods(self, source: str) -> list[dict[str, Any]]:
        method_pattern = re.compile(r"((?:@[A-Za-z]+(?:\([^\n]*?\))?\s*)+)public\s+ResponseEntity<", re.DOTALL)
        methods: list[dict[str, Any]] = []
        for match in method_pattern.finditer(source):
            annotation_block = match.group(1)
            mapping = re.search(r'@(Get|Post|Put|Delete)Mapping(?:\("([^"]*)"\))?', annotation_block)
            if not mapping:
                continue
            authorization = re.search(r"@PreAuthorize\(\"hasAuthority\('([^']+)'\)\"\)", annotation_block)
            methods.append(
                {
                    "http_method": mapping.group(1).upper(),
                    "sub_path": mapping.group(2) or "",
                    "authority": authorization.group(1) if authorization else None,
                }
            )
        return methods

    def _parse_permission_constants(self, source: str) -> list[dict[str, str]]:
        pattern = re.compile(r'public static final String ([A-Z0-9_]+) = "([^"]+)";')
        return [
            {
                "constant_name": match.group(1),
                "authority": match.group(2),
            }
            for match in pattern.finditer(source)
        ]

    def _match_single(self, source: str, prefix: str, suffix: str) -> str | None:
        start = source.find(prefix)
        if start < 0:
            return None
        start += len(prefix)
        end = source.find(suffix, start)
        if end < 0:
            return None
        return source[start:end]

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
