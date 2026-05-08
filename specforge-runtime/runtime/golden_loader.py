from __future__ import annotations

from pathlib import Path
from typing import Any

from .replay import load_yaml


class GoldenLoader:
    REQUIRED_ARTIFACTS = (
        "run-trace.yaml",
        "invalidation-report.yaml",
        "scheduler-trace.yaml",
        "verification-report.yaml",
        "logical-clock-summary.yaml",
        "lineage-report.yaml",
    )

    OPTIONAL_ARTIFACTS = (
        "replay-comparison.yaml",
        "replay-divergence-report.yaml",
        "benchmark-summary.yaml",
        "regression-summary.yaml",
    )

    def __init__(self, golden_root: Path) -> None:
        self.golden_root = golden_root

    def list_scenarios(self) -> list[dict[str, Any]]:
        scenarios: list[dict[str, Any]] = []
        if not self.golden_root.exists():
            return scenarios
        for scenario_dir in sorted(path for path in self.golden_root.iterdir() if path.is_dir()):
            manifest = load_yaml(scenario_dir / "scenario.yaml")
            if not manifest:
                continue
            scenarios.append(
                {
                    "name": scenario_dir.name,
                    "dir": scenario_dir,
                    "manifest": manifest,
                }
            )
        return scenarios

    def load_golden_bundle(self, scenario_dir: Path) -> dict[str, Any]:
        bundle: dict[str, Any] = {}
        for filename in self.REQUIRED_ARTIFACTS + self.OPTIONAL_ARTIFACTS:
            payload = load_yaml(scenario_dir / filename)
            if payload:
                bundle[filename] = payload
        return bundle
