from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any


def split_camel_case(value: str) -> list[str]:
    return re.findall(r"[A-Z]+(?=[A-Z][a-z]|$)|[A-Z]?[a-z]+|\d+", value)


def upper_camel(tokens: list[str]) -> str:
    return "".join(token[:1].upper() + token[1:] for token in tokens if token)


def lower_camel(tokens: list[str]) -> str:
    if not tokens:
        return ""
    head = tokens[0][:1].lower() + tokens[0][1:]
    tail = [token[:1].upper() + token[1:] for token in tokens[1:]]
    return "".join([head] + tail)


def snake_case(tokens: list[str]) -> str:
    return "_".join(token.lower() for token in tokens if token)


def kebab_case(tokens: list[str]) -> str:
    return "-".join(token.lower() for token in tokens if token)


def dot_case(tokens: list[str]) -> str:
    return ".".join(token[:1].lower() + token[1:] for token in tokens if token)


@dataclass(frozen=True)
class ReplacementRule:
    source: str
    target: str
    category: str


class NamingTransformer:
    def __init__(self, module_spec: dict[str, Any], resolved_schema: dict[str, Any], mutation_spec: dict[str, Any]) -> None:
        self.module_spec = module_spec
        self.resolved_schema = resolved_schema
        self.mutation_spec = mutation_spec
        self.source_package_root = resolved_schema["module_identity"]["package_root"]
        self.target_module_name = mutation_spec["target_module"]["name"]
        self.entity_mapping = dict(mutation_spec.get("semantic_mutations", {}).get("entities", {}))
        self.table_mapping = dict(mutation_spec.get("semantic_mutations", {}).get("tables", {}))
        self.route_mapping = dict(mutation_spec.get("semantic_mutations", {}).get("routes", {}))
        self.permission_mapping = dict(mutation_spec.get("semantic_mutations", {}).get("permissions", {}))
        self.target_package_root = mutation_spec["target_module"].get(
            "package_root",
            self._derive_target_package_root(),
        )
        self.package_mapping = self._derive_package_mapping()
        self.localization_mapping = self._derive_localization_mapping()
        self.replacement_rules = self._build_replacement_rules()

    def _derive_target_package_root(self) -> str:
        target_head = self.target_module_name.split("-", 1)[0]
        return self.source_package_root.rsplit(".", 1)[0] + f".{target_head}"

    def _derive_package_mapping(self) -> dict[str, str]:
        mapping = {self.source_package_root: self.target_package_root}
        for source_entity, target_entity in sorted(self.entity_mapping.items()):
            source_last = split_camel_case(source_entity)[-1].lower()
            target_last = split_camel_case(target_entity)[-1].lower()
            mapping[f"{self.source_package_root}.{source_last}"] = f"{self.target_package_root}.{target_last}"
        return mapping

    def _derive_localization_mapping(self) -> dict[str, str]:
        mapping: dict[str, str] = {}
        for source_entity, target_entity in sorted(self.entity_mapping.items()):
            mapping[f"form.{lower_camel(split_camel_case(source_entity))}"] = f"form.{lower_camel(split_camel_case(target_entity))}"
        return mapping

    def _build_replacement_rules(self) -> list[ReplacementRule]:
        rules: dict[tuple[str, str], ReplacementRule] = {}

        def add(source: str, target: str, category: str) -> None:
            if source and source != target:
                rules[(source, category)] = ReplacementRule(source=source, target=target, category=category)

        add(self.source_package_root, self.target_package_root, "package-root")
        for source, target in sorted(self.package_mapping.items()):
            add(source, target, "package")
            add(source.replace(".", "/"), target.replace(".", "/"), "path")
            add(source.replace(".", "\\"), target.replace(".", "\\"), "path")

        for source_entity, target_entity in sorted(self.entity_mapping.items()):
            source_tokens = split_camel_case(source_entity)
            target_tokens = split_camel_case(target_entity)

            add(source_entity, target_entity, "entity")
            add(lower_camel(source_tokens), lower_camel(target_tokens), "field")
            add(snake_case(source_tokens), snake_case(target_tokens), "table-token")
            add(kebab_case(source_tokens), kebab_case(target_tokens), "route-token")
            add(dot_case(source_tokens), dot_case(target_tokens), "localization-token")

        for source, target in sorted(self.table_mapping.items()):
            add(source, target, "table")

        for source, target in sorted(self.route_mapping.items()):
            add(source, target, "route")

        for source, target in sorted(self.permission_mapping.items()):
            add(source, target, "permission")

        for source, target in sorted(self.localization_mapping.items()):
            add(source, target, "localization")

        return sorted(rules.values(), key=lambda item: (-len(item.source), item.source, item.category))

    def rename_relative_path(self, relative_path: Path) -> Path:
        value = relative_path.as_posix()
        for rule in self.replacement_rules:
            value = value.replace(rule.source.replace("\\", "/"), rule.target.replace("\\", "/"))
        return Path(*value.split("/"))

    def rename_text(self, content: str) -> str:
        rewritten = content
        for rule in self.replacement_rules:
            rewritten = rewritten.replace(rule.source, rule.target)
        return rewritten

    def mapping_report(self) -> dict[str, Any]:
        return {
            "source_package_root": self.source_package_root,
            "target_package_root": self.target_package_root,
            "entity_mapping": self.entity_mapping,
            "table_mapping": self.table_mapping,
            "route_mapping": self.route_mapping,
            "permission_mapping": self.permission_mapping,
            "localization_mapping": self.localization_mapping,
            "package_mapping": self.package_mapping,
            "replacement_rules": [
                {"source": rule.source, "target": rule.target, "category": rule.category}
                for rule in self.replacement_rules
            ],
        }
