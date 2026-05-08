from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from runtime.codegen.common import dump_yaml, safe_load_yaml
from runtime.ir_lowering import IRLoweringPipeline
from runtime.synthesis import SynthesisPipeline

from .backend_assembler import BackendAssembler
from .boot_verifier import BootVerifier
from .infrastructure_validator import InfrastructureValidator


class ProjectAssemblyCompiler:
    def __init__(self, project_root: Path, backend_root: Path, run_root: Path, specs_dir: Path) -> None:
        self.project_root = project_root
        self.backend_root = backend_root
        self.run_root = run_root
        self.specs_dir = specs_dir
        self.generated_project_root = run_root / "generated-project"

    def run(self, project_assembly_plan_name: str, run_compile: bool = True, run_boot: bool = True) -> dict[str, Any]:
        plan_path = self._resolve_spec_path(project_assembly_plan_name, self.specs_dir)
        plan = safe_load_yaml(plan_path)
        module_reports: list[dict[str, Any]] = []
        infrastructure_reports: list[dict[str, Any]] = []

        platform_summary = self._prepare_project_baseline(plan)
        validator = InfrastructureValidator(self.generated_project_root)

        for module_entry in plan.get("module_sequence", []):
            if not bool(module_entry.get("enabled", True)):
                module_reports.append(
                    {
                        "module": module_entry.get("module"),
                        "status": "SKIPPED",
                        "reason": "disabled",
                    }
                )
                continue

            module_key = str(module_entry["module"])
            module_run_root = self.run_root / "modules" / module_key
            module_spec_name = str(module_entry.get("module_spec", "module-spec.yaml"))
            module_schema_name = str(module_entry.get("module_schema", "module-schema.resolved.yaml"))

            lowering_summary = IRLoweringPipeline(
                output_root=module_run_root,
                specs_dir=self.specs_dir,
            ).run(
                module_schema_name=module_schema_name,
                module_spec_name=module_spec_name,
            )
            field_schema_path = module_run_root / "generated-ir" / "field-schema.generated.yaml"

            module_output_root = module_run_root / "generated-module"
            synthesis_summary = SynthesisPipeline(
                project_root=self.project_root,
                backend_root=self.backend_root,
                output_root=module_output_root,
                specs_dir=self.specs_dir,
            ).run(verify_compile=False, field_schema_name=str(field_schema_path))

            merge_report = self._merge_module_output(module_key, module_output_root)
            field_schema = safe_load_yaml(field_schema_path)
            infrastructure = validator.validate(field_schema, platform_summary["platform_schema"])
            infrastructure_reports.append({"module": module_key, **infrastructure})

            status = "PASS"
            if lowering_summary["status"] == "FAIL" or synthesis_summary["status"] == "FAIL":
                status = "FAIL"
            elif merge_report["status"] == "FAIL" or infrastructure["status"] == "FAIL":
                status = "FAIL"

            module_report = {
                "module": module_key,
                "status": status,
                "module_spec": module_spec_name,
                "module_schema": module_schema_name,
                "field_schema_output": str(field_schema_path),
                "lowering_status": lowering_summary["status"],
                "synthesis_status": synthesis_summary["status"],
                "merge_status": merge_report["status"],
                "infrastructure_status": infrastructure["status"],
                "staging_output_root": str(module_output_root),
            }
            module_reports.append(module_report)
            dump_yaml(
                self.generated_project_root / "logs" / "modules" / module_key / "module-assembly-report.yaml",
                module_report,
            )
            if status == "FAIL":
                break

        verification = BootVerifier(self.generated_project_root).verify(run_compile=run_compile, run_boot=run_boot)

        compile_status = verification["compile_check"]["status"]
        boot_status = verification["boot_check"]["status"]
        if any(item["status"] == "FAIL" for item in module_reports):
            status = "FAIL"
        elif compile_status == "FAIL" or boot_status == "FAIL":
            status = "FAIL"
        elif compile_status == "BLOCKED" or boot_status == "BLOCKED":
            status = "BLOCKED"
        else:
            status = "PASS"

        report = {
            "status": status,
            "plan_id": plan.get("plan_id", plan_path.stem),
            "project_assembly_plan": str(plan_path),
            "module_count": len(module_reports),
            "successful_modules": len([item for item in module_reports if item["status"] == "PASS"]),
            "module_reports": module_reports,
            "infrastructure_reports": infrastructure_reports,
            "platform_status": platform_summary["status"],
            "compile_check_status": compile_status,
            "boot_check_status": boot_status,
            "generated_project_root": str(self.generated_project_root),
        }
        dump_yaml(self.generated_project_root / "logs" / "project-assembly-report.yaml", report)
        return {
            "report": report,
            "platform_summary": platform_summary,
            "module_reports": module_reports,
            "infrastructure_reports": infrastructure_reports,
            "verification": verification,
        }

    def _prepare_project_baseline(self, plan: dict[str, Any]) -> dict[str, Any]:
        modules = plan.get("module_sequence", [])
        if not modules:
            raise RuntimeError("project-assembly-plan.yaml must define at least one module entry")

        first_module = modules[0]
        module_schema_name = str(first_module.get("module_schema", "module-schema.resolved.yaml"))
        module_spec_name = str(first_module.get("module_spec", "module-spec.yaml"))
        baseline_run_root = self.run_root / "_baseline"
        lowering_summary = IRLoweringPipeline(
            output_root=baseline_run_root,
            specs_dir=self.specs_dir,
        ).run(
            module_schema_name=module_schema_name,
            module_spec_name=module_spec_name,
        )
        field_schema_path = baseline_run_root / "generated-ir" / "field-schema.generated.yaml"
        assembler = BackendAssembler(
            project_root=self.project_root,
            backend_root=self.backend_root,
            run_root=self.run_root,
            specs_dir=self.specs_dir,
        )
        platform_summary = assembler._prepare_backend_baseline(field_schema_path)
        dump_yaml(
            self.generated_project_root / "logs" / "project-baseline-report.yaml",
            {
                "status": platform_summary["status"],
                "baseline_module": first_module.get("module"),
                "baseline_lowering_status": lowering_summary["status"],
                "assembly_mode": platform_summary["assembly_mode"],
            },
        )
        return platform_summary

    def _merge_module_output(self, module_key: str, module_output_root: Path) -> dict[str, Any]:
        merged_files: list[str] = []
        conflicts: list[dict[str, Any]] = []
        for relative_root in [Path("src/main/java"), Path("src/main/resources")]:
            source_root = module_output_root / relative_root
            if not source_root.exists():
                continue
            for source_file in sorted(source_root.rglob("*")):
                if not source_file.is_file():
                    continue
                if "logs" in source_file.parts:
                    continue
                relative_path = source_file.relative_to(module_output_root)
                destination = self.generated_project_root / relative_path
                if destination.exists():
                    if source_file.read_bytes() != destination.read_bytes():
                        conflicts.append(
                            {
                                "module": module_key,
                                "path": relative_path.as_posix(),
                                "reason": "artifact-content-conflict",
                            }
                        )
                        continue
                else:
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(source_file, destination)
                merged_files.append(relative_path.as_posix())

        module_logs_root = module_output_root / "logs"
        if module_logs_root.exists():
            destination_logs_root = self.generated_project_root / "logs" / "modules" / module_key
            for log_file in sorted(module_logs_root.rglob("*")):
                if not log_file.is_file():
                    continue
                destination = destination_logs_root / log_file.relative_to(module_logs_root)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(log_file, destination)

        report = {
            "status": "FAIL" if conflicts else "PASS",
            "module": module_key,
            "merged_file_count": len(merged_files),
            "merged_files_sample": merged_files[:50],
            "conflict_count": len(conflicts),
            "conflicts": conflicts,
        }
        dump_yaml(self.generated_project_root / "logs" / "modules" / module_key / "merge-report.yaml", report)
        return report

    def _resolve_spec_path(self, raw_path: str, base_dir: Path) -> Path:
        candidate = Path(raw_path)
        if candidate.is_absolute():
            return candidate
        if candidate.exists():
            return candidate
        return base_dir / raw_path
