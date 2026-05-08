from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class FieldTypeDefinition:
    logical_type: str
    java_type: str
    sql_type: str
    imports: tuple[str, ...]
    validation_imports: tuple[str, ...]
    annotation_builder: str | None = None


class FieldTypeSystem:
    DEFINITIONS = {
        "long": FieldTypeDefinition("long", "Long", "BIGINT", tuple(), tuple()),
        "integer": FieldTypeDefinition("integer", "Integer", "INT", tuple(), tuple()),
        "string": FieldTypeDefinition("string", "String", "VARCHAR", tuple(), tuple()),
        "decimal": FieldTypeDefinition("decimal", "BigDecimal", "DECIMAL", ("java.math.BigDecimal",), tuple()),
        "boolean": FieldTypeDefinition("boolean", "Boolean", "TINYINT(1)", tuple(), tuple()),
        "datetime": FieldTypeDefinition("datetime", "Date", "DATETIME", ("java.util.Date",), tuple()),
        "enum": FieldTypeDefinition("enum", "String", "VARCHAR", tuple(), tuple()),
    }

    def resolve(self, field: dict[str, Any]) -> FieldTypeDefinition:
        logical_type = str(field.get("type", "string")).lower()
        if logical_type not in self.DEFINITIONS:
            raise ValueError(f"Unsupported field type: {logical_type}")
        return self.DEFINITIONS[logical_type]

    def sql_column_type(self, field: dict[str, Any]) -> str:
        definition = self.resolve(field)
        if definition.logical_type == "string":
            length = int(field.get("max_length", 255))
            return f"VARCHAR({length})"
        if definition.logical_type == "decimal":
            precision = int(field.get("precision", 18))
            scale = int(field.get("scale", 2))
            return f"DECIMAL({precision},{scale})"
        if definition.logical_type == "enum":
            values = [str(value) for value in field.get("enum_values", [])]
            max_length = max((len(value) for value in values), default=32)
            return f"VARCHAR({max_length})"
        return definition.sql_type

    def default_java_literal(self, field: dict[str, Any]) -> str:
        logical_type = str(field.get("type", "string")).lower()
        if logical_type == "string":
            return '""'
        if logical_type == "integer":
            return "0"
        if logical_type == "long":
            return "0L"
        if logical_type == "decimal":
            return "BigDecimal.ZERO"
        if logical_type == "boolean":
            return "Boolean.FALSE"
        return "null"
