from __future__ import annotations

from pathlib import Path
from typing import Any

from .common import CodegenContext, dump_yaml, safe_load_yaml
from .controller_emitter import ControllerEmitter
from .dto_emitter import DtoEmitter
from .entity_emitter import EntityEmitter
from .mapper_emitter import MapperEmitter
from .service_emitter import ServiceEmitter
from .sql_emitter import SqlEmitter
from .validator import CodegenValidator


class CodegenPipeline:
    def __init__(
        self,
        project_root: Path,
        backend_root: Path,
        output_root: Path,
        specs_dir: Path,
    ) -> None:
        self.project_root = project_root
        self.backend_root = backend_root
        self.output_root = output_root
        self.specs_dir = specs_dir

    def run(self, verify_compile: bool = False) -> dict[str, Any]:
        module_spec = safe_load_yaml(self.specs_dir / "module-spec.yaml")
        resolved_schema = safe_load_yaml(self.specs_dir / "module-schema.resolved.yaml")
        context = CodegenContext(
            project_root=self.project_root,
            backend_root=self.backend_root,
            output_root=self.output_root,
            module_spec=module_spec,
            resolved_schema=resolved_schema,
        )

        emitters = [
            EntityEmitter(),
            MapperEmitter(),
            DtoEmitter(),
            ServiceEmitter(),
            ControllerEmitter(),
            SqlEmitter(),
        ]
        results = [emitter.emit(context) for emitter in emitters]

        manifest = {
            "module_name": resolved_schema["module_identity"]["module_name"],
            "package_root": resolved_schema["module_identity"]["package_root"],
            "output_root": str(self.output_root),
            "emitters": results,
        }
        dump_yaml(self.output_root / "logs" / "codegen-manifest.yaml", manifest)

        validator = CodegenValidator(context)
        validation = validator.validate(results)
        compile_check = validator.compile_check() if verify_compile else {"status": "SKIPPED"}

        summary = {
            "module_name": resolved_schema["module_identity"]["module_name"],
            "status": "PASS" if validation["status"] == "PASS" and compile_check["status"] != "FAIL" else "FAIL",
            "artifact_count": sum(result["artifact_count"] for result in results),
            "validation_status": validation["status"],
            "compile_check_status": compile_check["status"],
            "output_root": str(self.output_root),
        }
        dump_yaml(self.output_root / "logs" / "codegen-summary.yaml", summary)
        return summary
