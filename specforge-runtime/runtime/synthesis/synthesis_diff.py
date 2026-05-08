from __future__ import annotations

from typing import Any


class SynthesisDiffBuilder:
    def build(self, context: dict[str, Any], emitter_results: list[dict[str, Any]], validation: dict[str, Any], compile_check: dict[str, Any]) -> dict[str, Any]:
        return {
            "module_name": context["schema"]["module"]["name"],
            "entity_count": len(context["schema"].get("entities", {})),
            "artifact_count": sum(result.get("artifact_count", 0) for result in emitter_results),
            "emitter_names": [result["emitter"] for result in emitter_results],
            "relation_bindings": context["relations"],
            "validation_status": validation["status"],
            "compile_check_status": compile_check["status"],
        }
