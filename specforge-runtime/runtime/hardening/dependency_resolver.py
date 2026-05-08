from __future__ import annotations

from pathlib import Path
from typing import Any

from runtime.codegen.common import dump_yaml


class DependencyResolver:
    def __init__(self, project_root: Path, logs_root: Path) -> None:
        self.project_root = project_root
        self.logs_root = logs_root

    def resolve(self, diagnostics: list[dict[str, Any]]) -> dict[str, Any]:
        report = {
            "status": "PASS",
            "actions": [],
            "project_file": str(self.project_root / "pom.xml"),
        }
        for finding in diagnostics:
            if finding.get("category") == "missing_dependency":
                report["status"] = "NO_ACTION"
                report["actions"].append(
                    {
                        "action": "dependency_insertion_deferred",
                        "reason": "No deterministic dependency catalog is available yet",
                    }
                )
        dump_yaml(self.logs_root / "dependency-resolution-report.yaml", report)
        return report
