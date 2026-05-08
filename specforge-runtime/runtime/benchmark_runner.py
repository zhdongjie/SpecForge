from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


class BenchmarkRunner:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.runs_dir = root / "runs"

    def run(self) -> dict[str, Any]:
        run_dirs = sorted(path for path in self.runs_dir.iterdir() if path.is_dir()) if self.runs_dir.exists() else []
        verification_reports = []
        for run_dir in run_dirs:
            report_path = run_dir / "logs" / "verification-report.yaml"
            if report_path.exists():
                verification_reports.append(yaml.safe_load(report_path.read_text(encoding="utf-8")) or {})
        total = len(verification_reports)
        passed = sum(1 for report in verification_reports if report.get("passed"))
        replay_scores = [report.get("replay_stability_score", 0.0) for report in verification_reports]
        determinism_scores = [report.get("scheduler_determinism_score", 0.0) for report in verification_reports]
        summary = {
            "recorded_at": self._now(),
            "sample_count": total,
            "replay_consistency_rate": (passed / total) if total else 1.0,
            "scheduler_stability": (sum(determinism_scores) / len(determinism_scores)) if determinism_scores else 1.0,
            "replay_equivalence_success_rate": (sum(replay_scores) / len(replay_scores)) if replay_scores else 1.0,
            "artifact_conflict_frequency": self._count_conflicts(run_dirs) / total if total else 0.0,
            "logical_clock_drift": self._count_clock_drift(verification_reports),
            "invalidation_propagation_depth": self._max_invalidation_depth(run_dirs),
        }
        output_path = self.root / "benchmark-summary.yaml"
        with output_path.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(summary, handle, sort_keys=False, allow_unicode=True)
        return summary

    def _count_conflicts(self, run_dirs: list[Path]) -> int:
        count = 0
        for run_dir in run_dirs:
            summary_path = run_dir / "logs" / "run-summary.yaml"
            if not summary_path.exists():
                continue
            payload = yaml.safe_load(summary_path.read_text(encoding="utf-8")) or {}
            count += len(payload.get("artifact_summary", {}).get("concurrency_conflicts", []))
        return count

    def _count_clock_drift(self, reports: list[dict[str, Any]]) -> int:
        return sum(1 for report in reports if not report.get("logical_clock_summary", {}).get("monotonic", True))

    def _max_invalidation_depth(self, run_dirs: list[Path]) -> int:
        max_depth = 0
        for run_dir in run_dirs:
            invalidation_path = run_dir / "logs" / "invalidation-report.yaml"
            if not invalidation_path.exists():
                continue
            payload = yaml.safe_load(invalidation_path.read_text(encoding="utf-8")) or {}
            max_depth = max(max_depth, len(payload.get("events", [])))
        return max_depth

    def _now(self) -> str:
        return datetime.now().astimezone().isoformat(timespec="seconds")
