from __future__ import annotations

from typing import Any


class ValidationLowering:
    def lower(self, module_schema: dict[str, Any], entities: dict[str, dict[str, Any]]) -> dict[str, Any]:
        rules = module_schema.get("validation_rules", {})
        contracts: list[str] = []
        unique_indexes: list[dict[str, Any]] = []
        for rule in rules.get("uniqueness", []):
            contracts.append(rule["rule_id"])
            unique_indexes.append(
                {
                    "rule_id": rule["rule_id"],
                    "scope": rule["scope"],
                }
            )
        for rule in rules.get("referential", []):
            contracts.append(rule["rule_id"])
        for rule in rules.get("shape", []):
            contracts.append(rule["rule_id"])
        contracts.extend(
            [
                "deterministic-field-ordering",
                "route-uniqueness",
                "permission-uniqueness",
            ]
        )
        return {
            "validation_contracts": sorted(set(contracts)),
            "unique_indexes": unique_indexes,
        }
