from __future__ import annotations

import json
from typing import Any


class LoweringValidator:
    def validate(self, generated_schema: dict[str, Any]) -> dict[str, Any]:
        findings: list[dict[str, Any]] = []
        entities = generated_schema.get("entities", {})
        permissions = generated_schema.get("permissions", [])
        route_segments = [payload.get("route_segment") for payload in entities.values() if payload.get("route_segment")]

        if len(set(permissions)) != len(permissions):
            findings.append({"code": "permission-duplication", "status": "FAIL", "details": "Permission identifiers must be unique"})
        if len(set(route_segments)) != len(route_segments):
            findings.append({"code": "route-duplication", "status": "FAIL", "details": "Route segments must be unique"})
        for entity_name, payload in sorted(entities.items()):
            field_names = [field["name"] for field in payload.get("fields", [])]
            if field_names != sorted(field_names, key=lambda value: (value != "id", value)):
                findings.append(
                    {
                        "code": "field-order-instability",
                        "status": "FAIL",
                        "details": f"{entity_name} field ordering is not canonical",
                    }
                )
            relation_targets = {relation["target"] for relation in payload.get("relations", [])}
            missing = sorted(target for target in relation_targets if target not in entities)
            if missing:
                findings.append(
                    {
                        "code": "relation-orphan",
                        "status": "FAIL",
                        "details": f"{entity_name} references missing targets: {', '.join(missing)}",
                    }
                )

        signature = json.dumps(generated_schema, sort_keys=True, separators=(",", ":"))
        return {
            "status": "PASS" if not findings else "FAIL",
            "finding_count": len(findings),
            "findings": findings,
            "deterministic_signature": signature,
        }
