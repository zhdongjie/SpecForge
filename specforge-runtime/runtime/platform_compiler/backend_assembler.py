from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from runtime.codegen.common import dump_yaml
from runtime.synthesis import SynthesisPipeline

from .boot_verifier import BootVerifier
from .infrastructure_validator import InfrastructureValidator
from .platform_pipeline import PlatformPipeline


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
        self.generated_project_root.mkdir(parents=True, exist_ok=True)

        platform_summary = PlatformPipeline(
            output_root=self.generated_project_root,
            run_root=self.run_root,
            backend_root=self.backend_root,
        ).run(field_schema_path)

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
        }
        dump_yaml(self.generated_project_root / "logs" / "assembly-report.yaml", report)
        return {
            "report": report,
            "platform_summary": platform_summary,
            "synthesis_summary": synthesis_summary,
            "infrastructure": infrastructure,
            "verification": verification,
        }
