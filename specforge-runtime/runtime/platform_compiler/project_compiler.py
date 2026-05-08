from __future__ import annotations

from pathlib import Path
from typing import Any

from runtime.codegen.common import dump_yaml
from runtime.ir_lowering import IRLoweringPipeline

from .backend_assembler import BackendAssembler
from .project_assembly_compiler import ProjectAssemblyCompiler


class ProjectCompiler:
    def __init__(self, project_root: Path, backend_root: Path, run_root: Path, specs_dir: Path) -> None:
        self.project_root = project_root
        self.backend_root = backend_root
        self.run_root = run_root
        self.specs_dir = specs_dir

    def run(
        self,
        module_schema_name: str = "module-schema.resolved.yaml",
        module_spec_name: str = "module-spec.yaml",
        project_assembly_plan_name: str | None = None,
        run_compile: bool = True,
        run_boot: bool = True,
    ) -> dict[str, Any]:
        if project_assembly_plan_name:
            assembly = ProjectAssemblyCompiler(
                project_root=self.project_root,
                backend_root=self.backend_root,
                run_root=self.run_root,
                specs_dir=self.specs_dir,
            ).run(
                project_assembly_plan_name=project_assembly_plan_name,
                run_compile=run_compile,
                run_boot=run_boot,
            )
            report = assembly["report"]
            summary = {
                "status": report["status"],
                "lowering_status": "MULTI_MODULE",
                "assembly_status": report["status"],
                "generated_project_root": str(self.run_root / "generated-project"),
                "project_assembly_plan": project_assembly_plan_name,
                "module_count": report["module_count"],
            }
            dump_yaml(self.run_root / "logs" / "project-compiler-report.yaml", summary)
            return summary

        lowering_summary = IRLoweringPipeline(
            output_root=self.run_root,
            specs_dir=self.specs_dir,
        ).run(module_schema_name=module_schema_name, module_spec_name=module_spec_name)
        field_schema_path = self.run_root / "generated-ir" / "field-schema.generated.yaml"
        assembly = BackendAssembler(
            project_root=self.project_root,
            backend_root=self.backend_root,
            run_root=self.run_root,
            specs_dir=self.specs_dir,
        ).assemble(field_schema_path=field_schema_path, run_compile=run_compile, run_boot=run_boot)
        if lowering_summary["status"] == "FAIL" or assembly["report"]["status"] == "FAIL":
            status = "FAIL"
        elif assembly["report"]["status"] == "BLOCKED":
            status = "BLOCKED"
        else:
            status = "PASS"
        summary = {
            "status": status,
            "lowering_status": lowering_summary["status"],
            "assembly_status": assembly["report"]["status"],
            "generated_project_root": str(self.run_root / "generated-project"),
            "module_schema": module_schema_name,
            "module_spec": module_spec_name,
        }
        dump_yaml(self.run_root / "logs" / "project-compiler-report.yaml", summary)
        return summary
