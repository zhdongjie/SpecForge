from __future__ import annotations

from pathlib import Path
from typing import Any

from runtime.codegen.common import dump_yaml, safe_load_yaml

from .audit_lowering import AuditLowering
from .capability_expander import CapabilityExpander
from .canonicalizer import LoweringCanonicalizer
from .dto_contract_lowering import DtoContractLowering
from .entity_inference import EntityInference
from .lowering_diff import LoweringDiffBuilder
from .lowering_validator import LoweringValidator
from .module_to_field_lowering import ModuleToFieldLowering
from .naming_resolution import NamingResolution
from .pagination_lowering import PaginationLowering
from .permission_lowering import PermissionLowering
from .relation_inference import RelationInference
from .validation_lowering import ValidationLowering


class IRLoweringPipeline:
    def __init__(self, output_root: Path, specs_dir: Path) -> None:
        self.output_root = output_root
        self.specs_dir = specs_dir

    def run(self, module_schema_name: str = "module-schema.resolved.yaml") -> dict[str, Any]:
        module_schema_path = self._resolve_input(module_schema_name)
        module_schema = safe_load_yaml(module_schema_path)
        module_spec = safe_load_yaml(self.specs_dir / "module-spec.yaml")
        enriched_schema = self._merge_with_module_spec(module_schema, module_spec)

        naming = NamingResolution()
        canonical = LoweringCanonicalizer().canonicalize(enriched_schema)
        expanded = CapabilityExpander().expand(canonical)
        entities = EntityInference(naming).infer(canonical, expanded)
        relations = RelationInference(naming).infer(canonical, entities)
        validation = ValidationLowering().lower(canonical, entities)
        permissions = PermissionLowering().lower(canonical, expanded)
        dto_contracts = DtoContractLowering().lower(expanded)
        pagination = PaginationLowering().lower(expanded, entities)
        audit = AuditLowering().lower(canonical, entities)
        generated_schema = ModuleToFieldLowering(naming).lower(
            canonical,
            expanded,
            self._canonicalize_field_order(entities),
            relations,
            validation,
            permissions,
            dto_contracts,
            pagination,
            audit,
        )

        validation_report = LoweringValidator().validate(generated_schema)
        diff_report = LoweringDiffBuilder().build(generated_schema, validation_report)

        output_file = self.output_root / "generated-ir" / "field-schema.generated.yaml"
        dump_yaml(output_file, generated_schema)
        dump_yaml(self.output_root / "generated-ir" / "logs" / "lowering-validation.yaml", validation_report)
        dump_yaml(self.output_root / "generated-ir" / "logs" / "lowering-diff.yaml", diff_report)
        report = {
            "module_name": generated_schema["module"]["name"],
            "status": validation_report["status"],
            "output_file": str(output_file),
            "entity_count": len(generated_schema.get("entities", {})),
            "permission_count": len(generated_schema.get("permissions", [])),
        }
        dump_yaml(self.output_root / "generated-ir" / "logs" / "lowering-report.yaml", report)
        return report

    def _resolve_input(self, module_schema_name: str) -> Path:
        candidate = Path(module_schema_name)
        if candidate.exists():
            return candidate
        return self.specs_dir / module_schema_name

    def _merge_with_module_spec(
        self,
        module_schema: dict[str, Any],
        module_spec: dict[str, Any],
    ) -> dict[str, Any]:
        merged = dict(module_schema)
        for key in [
            "api_groups",
            "capabilities",
            "entity_graph",
            "validation_rules",
            "architecture_constraints",
            "persistence_conventions",
            "localization_requirements",
            "audit_behavior",
        ]:
            if key not in merged and key in module_spec:
                merged[key] = module_spec[key]
        if "module_identity" in module_spec and "module_identity" in merged:
            merged["module_identity"] = {**module_spec["module_identity"], **merged["module_identity"]}
        elif "module_identity" not in merged and "module_identity" in module_spec:
            merged["module_identity"] = module_spec["module_identity"]
        return merged

    def _canonicalize_field_order(self, entities: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        normalized: dict[str, dict[str, Any]] = {}
        for entity_name, payload in sorted(entities.items()):
            fields = sorted(payload["fields"], key=lambda field: (field["name"] != "id", field["name"]))
            normalized[entity_name] = {**payload, "fields": fields}
        return normalized
