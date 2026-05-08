from __future__ import annotations

from typing import Any

from .naming_canonicalizer import NamingCanonicalizer


class RelationSynthesizer:
    def __init__(self, naming: NamingCanonicalizer) -> None:
        self.naming = naming

    def resolve(self, schema: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
        entities = schema.get("entities", {})
        resolved: dict[str, list[dict[str, Any]]] = {}
        for entity_name, entity_spec in entities.items():
            relations: list[dict[str, Any]] = []
            for relation in entity_spec.get("relations", []):
                target = relation["target"]
                if target not in entities:
                    raise ValueError(f"Relation target {target} does not exist for {entity_name}")
                target_spec = entities[target]
                target_summary_vo = f"{target}ListVo"
                relation_type = relation["type"]
                relation_record = {
                    "type": relation_type,
                    "target": target,
                    "self_field": relation["self_field"],
                    "target_field": relation["target_field"],
                    "target_table": target_spec["table"],
                    "target_summary_vo": target_summary_vo,
                    "property_name": self._property_name(relation_type, target),
                    "select_columns": self._select_columns(target_spec),
                }
                relations.append(relation_record)
            resolved[entity_name] = relations
        return resolved

    def _property_name(self, relation_type: str, target: str) -> str:
        singular = self.naming.to_camel_case(target)
        if relation_type in {"one_to_many", "many_to_many"}:
            return self.naming.pluralize(singular)
        return singular

    def _select_columns(self, target_spec: dict[str, Any]) -> str:
        columns: list[str] = []
        for field in target_spec.get("fields", []):
            if field["name"] == "id":
                columns.append("id")
                continue
            if len(columns) >= 4:
                break
            columns.append(self.naming.to_snake_case(field["name"]))
        return ", ".join(columns)
