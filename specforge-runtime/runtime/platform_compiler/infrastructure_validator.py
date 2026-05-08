from __future__ import annotations

from pathlib import Path
from typing import Any

from runtime.codegen.common import dump_yaml


class InfrastructureValidator:
    def __init__(self, output_root: Path) -> None:
        self.output_root = output_root

    def validate(self, field_schema: dict[str, Any], platform_schema: dict[str, Any]) -> dict[str, Any]:
        findings: list[dict[str, Any]] = []
        package_root = field_schema["module"]["package_root"]
        semantic_role = field_schema["module"].get("semantic_role", "")
        application_config_candidates = [
            self.output_root / "src" / "main" / "resources" / "application.yml",
            self.output_root / "src" / "main" / "resources" / "application.yaml",
        ]
        required_paths = [
            self.output_root / "pom.xml",
            self.output_root / "src" / "main" / "java" / Path(*platform_schema["platform"]["application_package"].split(".")) / f"{platform_schema['platform']['application_class']}.java",
            self.output_root / "src" / "main" / "java" / Path(*field_schema["module"]["package_root"].split(".")),
        ]
        for path in required_paths:
            if not path.exists():
                findings.append({"code": "missing_required_artifact", "status": "FAIL", "details": str(path)})
        if semantic_role == "business-domain" and not package_root.startswith("org.eu.originalkeen.business."):
            findings.append(
                {
                    "code": "business_domain_package_root_violation",
                    "status": "FAIL",
                    "details": f"Business-domain backend assembly must target org.eu.originalkeen.business.*, got {package_root}",
                }
            )
        if not any(candidate.exists() for candidate in application_config_candidates):
            findings.append(
                {
                    "code": "missing_required_artifact",
                    "status": "FAIL",
                    "details": "Missing application configuration file: application.yml or application.yaml",
                }
            )

        java_root = self.output_root / "src" / "main" / "java"
        if java_root.exists():
            resource_count = len(sorted(java_root.rglob("*Resource.java")))
            if resource_count == 0:
                findings.append({"code": "missing_generated_resources", "status": "FAIL", "details": "No resource layer artifacts were assembled"})

        report = {
            "status": "PASS" if not findings else "FAIL",
            "finding_count": len(findings),
            "findings": findings,
        }
        dump_yaml(self.output_root / "logs" / "infrastructure-validation.yaml", report)
        return report
