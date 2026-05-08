from __future__ import annotations

from pathlib import Path
from typing import Any

from runtime.codegen.common import dump_yaml
from runtime.ir_lowering import IRLoweringPipeline

from .backend_assembler import BackendAssembler


class ProjectCompiler:
    def __init__(self, project_root: Path, backend_root: Path, run_root: Path, specs_dir: Path) -> None:
        self.project_root = project_root
        self.backend_root = backend_root
        self.run_root = run_root
        self.specs_dir = specs_dir

    def run(
        self,
        module_schema_name: str = "module-schema.resolved.yaml",
        run_compile: bool = True,
        run_boot: bool = True,
    ) -> dict[str, Any]:
        lowering_summary = IRLoweringPipeline(
            output_root=self.run_root,
            specs_dir=self.specs_dir,
        ).run(module_schema_name=module_schema_name)
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
        }
        dump_yaml(self.run_root / "logs" / "project-compiler-report.yaml", summary)
        return summary
