from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from runtime.codegen.common import dump_yaml, parse_package_name, read_text, safe_load_yaml
from runtime.synthesis import SynthesisPipeline

from .boot_verifier import BootVerifier
from .infrastructure_validator import InfrastructureValidator


class BackendAssembler:
    def __init__(self, project_root: Path, backend_root: Path, run_root: Path, specs_dir: Path) -> None:
        self.project_root = project_root
        self.backend_root = backend_root
        self.run_root = run_root
        self.specs_dir = specs_dir
        self.generated_project_root = run_root / "generated-project"

    def assemble(self, field_schema_path: Path, run_compile: bool = True, run_boot: bool = True) -> dict[str, Any]:
        if self.generated_project_root.exists():
            shutil.rmtree(self.generated_project_root)
        platform_summary = self._prepare_backend_baseline(field_schema_path)

        synthesis_summary = SynthesisPipeline(
            project_root=self.project_root,
            backend_root=self.backend_root,
            output_root=self.generated_project_root,
            specs_dir=self.specs_dir,
        ).run(verify_compile=False, field_schema_name=str(field_schema_path))

        validator = InfrastructureValidator(self.generated_project_root)
        infrastructure = validator.validate(platform_summary["field_schema"], platform_summary["platform_schema"])
        verification = BootVerifier(self.generated_project_root).verify(run_compile=run_compile, run_boot=run_boot)

        if infrastructure["status"] == "FAIL" or synthesis_summary["status"] == "FAIL":
            status = "FAIL"
        elif verification["compile_check"]["status"] == "FAIL" or verification["boot_check"]["status"] == "FAIL":
            status = "FAIL"
        elif verification["compile_check"]["status"] == "BLOCKED" or verification["boot_check"]["status"] == "BLOCKED":
            status = "BLOCKED"
        else:
            status = "PASS"

        report = {
            "status": status,
            "platform_status": platform_summary["status"],
            "synthesis_status": synthesis_summary["status"],
            "infrastructure_status": infrastructure["status"],
            "compile_check_status": verification["compile_check"]["status"],
            "boot_check_status": verification["boot_check"]["status"],
            "generated_project_root": str(self.generated_project_root),
            "assembly_mode": platform_summary["assembly_mode"],
        }
        dump_yaml(self.generated_project_root / "logs" / "assembly-report.yaml", report)
        return {
            "report": report,
            "platform_summary": platform_summary,
            "synthesis_summary": synthesis_summary,
            "infrastructure": infrastructure,
            "verification": verification,
        }

    def _prepare_backend_baseline(self, field_schema_path: Path) -> dict[str, Any]:
        field_schema = safe_load_yaml(field_schema_path)
        self.generated_project_root.parent.mkdir(parents=True, exist_ok=True)

        if self.backend_root.exists():
            shutil.copytree(
                self.backend_root,
                self.generated_project_root,
                ignore=shutil.ignore_patterns("target", ".git", ".idea", "*.iml", "__pycache__"),
            )
            application_package, application_class = self._discover_application_entrypoint(self.generated_project_root)
            platform_schema = {
                "platform": {
                    "package_root": application_package.rsplit(".", 1)[0] if "." in application_package else application_package,
                    "application_package": application_package,
                    "application_class": application_class,
                    "artifact_id": self.generated_project_root.name,
                    "project_name": field_schema["module"]["name"],
                },
                "database": {
                    "type": field_schema["module"].get("database", "mysql"),
                },
            }
            manifest = {
                "status": "PASS",
                "assembly_mode": "backend-baseline-copy",
                "baseline_backend_root": str(self.backend_root),
                "generated_project_root": str(self.generated_project_root),
                "ignored_paths": ["target", ".git", ".idea", "*.iml", "__pycache__"],
            }
            dump_yaml(self.run_root / "generated-ir" / "platform-schema.generated.yaml", platform_schema)
            dump_yaml(self.generated_project_root / "logs" / "platform-report.yaml", manifest)
            return {
                "status": "PASS",
                "assembly_mode": "backend-baseline-copy",
                "field_schema": field_schema,
                "platform_schema": platform_schema,
                "manifest": manifest,
            }

        self.generated_project_root.mkdir(parents=True, exist_ok=True)
        platform_schema = {
            "platform": {
                "package_root": field_schema["module"]["package_root"],
                "application_package": field_schema["module"]["package_root"].rsplit(".", 1)[0],
                "application_class": "BackendApplication",
                "artifact_id": self.generated_project_root.name,
                "project_name": field_schema["module"]["name"],
            },
            "database": {
                "type": field_schema["module"].get("database", "mysql"),
            },
        }
        manifest = {
            "status": "PASS",
            "assembly_mode": "empty-output-root",
            "baseline_backend_root": None,
            "generated_project_root": str(self.generated_project_root),
        }
        dump_yaml(self.run_root / "generated-ir" / "platform-schema.generated.yaml", platform_schema)
        dump_yaml(self.generated_project_root / "logs" / "platform-report.yaml", manifest)
        return {
            "status": "PASS",
            "assembly_mode": "empty-output-root",
            "field_schema": field_schema,
            "platform_schema": platform_schema,
            "manifest": manifest,
        }

    def _discover_application_entrypoint(self, project_root: Path) -> tuple[str, str]:
        java_root = project_root / "src" / "main" / "java"
        for source_file in sorted(java_root.rglob("*.java")):
            source = read_text(source_file)
            if "@SpringBootApplication" not in source:
                continue
            return parse_package_name(source), source_file.stem
        raise RuntimeError("Unable to locate Spring Boot application entrypoint in backend baseline")
