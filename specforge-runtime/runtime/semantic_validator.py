from __future__ import annotations

from pathlib import Path
from typing import Any

from .dag_engine import DagEngine
from .replay import load_run_trace, load_task_records, load_yaml
from .task_state import TERMINAL_STATES, TaskState


class SemanticValidator:
    ALLOWED_TRANSITIONS = {
        "READY": {"RUNNING"},
        "RUNNING": {"SUCCESS", "FAILED"},
        "FAILED": {"READY"},
        "SUCCESS": set(),
        "SKIPPED": set(),
        "INVALIDATED": set(),
    }

    def validate(self, task_graph: dict[str, Any], run_dir: Path) -> dict[str, Any]:
        findings: list[dict[str, str]] = []
        dag = DagEngine(task_graph)
        run_trace = load_run_trace(run_dir)
        scheduler_trace = load_yaml(run_dir / "logs" / "scheduler-trace.yaml")
        run_summary = load_yaml(run_dir / "logs" / "run-summary.yaml")
        invalidation_report = load_yaml(run_dir / "logs" / "invalidation-report.yaml")
        task_records = load_task_records(run_dir)

        self._check_scheduler_trace_alignment(run_trace, scheduler_trace, findings)
        self._check_logical_clock(run_trace, findings)
        self._check_task_histories(task_records, findings)
        self._check_dependency_readiness(dag, run_trace, task_records, findings)
        self._check_parallel_failure_propagation(run_trace, task_records, findings)
        self._check_downstream_invalidation(dag, task_records, invalidation_report, findings)
        self._check_run_summary(run_trace, run_summary, findings)

        return {
            "validator": "semantic-validator",
            "passed": not any(finding["severity"] == "ERROR" for finding in findings),
            "finding_count": len(findings),
            "findings": findings,
        }

    def _check_scheduler_trace_alignment(
        self,
        run_trace: dict[str, Any],
        scheduler_trace: dict[str, Any],
        findings: list[dict[str, str]],
    ) -> None:
        if run_trace.get("scheduler_events", []) != scheduler_trace.get("events", []):
            findings.append(
                self._finding(
                    "ERROR",
                    "scheduler-trace-mismatch",
                    "run-trace scheduler_events do not match scheduler-trace events",
                )
            )

    def _check_logical_clock(self, run_trace: dict[str, Any], findings: list[dict[str, str]]) -> None:
        ticks = [
            event.get("execution_tick")
            for event in run_trace.get("scheduler_events", [])
            if event.get("execution_tick") is not None
        ]
        if ticks != sorted(ticks):
            findings.append(
                self._finding(
                    "ERROR",
                    "logical-clock-non-monotonic",
                    "Scheduler event execution ticks are not monotonic",
                )
            )
        if len(set(ticks)) != len(ticks):
            findings.append(
                self._finding(
                    "ERROR",
                    "logical-clock-duplicate-tick",
                    "Scheduler event execution ticks must be unique",
                )
            )

    def _check_task_histories(
        self,
        task_records: dict[str, dict[str, Any]],
        findings: list[dict[str, str]],
    ) -> None:
        for task_id, record in sorted(task_records.items()):
            history = record.get("lifecycle_state", {}).get("state_history", [])
            if not history:
                findings.append(
                    self._finding(
                        "ERROR",
                        "missing-state-history",
                        f"Task record {task_id} has no state history",
                    )
                )
                continue
            previous_state: str | None = None
            for entry in history:
                state = entry.get("state")
                if state not in TaskState.__members__ and state not in {member.value for member in TaskState}:
                    findings.append(
                        self._finding(
                            "ERROR",
                            "unknown-task-state",
                            f"Task {task_id} contains unknown state {state}",
                        )
                    )
                if previous_state is not None and state not in self.ALLOWED_TRANSITIONS.get(previous_state, set()):
                    findings.append(
                        self._finding(
                            "ERROR",
                            "invalid-state-transition",
                            f"Task {task_id} has invalid transition {previous_state} -> {state}",
                        )
                    )
                previous_state = state

            final_state = record.get("lifecycle_state", {}).get("current_state")
            if previous_state != final_state:
                findings.append(
                    self._finding(
                        "ERROR",
                        "final-state-history-mismatch",
                        f"Task {task_id} final state {final_state} does not match last history state {previous_state}",
                    )
                )
            if final_state in {state.value for state in TERMINAL_STATES}:
                continue
            findings.append(
                self._finding(
                    "ERROR",
                    "non-terminal-task-record",
                    f"Task {task_id} ended in non-terminal state {final_state}",
                )
            )

    def _check_dependency_readiness(
        self,
        dag: DagEngine,
        run_trace: dict[str, Any],
        task_records: dict[str, dict[str, Any]],
        findings: list[dict[str, str]],
    ) -> None:
        success_ticks: dict[str, int] = {}
        for event in run_trace.get("scheduler_events", []):
            if event.get("event") == "task-transition" and event.get("state") == "SUCCESS":
                success_ticks[event["task_id"]] = event["execution_tick"]

        seeded_tasks = set(run_trace.get("seeded_tasks", []))
        for task_id, record in sorted(task_records.items()):
            if task_id in seeded_tasks:
                continue
            ready_tick = None
            for entry in record.get("lifecycle_state", {}).get("state_history", []):
                if entry.get("state") == "READY":
                    ready_tick = entry.get("execution_tick")
                    break
            if ready_tick is None:
                continue
            missing_deps = [
                dep
                for dep in sorted(dag.dependencies.get(task_id, set()))
                if success_ticks.get(dep, -1) >= ready_tick or dep not in success_ticks
            ]
            if missing_deps:
                findings.append(
                    self._finding(
                        "ERROR",
                        "dependency-readiness-violation",
                        f"Task {task_id} entered READY before dependencies completed: {', '.join(missing_deps)}",
                    )
                )

    def _check_parallel_failure_propagation(
        self,
        run_trace: dict[str, Any],
        task_records: dict[str, dict[str, Any]],
        findings: list[dict[str, str]],
    ) -> None:
        terminal_failures = {
            task_id
            for task_id, record in task_records.items()
            if record.get("lifecycle_state", {}).get("current_state") == "FAILED"
        }
        failed_tick = None
        for event in run_trace.get("scheduler_events", []):
            if (
                event.get("event") == "task-transition"
                and event.get("state") == "FAILED"
                and event.get("task_id") in terminal_failures
            ):
                failed_tick = event.get("execution_tick")
                break
        if failed_tick is None:
            return
        for event in run_trace.get("scheduler_events", []):
            if event.get("event") == "wave-start" and event.get("execution_tick", 0) > failed_tick:
                findings.append(
                    self._finding(
                        "ERROR",
                        "post-failure-wave-launch",
                        "Scheduler launched a new wave after a task failure was recorded",
                    )
                )
                break

    def _check_downstream_invalidation(
        self,
        dag: DagEngine,
        task_records: dict[str, dict[str, Any]],
        invalidation_report: dict[str, Any],
        findings: list[dict[str, str]],
    ) -> None:
        for event in invalidation_report.get("events", []):
            task_id = event.get("task_id")
            trigger = event.get("triggered_by")
            if not task_id or not trigger:
                continue
            if task_id not in dag.transitive_downstream_for([trigger]):
                findings.append(
                    self._finding(
                        "ERROR",
                        "invalid-downstream-invalidation",
                        f"Task {task_id} was invalidated by non-upstream trigger {trigger}",
                    )
                )
            record = task_records.get(task_id, {})
            current_state = record.get("lifecycle_state", {}).get("current_state")
            if current_state != "INVALIDATED":
                findings.append(
                    self._finding(
                        "ERROR",
                        "missing-invalidated-state",
                        f"Task {task_id} invalidation event exists but task record state is {current_state}",
                    )
                )

    def _check_run_summary(
        self,
        run_trace: dict[str, Any],
        run_summary: dict[str, Any],
        findings: list[dict[str, str]],
    ) -> None:
        execution_summary = run_summary.get("execution_summary", {})
        if execution_summary.get("execution_sequence", []) != run_trace.get("executed_tasks", []):
            findings.append(
                self._finding(
                    "ERROR",
                    "execution-sequence-mismatch",
                    "run-summary execution sequence does not match run-trace executed tasks",
                )
            )
        logical_summary = run_summary.get("logical_clock_summary", {})
        trace_logical = run_trace.get("logical_clock_summary", {})
        if logical_summary != trace_logical:
            findings.append(
                self._finding(
                    "ERROR",
                    "logical-summary-mismatch",
                    "run-summary logical clock summary does not match run-trace logical clock summary",
                )
            )

    def _finding(self, severity: str, code: str, message: str) -> dict[str, str]:
        return {
            "severity": severity,
            "code": code,
            "message": message,
        }
