from __future__ import annotations

from pathlib import Path
from typing import Any

from .replay import load_run_trace, load_task_records, load_yaml


class SemanticEquivalenceValidator:
    def compare(self, baseline_source: Path | dict[str, Any], current_source: Path | dict[str, Any]) -> dict[str, Any]:
        baseline = self._build_semantic_snapshot(baseline_source)
        current = self._build_semantic_snapshot(current_source)
        differences: list[dict[str, Any]] = []

        self._compare_field("dependency_ordering", baseline, current, differences)
        self._compare_field("artifact_lineage", baseline, current, differences)
        self._compare_field("rollback_propagation", baseline, current, differences)
        self._compare_field("invalidation_map", baseline, current, differences)
        self._compare_field("scheduler_consistency", baseline, current, differences)
        self._compare_field("logical_clock", baseline, current, differences)
        self._compare_field("replay_determinism", baseline, current, differences)
        self._compare_field("checkpoint_consistency", baseline, current, differences)

        return {
            "validator": "semantic-equivalence",
            "passed": not differences,
            "difference_count": len(differences),
            "differences": differences,
            "baseline_snapshot": baseline,
            "current_snapshot": current,
        }

    def _build_semantic_snapshot(self, source: Path | dict[str, Any]) -> dict[str, Any]:
        bundle = self._load_bundle(source)
        run_trace = bundle.get("run-trace.yaml", {})
        invalidation_report = bundle.get("invalidation-report.yaml", {})
        verification_report = bundle.get("verification-report.yaml", {})
        lineage_report = bundle.get("lineage-report.yaml", {})
        scheduler_trace = bundle.get("scheduler-trace.yaml", {})
        task_records = bundle.get("task-records", {})

        scheduler_events = self._normalize_scheduler_events(
            run_trace.get("scheduler_events") or scheduler_trace.get("events", [])
        )
        lineage_snapshot = verification_report.get("lineage_snapshot") or lineage_report.get("artifact_lineage", {})
        logical_summary = verification_report.get("logical_clock_summary", {})
        checkpoint_summary = verification_report.get("checkpoint_validation", {})

        return {
            "dependency_ordering": [
                event["task_id"]
                for event in scheduler_events
                if event.get("event") == "task-transition" and event.get("state") == "SUCCESS"
            ],
            "artifact_lineage": lineage_snapshot or {
                task_id: sorted(
                    (
                        artifact.get("artifact_file_name", ""),
                        artifact.get("artifact_digest", ""),
                    )
                    for artifact in record.get("generated_artifact_lineage", {}).get("produced_artifacts", [])
                )
                for task_id, record in sorted(task_records.items())
            },
            "rollback_propagation": sorted(
                (
                    event.get("task_id", ""),
                    event.get("reason", ""),
                    event.get("triggered_by", ""),
                )
                for event in invalidation_report.get("events", [])
            ),
            "invalidation_map": self._build_invalidation_map(task_records, invalidation_report),
            "scheduler_consistency": scheduler_events,
            "logical_clock": {
                "monotonic": logical_summary.get("monotonic"),
                "transition_count": logical_summary.get("transition_count"),
                "scheduler_event_count": logical_summary.get("scheduler_event_count"),
                "final_tick": logical_summary.get("final_tick"),
            },
            "replay_determinism": {
                "replay_trace_consistency": verification_report.get("runtime_validations", {}).get(
                    "replay_trace_consistency"
                ),
                "scheduler_determinism_score": verification_report.get("scheduler_determinism_score"),
                "replay_stability_score": verification_report.get("replay_stability_score"),
            },
            "checkpoint_consistency": {
                "passed": checkpoint_summary.get("passed"),
                "finding_count": checkpoint_summary.get("finding_count"),
            },
        }

    def _load_bundle(self, source: Path | dict[str, Any]) -> dict[str, Any]:
        if isinstance(source, dict):
            return source
        if (source / "logs").exists():
            return self._load_run_bundle(source)
        return self._load_flat_bundle(source)

    def _load_run_bundle(self, run_dir: Path) -> dict[str, Any]:
        logs_dir = run_dir / "logs"
        bundle = {
            "run-trace.yaml": load_yaml(logs_dir / "run-trace.yaml"),
            "scheduler-trace.yaml": load_yaml(logs_dir / "scheduler-trace.yaml"),
            "verification-report.yaml": load_yaml(logs_dir / "verification-report.yaml"),
            "logical-clock-summary.yaml": load_yaml(logs_dir / "logical-clock-summary.yaml"),
            "lineage-report.yaml": load_yaml(logs_dir / "lineage-report.yaml"),
            "invalidation-report.yaml": load_yaml(logs_dir / "invalidation-report.yaml"),
            "replay-comparison.yaml": load_yaml(logs_dir / "replay-comparison.yaml"),
            "replay-divergence-report.yaml": load_yaml(logs_dir / "replay-divergence-report.yaml"),
            "task-records": load_task_records(run_dir),
        }
        return bundle

    def _build_invalidation_map(
        self,
        task_records: dict[str, dict[str, Any]],
        invalidation_report: dict[str, Any],
    ) -> dict[str, str]:
        from_records = {
            task_id: record.get("invalidation", {}).get("reason", "")
            for task_id, record in sorted(task_records.items())
            if record.get("invalidation")
        }
        if from_records:
            return from_records
        return {
            event.get("task_id", ""): event.get("reason", "")
            for event in invalidation_report.get("events", [])
            if event.get("task_id") and event.get("reason")
        }

    def _load_flat_bundle(self, bundle_dir: Path) -> dict[str, Any]:
        bundle: dict[str, Any] = {}
        for filename in (
            "run-trace.yaml",
            "scheduler-trace.yaml",
            "verification-report.yaml",
            "logical-clock-summary.yaml",
            "lineage-report.yaml",
            "invalidation-report.yaml",
            "replay-comparison.yaml",
            "replay-divergence-report.yaml",
        ):
            bundle[filename] = load_yaml(bundle_dir / filename)
        return bundle

    def _normalize_scheduler_events(self, events: list[dict[str, Any]]) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        for event in events:
            normalized_event = {
                "event": event.get("event"),
                "batch_id": event.get("batch_id"),
                "wave_index": event.get("wave_index"),
                "task_id": event.get("task_id"),
                "task_ids": list(event.get("task_ids", [])),
                "state": event.get("state"),
                "completed_states": dict(event.get("completed_states", {})),
                "mode": event.get("mode"),
                "halted": event.get("halted"),
            }
            normalized.append(normalized_event)
        return normalized

    def _compare_field(
        self,
        field: str,
        baseline: dict[str, Any],
        current: dict[str, Any],
        differences: list[dict[str, Any]],
    ) -> None:
        if baseline.get(field) == current.get(field):
            return
        differences.append(
            {
                "field": field,
                "baseline": baseline.get(field),
                "current": current.get(field),
            }
        )
