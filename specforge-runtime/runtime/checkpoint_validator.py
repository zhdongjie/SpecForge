from __future__ import annotations

from pathlib import Path
from typing import Any

from .replay import load_run_trace, load_task_records, load_yaml


class CheckpointValidator:
    def validate(
        self,
        task_graph: dict[str, Any],
        run_dir: Path,
        replay_source_run_id: str | None = None,
        affected_tasks: set[str] | None = None,
    ) -> dict[str, Any]:
        findings: list[dict[str, str]] = []
        task_records = load_task_records(run_dir)
        run_trace = load_run_trace(run_dir)
        invalidation_report = load_yaml(run_dir / "logs" / "invalidation-report.yaml")
        seeded_tasks = set(run_trace.get("seeded_tasks", []))

        for checkpoint in task_graph.get("integration_checkpoints", []):
            checkpoint_id = checkpoint.get("checkpoint_id", "<unknown>")
            producer = checkpoint.get("produced_by", "")
            producer_state = task_records.get(producer, {}).get("lifecycle_state", {}).get("current_state")
            if producer and producer_state == "SUCCESS":
                for consumer in checkpoint.get("required_for", []):
                    consumer_state = task_records.get(consumer, {}).get("lifecycle_state", {}).get("current_state")
                    if consumer_state not in {"SUCCESS", "INVALIDATED"}:
                        findings.append(
                            self._finding(
                                "ERROR",
                                "checkpoint-contract-violation",
                                f"Checkpoint {checkpoint_id} has consumer {consumer} in unexpected state {consumer_state}",
                            )
                        )

        if replay_source_run_id and affected_tasks:
            leaked = [
                event.get("task_id", "")
                for event in invalidation_report.get("events", [])
                if event.get("task_id") in seeded_tasks
            ]
            if leaked:
                findings.append(
                    self._finding(
                        "ERROR",
                        "partial-replay-invalidation-leak",
                        f"Seeded tasks were invalidated during partial replay: {', '.join(sorted(leaked))}",
                    )
                )

        return {
            "validator": "checkpoint-validator",
            "passed": not any(finding["severity"] == "ERROR" for finding in findings),
            "finding_count": len(findings),
            "findings": findings,
        }

    def _finding(self, severity: str, code: str, message: str) -> dict[str, str]:
        return {"severity": severity, "code": code, "message": message}
