from __future__ import annotations

from collections import defaultdict
from typing import Any


class CapabilityExpander:
    def expand(self, module_schema: dict[str, Any]) -> dict[str, Any]:
        capabilities = module_schema.get("capabilities", [])
        api_groups = {group["group_id"]: group for group in module_schema.get("api_groups", [])}
        by_aggregate: dict[str, dict[str, Any]] = {}
        validation_caps: list[dict[str, Any]] = []
        for capability in capabilities:
            group_id = capability["api_group"]
            group = api_groups[group_id]
            aggregate = group["aggregate"]
            aggregate_record = by_aggregate.setdefault(
                aggregate,
                {
                    "aggregate": aggregate,
                    "group_id": group_id,
                    "route_prefix": group["route_prefix"],
                    "capabilities": [],
                    "authorities": [],
                    "patterns": set(),
                    "touched_entities": set(),
                },
            )
            aggregate_record["capabilities"].append(capability)
            aggregate_record["authorities"].append(capability["authority"])
            aggregate_record["patterns"].add(capability["deterministic_pattern"])
            aggregate_record["touched_entities"].update(capability.get("touched_entities", []))
            if capability["deterministic_pattern"] == "uniqueness-check":
                validation_caps.append(capability)

        return {
            "aggregates": {
                key: {
                    **value,
                    "capabilities": sorted(value["capabilities"], key=lambda item: item["capability_id"]),
                    "authorities": sorted(set(value["authorities"])),
                    "patterns": sorted(value["patterns"]),
                    "touched_entities": sorted(value["touched_entities"]),
                }
                for key, value in sorted(by_aggregate.items(), key=lambda item: item[0])
            },
            "validation_capabilities": sorted(validation_caps, key=lambda item: item["capability_id"]),
        }
