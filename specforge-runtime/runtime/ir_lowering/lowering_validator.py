from __future__ import annotations

import json
from typing import Any


class LoweringValidator:
    def validate(self, generated_schema: dict[str, Any]) -> dict[str, Any]:
        findings: list[dict[str, Any]] = []
        module = generated_schema.get("module", {})
        entities = generated_schema.get("entities", {})
        permissions = generated_schema.get("permissions", [])
        semantic_role = module.get("semantic_role", "")
        route_segments = [payload.get("route_segment") for payload in entities.values() if payload.get("route_segment")]
        permission_namespaces = [
            payload.get("permission_namespace")
            for payload in entities.values()
            if payload.get("permission_namespace")
        ]

        if len(set(permissions)) != len(permissions):
            findings.append({"code": "permission-duplication", "status": "FAIL", "details": "Permission identifiers must be unique"})
        if len(set(route_segments)) != len(route_segments):
            findings.append({"code": "route-duplication", "status": "FAIL", "details": "Route segments must be unique"})

        if semantic_role == "business-domain":
            resource_entities = {
                entity_name: payload
                for entity_name, payload in sorted(entities.items())
                if self._requires_business_surface(payload)
            }
            if not permissions:
                findings.append(
                    {
                        "code": "business-permission-generation-missing",
                        "status": "FAIL",
                        "details": "Business-domain lowering must emit non-empty module permissions",
                    }
                )
            if not route_segments:
                findings.append(
                    {
                        "code": "business-route-generation-missing",
                        "status": "FAIL",
                        "details": "Business-domain lowering must emit non-empty entity route segments",
                    }
                )
            if not resource_entities:
                findings.append(
                    {
                        "code": "business-resource-entity-missing",
                        "status": "FAIL",
                        "details": "Business-domain lowering must retain at least one DTO-backed resource entity",
                    }
                )
            for entity_name, payload in resource_entities.items():
                if not payload.get("route_segment"):
                    findings.append(
                        {
                            "code": "business-entity-route-missing",
                            "status": "FAIL",
                            "details": f"{entity_name} is missing route_segment after lowering",
                        }
                    )
                if not payload.get("permission_namespace"):
                    findings.append(
                        {
                            "code": "business-entity-permission-namespace-missing",
                            "status": "FAIL",
                            "details": f"{entity_name} is missing permission_namespace after lowering",
                        }
                    )
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
            "route_segment_count": len(route_segments),
            "permission_count": len(permissions),
            "permission_namespace_count": len(permission_namespaces),
            "deterministic_signature": signature,
        }

    def _requires_business_surface(self, payload: dict[str, Any]) -> bool:
        dto_contract = payload.get("dto_contract")
        return isinstance(dto_contract, dict) and bool(dto_contract)
