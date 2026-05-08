from __future__ import annotations

import re
from typing import Iterable


class NamingResolution:
    GENERIC_COLUMN_PREFIXES = {"code", "name", "status", "label", "value"}

    def to_pascal_case(self, value: str) -> str:
        if "_" in value or "-" in value or " " in value:
            parts = re.split(r"[_\-\s]+", value)
            return "".join(part[:1].upper() + part[1:] for part in parts if part)
        if value[:1].islower():
            return value[:1].upper() + value[1:]
        return value

    def to_camel_case(self, value: str) -> str:
        pascal = self.to_pascal_case(value)
        return pascal[:1].lower() + pascal[1:] if pascal else pascal

    def to_snake_case(self, value: str) -> str:
        if "_" in value:
            return value.lower()
        words = re.findall(r"[A-Z][a-z0-9]*", self.to_pascal_case(value))
        return "_".join(word.lower() for word in words)

    def to_kebab_case(self, value: str) -> str:
        return self.to_snake_case(value).replace("_", "-")

    def common_route_base(self, routes: Iterable[str]) -> str:
        route_list = sorted({route.strip("/") for route in routes if route})
        if not route_list:
            return "/"
        segments = [route.split("/") for route in route_list]
        common: list[str] = []
        for group in zip(*segments):
            if len(set(group)) == 1:
                common.append(group[0])
            else:
                break
        return "/" + "/".join(common) if common else "/"

    def relative_route_segment(self, full_route: str, route_base: str) -> str:
        normalized_full = full_route.strip("/")
        normalized_base = route_base.strip("/")
        if normalized_base and normalized_full.startswith(normalized_base):
            suffix = normalized_full[len(normalized_base):].strip("/")
            return suffix or self.to_kebab_case(normalized_full.split("/")[-1])
        return normalized_full.split("/")[-1]

    def field_name_from_column(self, entity_name: str, column_name: str) -> str:
        normalized = column_name.lower()
        if normalized in {"id", "sort", "remark", "language_code", "created_time", "created_by", "last_modified_time", "last_modified_by", "deleted"}:
            return self.to_camel_case(normalized)
        if "_" in normalized:
            tokens = normalized.split("_")
            if len(tokens) > 1:
                return self.to_camel_case(normalized)
        base = self.to_camel_case(column_name)
        last_token = normalized.split("_")[-1]
        if last_token in self.GENERIC_COLUMN_PREFIXES:
            entity_base_name = entity_name[:-11] if entity_name.endswith("Translation") else entity_name
            entity_base = self.to_camel_case(entity_base_name)
            return entity_base[:1].lower() + entity_base[1:] + last_token[:1].upper() + last_token[1:]
        return base

    def entity_label(self, entity_name: str) -> str:
        tokens = re.findall(r"[A-Z][a-z0-9]*", self.to_pascal_case(entity_name))
        return " ".join(token.lower() for token in tokens)

    def permission_namespace(self, authorities: list[str]) -> str:
        normalized = sorted({authority for authority in authorities if authority})
        if not normalized:
            return ""
        parts = [authority.split(":")[:-1] for authority in normalized]
        common: list[str] = []
        for group in zip(*parts):
            if len(set(group)) == 1:
                common.append(group[0])
            else:
                break
        return ":".join(common)
