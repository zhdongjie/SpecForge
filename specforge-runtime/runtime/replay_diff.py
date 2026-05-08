from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .semantic_equivalence import SemanticEquivalenceValidator


class ReplayDiffEngine:
    def generate_report(self, baseline_source: Path | dict[str, Any], current_run_dir: Path) -> dict[str, Any]:
        equivalence = SemanticEquivalenceValidator().compare(baseline_source, current_run_dir)
        first_divergence = equivalence["differences"][0] if equivalence["differences"] else {}
        report = {
            "baseline_reference": str(baseline_source) if isinstance(baseline_source, Path) else "in-memory-bundle",
            "current_run_dir": str(current_run_dir),
            "match": equivalence["passed"],
            "divergence_count": equivalence["difference_count"],
            "divergence_root_cause": first_divergence.get("field"),
            "first_divergent_scheduler_event": self._extract_scheduler_divergence(first_divergence),
            "logical_clock_mismatch": self._extract_mismatch("logical_clock", equivalence),
            "lineage_inconsistency": self._extract_mismatch("artifact_lineage", equivalence),
            "invalidation_mismatch": self._extract_mismatch("invalidation_map", equivalence),
        }
        output_path = current_run_dir / "logs" / "replay-divergence-report.yaml"
        with output_path.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(report, handle, sort_keys=False, allow_unicode=True)
        return report

    def _extract_scheduler_divergence(self, difference: dict[str, Any]) -> dict[str, Any] | None:
        if difference.get("field") != "scheduler_consistency":
            return None
        baseline = difference.get("baseline", [])
        current = difference.get("current", [])
        for index, (left, right) in enumerate(zip(baseline, current)):
            if left != right:
                return {"index": index, "baseline": left, "current": right}
        if len(baseline) != len(current):
            return {"index": min(len(baseline), len(current)), "baseline": baseline, "current": current}
        return None

    def _extract_mismatch(self, field: str, equivalence: dict[str, Any]) -> dict[str, Any] | None:
        for difference in equivalence.get("differences", []):
            if difference.get("field") == field:
                return difference
        return None
