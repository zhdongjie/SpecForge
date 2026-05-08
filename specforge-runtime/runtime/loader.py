from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class SpecLoader:
    def __init__(self, specs_dir: Path) -> None:
        self.specs_dir = specs_dir

    def load_yaml(self, filename: str) -> dict[str, Any]:
        path = self.specs_dir / filename
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        if not isinstance(data, dict):
            raise ValueError(f"{filename} must contain a top-level mapping")
        return data

    def load_all(self) -> dict[str, dict[str, Any]]:
        return {
            "module_spec": self.load_yaml("module-spec.yaml"),
            "resolved_schema": self.load_yaml("module-schema.resolved.yaml"),
            "task_graph": self.load_yaml("generation-task-graph.yaml"),
        }
