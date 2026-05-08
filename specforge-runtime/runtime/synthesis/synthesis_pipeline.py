from __future__ import annotations

from pathlib import Path
from typing import Any

from runtime.codegen.common import dump_yaml, safe_load_yaml

from .controller_synthesizer import ControllerSynthesizer
from .dto_synthesizer import DtoSynthesizer
from .entity_synthesizer import EntitySynthesizer
from .field_type_system import FieldTypeSystem
from .mapper_synthesizer import MapperSynthesizer
from .naming_canonicalizer import NamingCanonicalizer
from .permission_synthesizer import PermissionSynthesizer
from .relation_synthesizer import RelationSynthesizer
from .service_synthesizer import ServiceSynthesizer
from .sql_synthesizer import SqlSynthesizer
from .synthesis_diff import SynthesisDiffBuilder
from .synthesis_validator import SynthesisValidator
from .validation_synthesizer import ValidationSynthesizer


class SynthesisPipeline:
    def __init__(self, project_root: Path, backend_root: Path, output_root: Path, specs_dir: Path) -> None:
        self.project_root = project_root
        self.backend_root = backend_root
        self.output_root = output_root
        self.specs_dir = specs_dir

    def run(self, verify_compile: bool = False, field_schema_name: str = "field-schema.resolved.yaml") -> dict[str, Any]:
        candidate = Path(field_schema_name)
        schema_path = candidate if candidate.exists() else (self.specs_dir / field_schema_name)
        schema = safe_load_yaml(schema_path)
        naming = NamingCanonicalizer()
        field_type_system = FieldTypeSystem()
        validation_synthesizer = ValidationSynthesizer()
        relations = RelationSynthesizer(naming).resolve(schema)

        module_name = naming.to_pascal_case(schema["module"]["name"].replace("-", " ").title().replace(" ", ""))
        context = {
            "project_root": self.project_root,
            "backend_root": self.backend_root,
            "output_root": self.output_root,
            "schema": schema,
            "module_name": module_name,
            "package_root": schema["module"]["package_root"],
            "naming": naming,
            "field_type_system": field_type_system,
            "validation_synthesizer": validation_synthesizer,
            "relations": relations,
        }

        permission_result = PermissionSynthesizer().emit(context)
        context["permission_class"] = permission_result["permission_class"]
        emitters = [
            ("permission-synthesizer", permission_result),
            ("entity-synthesizer", EntitySynthesizer().emit(context)),
            ("dto-synthesizer", DtoSynthesizer().emit(context)),
            ("mapper-synthesizer", MapperSynthesizer().emit(context)),
            ("service-synthesizer", ServiceSynthesizer().emit(context)),
            ("controller-synthesizer", ControllerSynthesizer().emit(context)),
            ("sql-synthesizer", SqlSynthesizer().emit(context)),
        ]
        emitter_results = [{"emitter": name, **result} for name, result in emitters]

        manifest = {
            "module_name": schema["module"]["name"],
            "package_root": schema["module"]["package_root"],
            "bounded_context": schema["module"]["bounded_context"],
            "artifact_count": sum(result["artifact_count"] for _, result in emitters),
            "emitters": emitter_results,
            "relations": relations,
        }
        dump_yaml(self.output_root / "logs" / "synthesis-manifest.yaml", manifest)

        validator = SynthesisValidator(context)
        validation = validator.validate()
        compile_check = validator.compile_check() if verify_compile else {"status": "SKIPPED"}
        diff = SynthesisDiffBuilder().build(context, emitter_results, validation, compile_check)
        dump_yaml(self.output_root / "logs" / "synthesis-diff.yaml", diff)

        report = {
            "module_name": schema["module"]["name"],
            "status": "PASS" if validation["status"] == "PASS" and compile_check["status"] != "FAIL" else "FAIL",
            "output_root": str(self.output_root),
            "artifact_count": manifest["artifact_count"],
            "validation_status": validation["status"],
            "compile_check_status": compile_check["status"],
        }
        dump_yaml(self.output_root / "logs" / "synthesis-report.yaml", report)
        return report
