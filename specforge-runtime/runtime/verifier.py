from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from .checkpoint_validator import CheckpointValidator
from .graph_validator import GraphValidator
from .lineage_validator import LineageValidator
from .replay import load_run_trace, load_task_records
from .replay_diff import ReplayDiffEngine
from .replay_validator import ReplayValidator
from .semantic_equivalence import SemanticEquivalenceValidator
from .semantic_validator import SemanticValidator


class RuntimeVerifier:
    def __init__(self, specs_dir: Path, run_dir: Path) -> None:
        self.specs_dir = specs_dir
        self.run_dir = run_dir
        self.logs_dir = run_dir / "logs"
        self.graph_validator = GraphValidator()
        self.semantic_validator = SemanticValidator()
        self.replay_validator = ReplayValidator()
        self.lineage_validator = LineageValidator()
        self.checkpoint_validator = CheckpointValidator()
        self.semantic_equivalence = SemanticEquivalenceValidator()
        self.replay_diff = ReplayDiffEngine()

    def verify_static(self, loaded: dict[str, dict[str, Any]]) -> dict[str, Any]:
        graph_report = self.graph_validator.validate(loaded["task_graph"])
        report = {
            "phase": "static",
            "recorded_at": self._now(),
            "specs_dir": str(self.specs_dir),
            "graph_validation": graph_report,
        }
        report["passed"] = graph_report["passed"]
        self._write_yaml(self.logs_dir / "static-verification.yaml", report)
        return report

    def verify_runtime(
        self,
        loaded: dict[str, dict[str, Any]],
        replay_source_run_id: str | None = None,
        affected_tasks: set[str] | None = None,
    ) -> dict[str, Any]:
        semantic_report = self.semantic_validator.validate(loaded["task_graph"], self.run_dir)
        lineage_report = self.lineage_validator.validate(self.run_dir)
        checkpoint_report = self.checkpoint_validator.validate(
            loaded["task_graph"],
            self.run_dir,
            replay_source_run_id=replay_source_run_id,
            affected_tasks=affected_tasks,
        )
        replay_report = self.replay_validator.validate(
            self.run_dir,
            replay_source_run_id=replay_source_run_id,
            affected_tasks=affected_tasks,
        )

        run_trace = load_run_trace(self.run_dir)
        task_records = load_task_records(self.run_dir)
        logical_clock_summary = self._build_logical_clock_summary(run_trace)
        lineage_snapshot = self._build_lineage_snapshot(task_records)
        lineage_summary = {
            **lineage_report,
            "artifact_lineage": lineage_snapshot,
        }

        semantic_equivalence_report: dict[str, Any] | None = None
        replay_divergence_report: dict[str, Any] | None = None
        if replay_source_run_id:
            baseline_run_dir = self.run_dir.parent / replay_source_run_id
            semantic_equivalence_report = self.semantic_equivalence.compare(baseline_run_dir, self.run_dir)
            if not semantic_equivalence_report["passed"]:
                replay_divergence_report = self.replay_diff.generate_report(baseline_run_dir, self.run_dir)

        replay_stability_score = self._score_bool(
            replay_report.get("passed", True)
            and (semantic_equivalence_report["passed"] if semantic_equivalence_report else True)
        )
        scheduler_determinism_score = self._score_bool(
            semantic_report.get("passed", True) and logical_clock_summary.get("monotonic", True)
        )

        report = {
            "phase": "runtime",
            "recorded_at": self._now(),
            "run_dir": str(self.run_dir),
            "semantic_validation": semantic_report,
            "lineage_validation": lineage_report,
            "checkpoint_validation": checkpoint_report,
            "replay_validation": replay_report,
            "semantic_equivalence_status": (
                semantic_equivalence_report["passed"] if semantic_equivalence_report else True
            ),
            "semantic_equivalence": semantic_equivalence_report,
            "replay_stability_score": replay_stability_score,
            "scheduler_determinism_score": scheduler_determinism_score,
            "invalidation_integrity": semantic_report["passed"],
            "lineage_integrity": lineage_report["passed"],
            "checkpoint_consistency": checkpoint_report["passed"],
            "replay_divergence_count": (
                semantic_equivalence_report["difference_count"] if semantic_equivalence_report else 0
            ),
            "logical_clock_summary": logical_clock_summary,
            "lineage_snapshot": lineage_snapshot,
            "runtime_validations": {
                "replay_trace_consistency": replay_report.get("passed", True),
                "semantic_equivalence": semantic_equivalence_report["passed"] if semantic_equivalence_report else True,
                "logical_clock_monotonicity": logical_clock_summary.get("monotonic", True),
                "checkpoint_contracts": checkpoint_report.get("passed", True),
            },
        }
        report["passed"] = all(
            item["passed"] for item in (semantic_report, lineage_report, checkpoint_report, replay_report)
        ) and (semantic_equivalence_report["passed"] if semantic_equivalence_report else True)

        self._write_yaml(self.logs_dir / "logical-clock-summary.yaml", logical_clock_summary)
        self._write_yaml(self.logs_dir / "lineage-report.yaml", lineage_summary)
        if replay_divergence_report is not None:
            self._write_yaml(self.logs_dir / "replay-divergence-report.yaml", replay_divergence_report)
        self._write_yaml(self.logs_dir / "verification-report.yaml", report)
        return report

    def _build_logical_clock_summary(self, run_trace: dict[str, Any]) -> dict[str, Any]:
        scheduler_events = run_trace.get("scheduler_events", [])
        ticks = [
            event.get("execution_tick")
            for event in scheduler_events
            if event.get("execution_tick") is not None
        ]
        return {
            "validator": "logical-clock-summary",
            "monotonic": ticks == sorted(ticks),
            "final_tick": ticks[-1] if ticks else 0,
            "transition_count": sum(1 for event in scheduler_events if event.get("event") == "task-transition"),
            "scheduler_event_count": len(ticks),
            "unique_tick_count": len(set(ticks)),
        }

    def _build_lineage_snapshot(self, task_records: dict[str, dict[str, Any]]) -> dict[str, Any]:
        return {
            task_id: sorted(
                (
                    artifact.get("artifact_file_name", ""),
                    artifact.get("artifact_digest", ""),
                )
                for artifact in record.get("generated_artifact_lineage", {}).get("produced_artifacts", [])
            )
            for task_id, record in sorted(task_records.items())
        }

    def _score_bool(self, passed: bool) -> float:
        return 1.0 if passed else 0.0

    def _write_yaml(self, path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(payload, handle, sort_keys=False, allow_unicode=True)

    def _now(self) -> str:
        return datetime.now().astimezone().isoformat(timespec="seconds")
