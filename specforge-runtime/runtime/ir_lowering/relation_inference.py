from __future__ import annotations

from typing import Any

from .naming_resolution import NamingResolution


class RelationInference:
    def __init__(self, naming: NamingResolution) -> None:
        self.naming = naming

    def infer(self, module_schema: dict[str, Any], entities: dict[str, dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        referential_rules = module_schema.get("validation_rules", {}).get("referential", [])
        referential_map = {
            tuple(rule["source"].split(".", 1)): tuple(rule["target"].split(".", 1))
            for rule in referential_rules
        }
        result: dict[str, list[dict[str, Any]]] = {}
        for entity in module_schema.get("entity_graph", {}).get("entities", []):
            entity_name = entity["entity_id"]
            relations: list[dict[str, Any]] = []
            for relation in entity.get("relations", []):
                target = relation["target"]
                relation_type = relation["relation"].replace("-", "_")
                if relation_type == "many_to_one":
                    self_field, target_field = self._many_to_one_binding(entity_name, target, referential_map)
                    relations.append(
                        {
                            "type": relation_type,
                            "target": target,
                            "self_field": self_field,
                            "target_field": target_field,
                        }
                    )
                elif relation_type == "one_to_many":
                    target_bindings = self._reverse_many_to_one(target, entity_name, referential_map)
                    relations.append(
                        {
                            "type": relation_type,
                            "target": target,
                            "self_field": target_bindings[1],
                            "target_field": target_bindings[0],
                        }
                    )
            result[entity_name] = relations
        return result

    def _many_to_one_binding(
        self,
        entity_name: str,
        target: str,
        referential_map: dict[tuple[str, str], tuple[str, str]],
    ) -> tuple[str, str]:
        for (source_entity, source_field), (target_entity, target_field) in referential_map.items():
            if source_entity == entity_name and target_entity == target:
                return (
                    self.naming.field_name_from_column(entity_name, source_field),
                    self.naming.field_name_from_column(target, target_field),
                )
        default_self = self.naming.to_camel_case(target) + "Id"
        return default_self, "id"

    def _reverse_many_to_one(
        self,
        child_entity: str,
        parent_entity: str,
        referential_map: dict[tuple[str, str], tuple[str, str]],
    ) -> tuple[str, str]:
        for (source_entity, source_field), (target_entity, target_field) in referential_map.items():
            if source_entity == child_entity and target_entity == parent_entity:
                return (
                    self.naming.field_name_from_column(child_entity, source_field),
                    self.naming.field_name_from_column(parent_entity, target_field),
                )
        return self.naming.to_camel_case(parent_entity) + "Id", "id"
