from __future__ import annotations

import re


class NamingCanonicalizer:
    def pascal_to_words(self, value: str) -> list[str]:
        return [part for part in re.findall(r"[A-Z][a-z0-9]*", value) if part]

    def to_pascal_case(self, value: str) -> str:
        if "_" in value or "-" in value:
            parts = re.split(r"[_-]+", value)
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
        words = self.pascal_to_words(self.to_pascal_case(value))
        return "_".join(word.lower() for word in words)

    def pluralize(self, value: str) -> str:
        if value.endswith("y") and not value.endswith(("ay", "ey", "iy", "oy", "uy")):
            return value[:-1] + "ies"
        if value.endswith("s"):
            return value + "es"
        return value + "s"

    def entity_label(self, entity_name: str) -> str:
        return " ".join(self.pascal_to_words(entity_name))

    def dto_name(self, entity_name: str, suffix: str) -> str:
        return f"{entity_name}{suffix}"

    def lower_hyphen(self, value: str) -> str:
        words = self.pascal_to_words(self.to_pascal_case(value))
        return "-".join(word.lower() for word in words)
