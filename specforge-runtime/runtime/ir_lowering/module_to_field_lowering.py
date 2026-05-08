from __future__ import annotations

from typing import Any

from .naming_resolution import NamingResolution


class ModuleToFieldLowering:
    def __init__(self, naming: NamingResolution) -> None:
        self.naming = naming

    def lower(
        self,
        module_schema: dict[str, Any],
        expanded: dict[str, Any],
        entities: dict[str, dict[str, Any]],
        relations: dict[str, list[dict[str, Any]]],
        validation: dict[str, Any],
        permissions: dict[str, Any],
        dto_contracts: dict[str, Any],
        pagination: dict[str, Any],
        audit: dict[str, Any],
    ) -> dict[str, Any]:
        route_prefixes = [aggregate_info["route_prefix"] for aggregate_info in expanded["aggregates"].values()]
        route_base = self.naming.common_route_base(route_prefixes)
        database = module_schema.get("persistence_conventions", {}).get("database", "unknown")
        response_bindings = module_schema.get("architectural_bindings", {}).get("response_bindings", {})

        lowered_entities: dict[str, dict[str, Any]] = {}
        for entity_name, entity_payload in sorted(entities.items()):
            aggregate_info = expanded["aggregates"].get(entity_name)
            authorities = aggregate_info["authorities"] if aggregate_info else []
            route_prefix = aggregate_info["route_prefix"] if aggregate_info else ""
            lowered_entities[entity_name] = {
                "table": entity_payload["table"],
                "description": entity_payload["description"],
                "aggregate_role": entity_payload["aggregate_role"],
                "route_segment": self.naming.relative_route_segment(route_prefix, route_base) if route_prefix else None,
                "permission_namespace": self.naming.permission_namespace(authorities),
                "fields": entity_payload["fields"],
                "relations": relations.get(entity_name, []),
                "dto_contract": dto_contracts["dto_contracts"].get(entity_name),
            }

        return {
            "module": {
                "name": module_schema["module_identity"]["module_name"],
                "bounded_context": module_schema.get("module_identity", {}).get(
                    "bounded_context",
                    module_schema.get("resolution_context", {}).get("bounded_context"),
                ),
                "package_root": module_schema["module_identity"]["package_root"],
                "route_base": route_base,
                "database": database,
            },
            "entities": lowered_entities,
            "permissions": permissions["permissions"],
            "validation_contracts": validation["validation_contracts"],
            "architecture_contract": {
                "manager_boundary": True,
                "response_wrapper": response_bindings.get("wrapper_type", "ResponseVo"),
                "pagination_wrapper": response_bindings.get("page_type", "PageVo"),
                "primary_key_entity": "PrimaryKeyEntity",
                "service_impl_base": "ServiceImpl",
                "mapper_base": "BaseMapper",
            },
            "pagination_contract": pagination["pagination_contract"],
            "audit_contract": audit["audit_contract"],
            "permission_families": permissions["permission_families"],
            "dto_contracts": dto_contracts["dto_contracts"],
        }
