from __future__ import annotations

from pathlib import Path
from typing import Any

from runtime.codegen.common import dump_yaml
from runtime.platform_compiler import ProjectCompiler

from .boot_diagnostics import BootDiagnostics
from .boot_repair_validator import BootRepairValidator
from .compile_diagnostics import CompileDiagnostics
from .compile_repair_engine import CompileRepairEngine
from .compile_repair_validator import CompileRepairValidator
from .deterministic_repair_validator import DeterministicRepairValidator
from .project_health_reporter import ProjectHealthReporter


class HardeningPipeline:
    def __init__(self, project_root: Path, backend_root: Path, run_root: Path, specs_dir: Path) -> None:
        self.project_root = project_root
        self.backend_root = backend_root
        self.run_root = run_root
        self.specs_dir = specs_dir
        self.generated_project_root = run_root / "generated-project"
        self.logs_root = self.generated_project_root / "logs"

    def run(
        self,
        module_schema_name: str = "module-schema.resolved.yaml",
        module_spec_name: str = "module-spec.yaml",
        project_assembly_plan_name: str | None = None,
        auto_repair: bool = False,
        verify_boot: bool = False,
        repair_max_passes: int = 5,
    ) -> dict[str, Any]:
        compiler_summary = ProjectCompiler(
            project_root=self.project_root,
            backend_root=self.backend_root,
            run_root=self.run_root,
            specs_dir=self.specs_dir,
        ).run(
            module_schema_name=module_schema_name,
            module_spec_name=module_spec_name,
            project_assembly_plan_name=project_assembly_plan_name,
            run_compile=False,
            run_boot=False,
        )

        initial_compile_diagnostics = CompileDiagnostics(self.generated_project_root, self.logs_root).run()
        compile_diagnostics = initial_compile_diagnostics
        compile_repair_report = {"status": "SKIPPED", "repairs": [], "post_repair_status": compile_diagnostics["status"]}
        if auto_repair:
            repair_runs: list[dict[str, Any]] = []
            for _ in range(max(1, repair_max_passes)):
                if compile_diagnostics["status"] != "FAIL":
                    break
                pass_report = CompileRepairEngine(self.generated_project_root, self.logs_root).apply(
                    compile_diagnostics,
                    max_passes=1,
                )
                repair_runs.append(pass_report)
                if pass_report["status"] == "NO_ACTION":
                    compile_repair_report = pass_report
                    break
                compile_diagnostics = CompileDiagnostics(self.generated_project_root, self.logs_root).run()
                compile_repair_report = {
                    "status": "PASS",
                    "repairs": [repair for item in repair_runs for repair in item.get("repairs", [])],
                    "repair_passes": [entry for item in repair_runs for entry in item.get("repair_passes", [])],
                    "dependency_resolution_status": repair_runs[-1].get("dependency_resolution_status", "PASS"),
                    "post_repair_status": compile_diagnostics["status"],
                }
            if not repair_runs:
                dump_yaml(self.logs_root / "compile-repair-report.yaml", compile_repair_report)
                dump_yaml(self.logs_root / "dependency-resolution-report.yaml", {"status": "SKIPPED", "actions": []})
            else:
                if "post_repair_status" not in compile_repair_report:
                    compile_repair_report["post_repair_status"] = compile_diagnostics["status"]
                dump_yaml(self.logs_root / "compile-repair-report.yaml", compile_repair_report)
        else:
            dump_yaml(self.logs_root / "compile-repair-report.yaml", compile_repair_report)
            dump_yaml(self.logs_root / "dependency-resolution-report.yaml", {"status": "SKIPPED", "actions": []})

        compile_repair_validation = CompileRepairValidator().validate(initial_compile_diagnostics, compile_repair_report)

        boot_diagnostics: dict[str, Any]
        boot_repair_report: dict[str, Any]
        if compile_diagnostics["status"] == "PASS" and verify_boot:
            boot_diagnostics = BootDiagnostics(self.generated_project_root, self.logs_root).run()
        elif verify_boot:
            boot_diagnostics = {"status": "BLOCKED", "boot_failures": [], "reason": "compile_failed"}
            dump_yaml(self.logs_root / "boot-diagnostics.yaml", boot_diagnostics)
        else:
            boot_diagnostics = {"status": "SKIPPED", "boot_failures": []}
            dump_yaml(self.logs_root / "boot-diagnostics.yaml", boot_diagnostics)

        boot_repair_report = {
            "status": "SKIPPED",
            "repairs": [],
            "post_repair_status": boot_diagnostics["status"],
        }
        dump_yaml(self.logs_root / "boot-repair-report.yaml", boot_repair_report)
        boot_repair_validation = BootRepairValidator().validate(boot_diagnostics, boot_repair_report)
        deterministic_validation = DeterministicRepairValidator().validate(
            compile_repair_report,
            boot_repair_report,
        )
        health_report = ProjectHealthReporter(self.logs_root).write(
            compile_diagnostics=compile_diagnostics,
            compile_repair_report=compile_repair_report,
            boot_diagnostics=boot_diagnostics,
            boot_repair_report=boot_repair_report,
            compile_repair_validation=compile_repair_validation,
            boot_repair_validation=boot_repair_validation,
            deterministic_validation=deterministic_validation,
        )
        summary = {
            "status": health_report["status"],
            "compiler_status": compiler_summary["status"],
            "generated_project_root": str(self.generated_project_root),
            "compile_status": compile_diagnostics["status"],
            "boot_status": boot_diagnostics["status"],
        }
        dump_yaml(self.run_root / "logs" / "hardening-report.yaml", summary)
        return summary
