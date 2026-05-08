from __future__ import annotations

from copy import deepcopy
from typing import Any


class LoweringCanonicalizer:
    def canonicalize(self, module_schema: dict[str, Any]) -> dict[str, Any]:
        payload = deepcopy(module_schema)
        payload["api_groups"] = sorted(payload.get("api_groups", []), key=lambda item: item["group_id"])
        payload["capabilities"] = sorted(payload.get("capabilities", []), key=lambda item: item["capability_id"])
        entity_graph = payload.get("entity_graph", {})
        entity_graph["entities"] = sorted(entity_graph.get("entities", []), key=lambda item: item["entity_id"])
        for entity in entity_graph.get("entities", []):
            entity["relations"] = sorted(entity.get("relations", []), key=lambda item: (item["target"], item["relation"]))
        validation_rules = payload.get("validation_rules", {})
        validation_rules["uniqueness"] = sorted(validation_rules.get("uniqueness", []), key=lambda item: item["rule_id"])
        validation_rules["referential"] = sorted(validation_rules.get("referential", []), key=lambda item: item["rule_id"])
        validation_rules["shape"] = sorted(validation_rules.get("shape", []), key=lambda item: item["rule_id"])
        localization = payload.get("localization_requirements", {})
        localized_fields = localization.get("localized_fields", {})
        localization["localized_fields"] = {
            key: sorted(value)
            for key, value in sorted(localized_fields.items(), key=lambda item: item[0])
        }
        return payload
