from __future__ import annotations

from collections import OrderedDict
from typing import Any

from .naming_resolution import NamingResolution


class EntityInference:
    def __init__(self, naming: NamingResolution) -> None:
        self.naming = naming

    def infer(self, module_schema: dict[str, Any], expanded: dict[str, Any]) -> dict[str, dict[str, Any]]:
        entities: dict[str, dict[str, Any]] = {}
        entity_specs = {
            entity["entity_id"]: entity
            for entity in module_schema.get("entity_graph", {}).get("entities", [])
        }
        unique_rules = module_schema.get("validation_rules", {}).get("uniqueness", [])
        referential_rules = module_schema.get("validation_rules", {}).get("referential", [])
        localized_fields = module_schema.get("localization_requirements", {}).get("localized_fields", {})

        for entity_name, entity_spec in sorted(entity_specs.items()):
            aggregate_role = entity_spec.get("aggregate_role", "owned")
            inferred_fields: "OrderedDict[str, dict[str, Any]]" = OrderedDict()
            self._add_field(inferred_fields, "id", {"name": "id", "type": "long", "primary_key": True})

            for rule in unique_rules:
                table_name = self._scope_table(rule["scope"])
                if table_name != entity_spec["table"]:
                    continue
                scope_columns = self._scope_columns(rule["scope"])
                for column in scope_columns:
                    field_name = self.naming.field_name_from_column(entity_name, column)
                    self._add_field(
                        inferred_fields,
                        field_name,
                        self._column_contract(
                            entity_name,
                            field_name,
                            column,
                            unique=len(scope_columns) == 1,
                        ),
                    )

            for rule in referential_rules:
                source_entity, source_field = rule["source"].split(".", 1)
                if source_entity != entity_name:
                    continue
                field_name = self.naming.field_name_from_column(entity_name, source_field)
                self._add_field(
                    inferred_fields,
                    field_name,
                    self._column_contract(entity_name, field_name, source_field, required=True),
                )

            if aggregate_role in {"root", "child-root"}:
                aggregate_info = expanded["aggregates"].get(entity_name, {})
                for pattern in aggregate_info.get("patterns", []):
                    if pattern in {"page", "list"}:
                        self._inject_admin_support_fields(entity_name, inferred_fields)

            if aggregate_role == "translation-child":
                parent = self._translation_parent(entity_spec)
                parent_field = self.naming.to_camel_case(parent) + "Id"
                self._add_field(
                    inferred_fields,
                    parent_field,
                    {"name": parent_field, "type": "long", "required": True},
                )
                self._add_field(
                    inferred_fields,
                    "languageCode",
                    {"name": "languageCode", "type": "string", "required": True, "max_length": 16},
                )
                for localized_column in localized_fields.get(parent, []):
                    field_name = self.naming.field_name_from_column(parent, localized_column)
                    self._add_field(
                        inferred_fields,
                        field_name,
                        self._column_contract(parent, field_name, localized_column, required=True),
                    )

            entities[entity_name] = {
                "table": entity_spec["table"],
                "description": self.naming.entity_label(entity_name),
                "aggregate_role": aggregate_role,
                "fields": list(inferred_fields.values()),
                "field_sources": {
                    field_name: field_contract.get("inference_source", "inferred")
                    for field_name, field_contract in inferred_fields.items()
                },
            }
        return entities

    def _inject_admin_support_fields(self, entity_name: str, inferred_fields: OrderedDict[str, dict[str, Any]]) -> None:
        status_field = self.naming.to_camel_case(entity_name) + "Status"
        self._add_field(
            inferred_fields,
            "sort",
            {"name": "sort", "type": "integer", "required": True, "inference_source": "pagination-lowering"},
        )
        self._add_field(
            inferred_fields,
            status_field,
            {
                "name": status_field,
                "type": "enum",
                "required": True,
                "enum_values": ["ENABLED", "DISABLED"],
                "inference_source": "status-pattern-lowering",
            },
        )

    def _column_contract(
        self,
        entity_name: str,
        field_name: str,
        column_name: str,
        unique: bool = False,
        required: bool = True,
    ) -> dict[str, Any]:
        contract = {
            "name": field_name,
            "type": "string",
            "required": required,
            "inference_source": f"column-scope:{column_name}",
        }
        if unique:
            contract["unique"] = True
        lowered = column_name.lower()
        if lowered.endswith("_id") or lowered == "id":
            return {"name": field_name, "type": "long", "required": required, "inference_source": f"column-scope:{column_name}"}
        if lowered in {"sort", "sort_order"}:
            return {"name": field_name, "type": "integer", "required": required, "inference_source": f"column-scope:{column_name}"}
        if lowered.endswith("_status") or lowered == "status":
            contract["type"] = "enum"
            contract["enum_values"] = ["ENABLED", "DISABLED"]
            return contract
        if lowered.endswith("_time"):
            return {"name": field_name, "type": "datetime", "required": False, "inference_source": f"column-scope:{column_name}"}
        if lowered == "remark":
            contract["max_length"] = 255
            contract["required"] = False
            return contract
        contract["max_length"] = 128 if lowered.endswith(("value", "label", "name")) else 64
        return contract

    def _scope_table(self, scope: str) -> str:
        return scope.split(".", 1)[0]

    def _scope_columns(self, scope: str) -> list[str]:
        raw = scope.split(".", 1)[1]
        if raw.startswith("(") and raw.endswith(")"):
            return [item.strip() for item in raw[1:-1].split(",")]
        return [raw.strip()]

    def _translation_parent(self, entity_spec: dict[str, Any]) -> str:
        for relation in entity_spec.get("relations", []):
            if relation["relation"] == "many-to-one":
                return relation["target"]
        raise ValueError(f"Unable to infer translation parent for {entity_spec['entity_id']}")

    def _add_field(
        self,
        inferred_fields: OrderedDict[str, dict[str, Any]],
        key: str,
        field_contract: dict[str, Any],
    ) -> None:
        if key in inferred_fields:
            existing = inferred_fields[key]
            merged = dict(existing)
            merged.update({name: value for name, value in field_contract.items() if value is not None})
            if existing.get("unique") or field_contract.get("unique"):
                merged["unique"] = True
            if existing.get("required") or field_contract.get("required"):
                merged["required"] = True
            inferred_fields[key] = merged
            return
        inferred_fields[key] = field_contract
