from __future__ import annotations

from pathlib import Path
from typing import Any


class MutationDiffBuilder:
    def build(
        self,
        mutation_spec: dict[str, Any],
        artifact_records: list[dict[str, Any]],
        validation_report: dict[str, Any],
        compile_report: dict[str, Any],
    ) -> dict[str, Any]:
        semantic_mutations = mutation_spec.get("semantic_mutations", {})
        return {
            "source_module": mutation_spec.get("source_module"),
            "target_module": mutation_spec.get("target_module", {}).get("name"),
            "renamed_entities": semantic_mutations.get("entities", {}),
            "renamed_routes": semantic_mutations.get("routes", {}),
            "renamed_permissions": semantic_mutations.get("permissions", {}),
            "renamed_tables": semantic_mutations.get("tables", {}),
            "rewritten_artifacts": [
                {
                    "source": record["source_relative_path"],
                    "target": record["destination_relative_path"],
                }
                for record in artifact_records
            ],
            "preserved_invariants": [
                "architecture-boundaries",
                "crud-semantics",
                "security-model",
                "validation-conventions",
                "package-structure",
            ],
            "validation_status": validation_report.get("status"),
            "compile_verification_status": compile_report.get("status"),
        }
