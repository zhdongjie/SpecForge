from __future__ import annotations

from typing import Any


class LoweringDiffBuilder:
    def build(self, generated_schema: dict[str, Any], validation: dict[str, Any]) -> dict[str, Any]:
        entities = generated_schema.get("entities", {})
        return {
            "module_name": generated_schema.get("module", {}).get("name"),
            "entity_count": len(entities),
            "entity_fields": {
                entity_name: [field["name"] for field in payload.get("fields", [])]
                for entity_name, payload in sorted(entities.items())
            },
            "relation_graph": {
                entity_name: payload.get("relations", [])
                for entity_name, payload in sorted(entities.items())
            },
            "permission_count": len(generated_schema.get("permissions", [])),
            "validation_status": validation["status"],
        }
