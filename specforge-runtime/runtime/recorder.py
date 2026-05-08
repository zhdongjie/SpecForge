from __future__ import annotations

from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any

import yaml

from .task_state import TaskState


class Recorder:
    def __init__(self, run_dir: Path, specs_dir: Path) -> None:
        self.run_dir = run_dir
        self.logs_dir = run_dir / "logs"
        self.task_records_dir = run_dir / "task-records"
        self.specs_dir = specs_dir
        self.log_path = self.logs_dir / "runtime.log"
        self.summary_path = self.logs_dir / "run-summary.yaml"
        self.trace_path = self.logs_dir / "run-trace.yaml"
        self.comparison_path = self.logs_dir / "replay-comparison.yaml"
        self.invalidation_path = self.logs_dir / "invalidation-report.yaml"
        self.scheduler_trace_path = self.logs_dir / "scheduler-trace.yaml"
        self.verification_path = self.logs_dir / "verification-report.yaml"
        self._lock = Lock()
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.task_records_dir.mkdir(parents=True, exist_ok=True)
        self.log_path.write_text("", encoding="utf-8")

    def log_transition(self, state: TaskState, task: dict[str, Any], stamp: dict[str, Any]) -> None:
        label = f"{task['task_id']} ({task['semantic_operation']})"
        line = f"[{state.value}] {label} [tick={stamp['execution_tick']}]"
        with self._lock:
            print(line)
            with self.log_path.open("a", encoding="utf-8") as handle:
                handle.write(line + "\n")

    def write_task_record(
        self,
        task: dict[str, Any],
        task_id: str,
        state_history: list[dict[str, Any]],
        final_state: TaskState,
        planned_artifacts: list[dict[str, Any]],
        validation_results: dict[str, Any],
        downstream_ready: list[str],
        dependencies: list[str],
        retry_attempt: int,
        retry_max_attempts: int,
        invalidation: dict[str, Any] | None = None,
        seeded_from_run: str | None = None,
        logical_clock_summary: dict[str, Any] | None = None,
    ) -> Path:
        now = self._now()
        record = {
            "execution_identity": {
                "run_record_id": f"trr-{self.run_dir.name}-{task_id.lower()}",
                "pipeline_run_id": self.run_dir.name,
                "task_graph_id": "dictionary-management-generation-dag-v1",
                "task_id": task_id,
                "semantic_operation": task["semantic_operation"],
                "compiler_stage": task.get("stage"),
            },
            "lifecycle_state": {
                "current_state": final_state.value,
                "terminal": final_state in {TaskState.SUCCESS, TaskState.FAILED, TaskState.SKIPPED, TaskState.INVALIDATED},
                "state_history": state_history,
                "success": final_state == TaskState.SUCCESS,
            },
            "timestamps": {
                "recorded_at": now,
                "started_at": state_history[0]["entered_at"] if state_history else now,
                "finished_at": state_history[-1]["entered_at"] if state_history else now,
            },
            "logical_clock": logical_clock_summary or {},
            "semantic_provenance": {
                "source_module_spec": str(self.specs_dir / "module-spec.yaml"),
                "source_resolved_schema": str(self.specs_dir / "module-schema.resolved.yaml"),
                "source_task_graph": str(self.specs_dir / "generation-task-graph.yaml"),
            },
            "generated_artifact_lineage": {
                "produced_artifacts": planned_artifacts,
                "dependency_inputs": list(dependencies),
            },
            "validation_results": validation_results,
            "retry_metadata": {
                "attempt": retry_attempt,
                "max_attempts": retry_max_attempts,
                "retry_safe": True,
            },
            "integration_status": {
                "upstream_dependencies": list(dependencies),
                "downstream_ready": list(downstream_ready),
            },
        }
        if invalidation is not None:
            record["invalidation"] = invalidation
        if seeded_from_run is not None:
            record["seeded_from_run"] = seeded_from_run
        output_path = self.task_records_dir / f"{task_id}.task-run-record.yaml"
        self._write_yaml(output_path, record)
        return output_path

    def write_run_summary(self, summary: dict[str, Any]) -> Path:
        self._write_yaml(self.summary_path, summary)
        return self.summary_path

    def write_run_trace(self, trace: dict[str, Any]) -> Path:
        self._write_yaml(self.trace_path, trace)
        return self.trace_path

    def write_replay_comparison(self, comparison: dict[str, Any]) -> Path:
        self._write_yaml(self.comparison_path, comparison)
        return self.comparison_path

    def write_invalidation_report(self, payload: dict[str, Any]) -> Path:
        self._write_yaml(self.invalidation_path, payload)
        return self.invalidation_path

    def write_scheduler_trace(self, payload: dict[str, Any]) -> Path:
        self._write_yaml(self.scheduler_trace_path, payload)
        return self.scheduler_trace_path

    def write_verification_report(self, payload: dict[str, Any]) -> Path:
        self._write_yaml(self.verification_path, payload)
        return self.verification_path

    def _write_yaml(self, path: Path, payload: dict[str, Any]) -> None:
        with self._lock:
            with path.open("w", encoding="utf-8") as handle:
                yaml.safe_dump(payload, handle, sort_keys=False, allow_unicode=True)

    def _now(self) -> str:
        return datetime.now().astimezone().isoformat(timespec="seconds")
