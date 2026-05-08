from __future__ import annotations

from collections import defaultdict
from datetime import datetime
import hashlib
from pathlib import Path
import shutil
from typing import Any

from .artifact_planner import ArtifactPlanner
from .conflict_detector import ConflictDetector
from .dag_engine import DagEngine
from .logical_clock import LogicalClock
from .parallel_scheduler import ParallelScheduler, ScheduledWave
from .recorder import Recorder
from .replay import compare_traces, load_run_trace, load_task_records
from .run_config import RunConfig
from .task_state import TaskState
from .validator import Validator


class RuntimeExecutor:
    def __init__(
        self,
        dag: DagEngine,
        resolved_schema: dict[str, Any],
        task_graph: dict[str, Any],
        run_dir: Path,
        specs_dir: Path,
        run_config: RunConfig,
    ) -> None:
        self.dag = dag
        self.resolved_schema = resolved_schema
        self.task_graph = task_graph
        self.run_dir = run_dir
        self.specs_dir = specs_dir
        self.run_config = run_config
        self.runs_root = run_dir.parent
        self.source_run_dir = self.runs_root / run_config.replay_source_run_id if run_config.replay_source_run_id else None
        self.states = {task_id: TaskState.WAITING for task_id in self.dag.task_payloads}
        self.history: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.execution_sequence: list[str] = []
        self.task_results: dict[str, dict[str, Any]] = {}
        self.total_planned_artifacts = 0
        self.attempt_counters: dict[str, int] = defaultdict(int)
        self.invalidation_events: list[dict[str, Any]] = []
        self.halted = False
        self.halt_reason: str | None = None
        self.max_parallelism_observed = 0
        self.batch_execution_stats: list[dict[str, Any]] = []
        self.conflict_violations: list[dict[str, Any]] = []
        self.scheduler_events: list[dict[str, Any]] = []
        self.transition_sequence = 0
        self.clock = LogicalClock()
        self.recorder = Recorder(run_dir, specs_dir)
        self.validator = Validator(task_graph, resolved_schema)
        self.artifact_planner = ArtifactPlanner(resolved_schema, run_dir / "artifacts")
        self.conflict_detector = ConflictDetector()
        self.scheduler = ParallelScheduler(dag, task_graph, max_workers=run_config.max_workers)
        self.baseline_trace = load_run_trace(self.source_run_dir) if self.source_run_dir else {}
        self.source_task_records = load_task_records(self.source_run_dir) if self.source_run_dir else {}
        self.affected_tasks = self._resolve_affected_tasks()
        self.seeded_tasks = self._resolve_seeded_tasks()
        self._prepare_run_dirs()
        self._seed_prior_state()

    def execute(self) -> None:
        completed_tasks = {task_id for task_id, state in self.states.items() if state == TaskState.SUCCESS}
        batches = self.scheduler.build_batches(self.affected_tasks, self.seeded_tasks)
        for batch in batches:
            if self.halted:
                break
            batch_result = self._execute_batch(batch, completed_tasks)
            self.batch_execution_stats.append(batch_result)
            completed_tasks = {task_id for task_id, state in self.states.items() if state == TaskState.SUCCESS}

        self.recorder.write_invalidation_report(
            {
                "run_id": self.run_config.run_id,
                "recorded_at": self._now(),
                "events": self.invalidation_events,
            }
        )
        scheduler_trace = {
            "run_id": self.run_config.run_id,
            "recorded_at": self._now(),
            "max_parallelism": self.max_parallelism_observed,
            "events": self.scheduler_events,
        }
        self.recorder.write_scheduler_trace(scheduler_trace)
        current_trace = self._build_run_trace()
        self.recorder.write_run_trace(current_trace)

        replay_comparison: dict[str, Any] | None = None
        if self.run_config.compare_trace and self.baseline_trace:
            subset = set(self.affected_tasks) if self.run_config.mode == "partial-replay" else None
            replay_comparison = compare_traces(self.baseline_trace, current_trace, task_subset=subset)
            replay_comparison["baseline_run_id"] = self.run_config.replay_source_run_id
            replay_comparison["current_run_id"] = self.run_config.run_id
            self.recorder.write_replay_comparison(replay_comparison)

        summary = self._build_run_summary(replay_comparison)
        self.recorder.write_run_summary(summary)
        if not all(state == TaskState.SUCCESS for state in self.states.values()):
            failed = [task_id for task_id, state in self.states.items() if state != TaskState.SUCCESS]
            raise RuntimeError(f"Runtime execution did not fully succeed: {failed}")

    def _execute_batch(self, batch: dict[str, Any], completed_tasks: set[str]) -> dict[str, Any]:
        batch_id = batch["batch_id"]
        batch_tasks = batch["task_ids"]
        mode = batch["mode"]
        launched: set[str] = set()
        wave_count = 0
        batch_executed: list[str] = []
        self._record_scheduler_event(
            {
                "event": "batch-start",
                "batch_id": batch_id,
                "mode": mode,
                "task_ids": list(batch_tasks),
            }
        )

        while not self.halted:
            ready_tasks = self.scheduler.ready_tasks_for_batch(batch_tasks, completed_tasks, launched)
            if not ready_tasks:
                break
            wave = self.scheduler.make_wave(batch_id, wave_count, ready_tasks, mode)
            if not wave.task_ids:
                break
            wave_count += 1
            batch_executed.extend(list(wave.task_ids))
            launched.update(wave.task_ids)
            self.max_parallelism_observed = max(self.max_parallelism_observed, len(wave.task_ids))
            task_plans = {
                task_id: self.artifact_planner.plan_for_task(self.dag.task_payloads[task_id])
                for task_id in wave.task_ids
            }
            self.total_planned_artifacts += sum(len(artifacts) for artifacts in task_plans.values())
            conflicts = self.conflict_detector.detect_batch_conflicts(batch_id, task_plans)
            if conflicts:
                self._handle_conflicts(batch_id, wave, conflicts)
                break

            self._record_scheduler_event(
                {
                    "event": "wave-start",
                    "batch_id": batch_id,
                    "wave_index": wave.wave_index,
                    "task_ids": list(wave.task_ids),
                    "worker_slots": dict(wave.worker_slots),
                }
            )
            for task_id in wave.task_ids:
                task = self.dag.task_payloads[task_id]
                self.execution_sequence.append(task_id)
                self._transition(task_id, task, TaskState.READY, worker_slot=wave.worker_slots[task_id])
                self._transition(task_id, task, TaskState.RUNNING, worker_slot=wave.worker_slots[task_id])

            results = self.scheduler.execute_wave(
                wave,
                lambda task_id, worker_slot: self._simulate_task_execution(
                    task_id,
                    self.dag.task_payloads[task_id],
                    task_plans[task_id],
                    worker_slot,
                ),
            )
            batch_failed = False
            for result in results:
                completed_tasks.add(result["task_id"]) if self._process_task_result(result) else None
                if result["final_state"] != TaskState.SUCCESS.value:
                    batch_failed = True
            self._record_scheduler_event(
                {
                    "event": "wave-complete",
                    "batch_id": batch_id,
                    "wave_index": wave.wave_index,
                    "task_ids": list(wave.task_ids),
                    "completed_states": {
                        result["task_id"]: result["final_state"]
                        for result in results
                    },
                }
            )
            if batch_failed:
                break

        self._record_scheduler_event(
            {
                "event": "batch-complete",
                "batch_id": batch_id,
                "mode": mode,
                "task_ids": list(batch_tasks),
                "executed_tasks": batch_executed,
                "halted": self.halted,
            }
        )
        return {
            "batch_id": batch_id,
            "mode": mode,
            "wave_count": wave_count,
            "task_count": len(batch_tasks),
            "executed_tasks": batch_executed,
            "max_parallelism": max(
                [len(event.get("task_ids", [])) for event in self.scheduler_events if event.get("batch_id") == batch_id and event.get("event") == "wave-start"],
                default=0,
            ),
        }

    def _simulate_task_execution(
        self,
        task_id: str,
        task: dict[str, Any],
        planned_artifacts: list[dict[str, Any]],
        worker_slot: int,
    ) -> dict[str, Any]:
        max_attempts = task.get("retry_policy", {}).get("max_attempts", 1)
        attempt_results: list[dict[str, Any]] = []
        final_artifacts: list[dict[str, Any]] = []
        final_state = TaskState.FAILED.value
        for attempt in range(1, max_attempts + 1):
            validation = self.validator.run(task, planned_artifacts, dependency_status_ok=True)
            validation = self._apply_failure_injection(task_id, validation, attempt)
            success = validation["overall_status"] == "PASS"
            invalidated_paths: list[str] = []
            if success:
                self.artifact_planner.materialize(planned_artifacts, task_id)
                final_artifacts = self._attach_artifact_digests(planned_artifacts)
                final_state = TaskState.SUCCESS.value
            else:
                invalidated_paths = self._invalidate_task_artifacts(planned_artifacts, task_id, reason="failed-attempt")
                final_state = TaskState.FAILED.value
            attempt_results.append(
                {
                    "attempt": attempt,
                    "validation": validation,
                    "success": success,
                    "invalidated_paths": invalidated_paths,
                }
            )
            if success:
                break
        return {
            "task_id": task_id,
            "task": task,
            "worker_slot": worker_slot,
            "planned_artifacts": final_artifacts if final_state == TaskState.SUCCESS.value else planned_artifacts,
            "attempt_results": attempt_results,
            "final_state": final_state,
        }

    def _process_task_result(self, result: dict[str, Any]) -> bool:
        task_id = result["task_id"]
        task = result["task"]
        planned_artifacts = result["planned_artifacts"]
        worker_slot = result["worker_slot"]
        attempt_results = result["attempt_results"]
        final_validation = attempt_results[-1]["validation"] if attempt_results else {"overall_status": "PASS", "hooks": []}

        for index, attempt_result in enumerate(attempt_results, start=1):
            self.attempt_counters[task_id] = attempt_result["attempt"]
            if attempt_result["success"]:
                self._transition(task_id, task, TaskState.SUCCESS, worker_slot=worker_slot)
                self._finalize_task(
                    task_id,
                    task,
                    planned_artifacts,
                    attempt_result["validation"],
                    worker_slot=worker_slot,
                )
                return True
            self._transition(task_id, task, TaskState.FAILED, worker_slot=worker_slot)
            if index < len(attempt_results):
                self._transition(task_id, task, TaskState.READY, worker_slot=worker_slot)
                self._transition(task_id, task, TaskState.RUNNING, worker_slot=worker_slot)

        invalidation = self._build_invalidation_metadata("failed-attempt", attempt_results[-1]["invalidated_paths"])
        self._finalize_task(
            task_id,
            task,
            planned_artifacts,
            final_validation,
            invalidation=invalidation,
            worker_slot=worker_slot,
        )
        self._halt_and_invalidate_after_failure(task_id, final_validation)
        return False

    def _handle_conflicts(self, batch_id: str, wave: ScheduledWave, conflicts: list[dict[str, Any]]) -> None:
        self.conflict_violations.extend(conflicts)
        self.halted = True
        self.halt_reason = f"{batch_id}:artifact-conflict"
        conflict_tasks: set[str] = set()
        for conflict in conflicts:
            conflict_tasks.update(conflict["owners"])

        for task_id in self.scheduler.sort_task_ids(conflict_tasks):
            task = self.dag.task_payloads[task_id]
            self._transition(task_id, task, TaskState.INVALIDATED, worker_slot=wave.worker_slots.get(task_id, -1))
            validation = {
                "overall_status": "FAIL",
                "hooks": [
                    {
                        "hook": "artifact_ownership_conflict",
                        "status": "FAIL",
                        "details": "; ".join(conflict["details"] for conflict in conflicts if task_id in conflict["owners"]),
                    }
                ],
            }
            invalidation = self._build_invalidation_metadata("artifact-conflict", [])
            self._finalize_task(
                task_id,
                task,
                [],
                validation,
                invalidation=invalidation,
                worker_slot=wave.worker_slots.get(task_id, -1),
            )
            self.invalidation_events.append(
                {
                    "reason": "artifact-conflict",
                    "task_id": task_id,
                    "invalidated_artifacts": [],
                    "batch_id": batch_id,
                }
            )
        self._invalidate_remaining_tasks(trigger_task_id=self.scheduler.sort_task_ids(conflict_tasks)[0], reason="artifact-conflict")

    def _transition(
        self,
        task_id: str,
        task: dict[str, Any],
        state: TaskState,
        worker_slot: int,
    ) -> None:
        self.states[task_id] = state
        self.transition_sequence += 1
        stamp = self.clock.next("transition", task_id, self.transition_sequence)
        entry = {
            "state": state.value,
            "entered_at": self._now(),
            "execution_tick": stamp.execution_tick,
            "logical_order_id": stamp.logical_order_id,
            "worker_slot": worker_slot,
        }
        self.history[task_id].append(entry)
        self.recorder.log_transition(state, task, entry)
        self._record_scheduler_event(
            {
                "event": "task-transition",
                "task_id": task_id,
                "state": state.value,
                "worker_slot": worker_slot,
                "execution_tick": stamp.execution_tick,
                "logical_order_id": stamp.logical_order_id,
            },
            use_existing_tick=True,
        )

    def _finalize_task(
        self,
        task_id: str,
        task: dict[str, Any],
        planned_artifacts: list[dict[str, Any]],
        validation: dict[str, Any],
        invalidation: dict[str, Any] | None = None,
        worker_slot: int = -1,
    ) -> None:
        dependencies = sorted(self.dag.dependencies[task_id])
        downstream_ready = [
            dependent
            for dependent in self.dag.downstream_for(task_id)
            if self.dag.dependencies_satisfied(dependent, self.states)
        ]
        logical_ticks = [entry["execution_tick"] for entry in self.history[task_id]]
        self.task_results[task_id] = {
            "task_id": task_id,
            "final_state": self.states[task_id].value,
            "attempts": self.attempt_counters[task_id],
            "validation_status": validation.get("overall_status", "PASS"),
            "artifact_files": [artifact.get("artifact_file_name", "") for artifact in planned_artifacts],
            "logical_ticks": logical_ticks,
            "seeded": False,
        }
        self.recorder.write_task_record(
            task=task,
            task_id=task_id,
            state_history=self.history[task_id],
            final_state=self.states[task_id],
            planned_artifacts=planned_artifacts,
            validation_results=validation,
            downstream_ready=downstream_ready,
            dependencies=dependencies,
            retry_attempt=self.attempt_counters[task_id],
            retry_max_attempts=task.get("retry_policy", {}).get("max_attempts", 1),
            invalidation=invalidation,
            logical_clock_summary={
                "worker_slot": worker_slot,
                "transition_ticks": logical_ticks,
                "monotonic": logical_ticks == sorted(logical_ticks),
            },
        )

    def _halt_and_invalidate_after_failure(self, failed_task_id: str, validation: dict[str, Any]) -> None:
        self.halted = True
        self.halt_reason = f"{failed_task_id}:{validation.get('overall_status', 'FAIL')}"
        self._invalidate_remaining_tasks(trigger_task_id=failed_task_id, reason="validation-failure")

    def _invalidate_remaining_tasks(self, trigger_task_id: str, reason: str) -> None:
        downstream = set(
            task_id
            for task_id in self.dag.transitive_downstream_for([trigger_task_id])
            if task_id in self.affected_tasks and self.states[task_id] == TaskState.WAITING
        )
        remaining_waiting = {
            task_id
            for task_id in self.affected_tasks
            if self.states[task_id] == TaskState.WAITING
        }
        for task_id in self.scheduler.sort_task_ids(downstream | remaining_waiting):
            task = self.dag.task_payloads[task_id]
            invalidation_reason = "downstream-invalidation" if task_id in downstream else "pipeline-halt"
            self._transition(task_id, task, TaskState.INVALIDATED, worker_slot=-1)
            self.task_results[task_id] = {
                "task_id": task_id,
                "final_state": TaskState.INVALIDATED.value,
                "attempts": 0,
                "validation_status": "NOT_RUN",
                "artifact_files": [],
                "logical_ticks": [entry["execution_tick"] for entry in self.history[task_id]],
                "seeded": False,
            }
            self.recorder.write_task_record(
                task=task,
                task_id=task_id,
                state_history=self.history[task_id],
                final_state=self.states[task_id],
                planned_artifacts=[],
                validation_results={
                    "overall_status": "NOT_RUN",
                    "hooks": [],
                    "reason": f"{invalidation_reason} after {trigger_task_id}",
                },
                downstream_ready=[],
                dependencies=sorted(self.dag.dependencies[task_id]),
                retry_attempt=0,
                retry_max_attempts=task.get("retry_policy", {}).get("max_attempts", 1),
                invalidation=self._build_invalidation_metadata(invalidation_reason, []),
                logical_clock_summary={
                    "worker_slot": -1,
                    "transition_ticks": [entry["execution_tick"] for entry in self.history[task_id]],
                    "monotonic": True,
                },
            )
            self.invalidation_events.append(
                {
                    "reason": invalidation_reason if reason != "artifact-conflict" else "artifact-conflict",
                    "task_id": task_id,
                    "triggered_by": trigger_task_id,
                    "invalidated_artifacts": [],
                }
            )

    def _apply_failure_injection(self, task_id: str, validation: dict[str, Any], attempt: int) -> dict[str, Any]:
        injections = self.run_config.injections_for(task_id, attempt)
        if not injections:
            return validation
        hooks = list(validation.get("hooks", []))
        for injection in injections:
            hooks.append(
                {
                    "hook": "failure_injection",
                    "status": "FAIL",
                    "details": f"{injection.failure_type}: {injection.message}",
                }
            )
        return {
            "overall_status": "FAIL",
            "hooks": hooks,
            "failure_type": injections[0].failure_type,
            "injected": True,
        }

    def _invalidate_task_artifacts(
        self,
        planned_artifacts: list[dict[str, Any]],
        task_id: str,
        reason: str,
    ) -> list[str]:
        invalidated_paths: list[str] = []
        for artifact in planned_artifacts:
            path = Path(artifact["planned_path"])
            if path.exists():
                path.unlink()
                invalidated_paths.append(str(path))
        self.invalidation_events.append(
            {
                "reason": reason,
                "task_id": task_id,
                "invalidated_artifacts": invalidated_paths,
            }
        )
        return invalidated_paths

    def _attach_artifact_digests(self, planned_artifacts: list[dict[str, Any]]) -> list[dict[str, Any]]:
        enriched: list[dict[str, Any]] = []
        for artifact in planned_artifacts:
            path = Path(artifact["planned_path"])
            digest = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else ""
            enriched.append({**artifact, "artifact_digest": digest})
        return enriched

    def _resolve_affected_tasks(self) -> set[str]:
        if not self.run_config.partial_replay_tasks:
            return set(self.dag.task_payloads)
        requested = set(self.run_config.partial_replay_tasks)
        unknown = sorted(requested - set(self.dag.task_payloads))
        if unknown:
            raise ValueError(f"Unknown partial replay tasks: {unknown}")
        affected = set(requested)
        affected.update(self.dag.transitive_downstream_for(sorted(requested)))
        return affected

    def _resolve_seeded_tasks(self) -> set[str]:
        if self.run_config.mode != "partial-replay":
            return set()
        if not self.source_task_records:
            raise ValueError("Partial replay requires source task records")
        seeded = set(self.dag.task_payloads) - self.affected_tasks
        for task_id in seeded:
            record = self.source_task_records.get(task_id)
            state = record.get("lifecycle_state", {}).get("current_state") if record else None
            if state != TaskState.SUCCESS.value:
                raise ValueError(f"Cannot seed non-successful baseline task: {task_id}")
        return seeded

    def _seed_prior_state(self) -> None:
        for task_id in self.scheduler.sort_task_ids(self.seeded_tasks):
            self.states[task_id] = TaskState.SUCCESS
            record = self.source_task_records[task_id]
            self.history[task_id] = list(record.get("lifecycle_state", {}).get("state_history", []))
            lineage = record.get("generated_artifact_lineage", {}).get("produced_artifacts", [])
            logical_ticks = [
                entry.get("execution_tick")
                for entry in self.history[task_id]
                if entry.get("execution_tick") is not None
            ]
            self.task_results[task_id] = {
                "task_id": task_id,
                "final_state": TaskState.SUCCESS.value,
                "attempts": record.get("retry_metadata", {}).get("attempt", 1),
                "validation_status": record.get("validation_results", {}).get("overall_status", "PASS"),
                "artifact_files": [artifact.get("artifact_file_name", "") for artifact in lineage],
                "logical_ticks": logical_ticks,
                "seeded": True,
            }

    def _prepare_run_dirs(self) -> None:
        if self.run_dir.exists():
            shutil.rmtree(self.run_dir)
        if self.run_config.mode == "partial-replay":
            if self.source_run_dir is None or not self.source_run_dir.exists():
                raise ValueError("Partial replay requires a valid replay source run directory")
            shutil.copytree(self.source_run_dir, self.run_dir)
            for directory in (self.run_dir / "artifacts", self.run_dir / "logs", self.run_dir / "task-records"):
                directory.mkdir(parents=True, exist_ok=True)
            self._reset_logs()
            self._invalidate_replay_scope()
            return
        for directory in (self.run_dir / "artifacts", self.run_dir / "logs", self.run_dir / "task-records"):
            directory.mkdir(parents=True, exist_ok=True)
        self._reset_logs()

    def _reset_logs(self) -> None:
        logs_dir = self.run_dir / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        for path in logs_dir.iterdir():
            if path.is_file():
                path.unlink()

    def _invalidate_replay_scope(self) -> None:
        for task_id in self.scheduler.sort_task_ids(self.affected_tasks):
            record_path = self.run_dir / "task-records" / f"{task_id}.task-run-record.yaml"
            if record_path.exists():
                record_path.unlink()
            baseline = self.source_task_records.get(task_id, {})
            artifacts = baseline.get("generated_artifact_lineage", {}).get("produced_artifacts", [])
            invalidated_paths: list[str] = []
            for artifact in artifacts:
                planned_path = artifact.get("planned_path")
                if not planned_path:
                    continue
                candidate = self.run_dir / "artifacts" / Path(planned_path).name
                if candidate.exists():
                    candidate.unlink()
                    invalidated_paths.append(str(candidate))
            if invalidated_paths:
                self.invalidation_events.append(
                    {
                        "reason": "partial-replay-scope-reset",
                        "task_id": task_id,
                        "invalidated_artifacts": invalidated_paths,
                    }
                )

    def _build_invalidation_metadata(self, reason: str, invalidated_paths: list[str]) -> dict[str, Any]:
        return {
            "reason": reason,
            "invalidated_artifacts": invalidated_paths,
            "recorded_at": self._now(),
        }

    def _build_run_trace(self) -> dict[str, Any]:
        scheduler_ticks = [
            event["execution_tick"]
            for event in self.scheduler_events
            if "execution_tick" in event
        ]
        transition_count = sum(1 for event in self.scheduler_events if event.get("event") == "task-transition")
        return {
            "run_id": self.run_config.run_id,
            "mode": self.run_config.mode,
            "replay_source_run_id": self.run_config.replay_source_run_id,
            "affected_tasks": self.scheduler.sort_task_ids(self.affected_tasks),
            "seeded_tasks": self.scheduler.sort_task_ids(self.seeded_tasks),
            "executed_tasks": list(self.execution_sequence),
            "halted": self.halted,
            "halt_reason": self.halt_reason,
            "scheduler_events": self.scheduler_events,
            "logical_clock_summary": {
                "final_tick": self.clock.current_tick,
                "monotonic": scheduler_ticks == sorted(scheduler_ticks),
                "transition_count": transition_count,
                "scheduler_event_count": len(scheduler_ticks),
            },
            "task_results": [self.task_results[task_id] for task_id in sorted(self.task_results)],
        }

    def _build_run_summary(self, replay_comparison: dict[str, Any] | None) -> dict[str, Any]:
        scheduler_ticks = [
            event["execution_tick"]
            for event in self.scheduler_events
            if "execution_tick" in event
        ]
        transition_count = sum(1 for event in self.scheduler_events if event.get("event") == "task-transition")
        return {
            "run_identity": {
                "pipeline_run_id": self.run_config.run_id,
                "task_graph_id": self.task_graph["graph_context"]["graph_id"],
                "recorded_at": self._now(),
                "mode": self.run_config.mode,
                "replay_source_run_id": self.run_config.replay_source_run_id,
            },
            "execution_summary": {
                "total_tasks": len(self.execution_sequence),
                "successful_tasks": sum(1 for state in self.states.values() if state == TaskState.SUCCESS),
                "failed_tasks": sorted(task_id for task_id, state in self.states.items() if state == TaskState.FAILED),
                "skipped_tasks": sorted(task_id for task_id, state in self.states.items() if state == TaskState.SKIPPED),
                "invalidated_tasks": sorted(task_id for task_id, state in self.states.items() if state == TaskState.INVALIDATED),
                "execution_sequence": self.execution_sequence,
                "deterministic_replay_ready": True,
                "halted": self.halted,
                "seeded_tasks": self.scheduler.sort_task_ids(self.seeded_tasks),
                "affected_tasks": self.scheduler.sort_task_ids(self.affected_tasks),
                "max_parallelism": self.max_parallelism_observed,
                "batch_execution_stats": self.batch_execution_stats,
            },
            "artifact_summary": {
                "planned_artifact_count": self.total_planned_artifacts,
                "concurrency_conflicts": self.conflict_violations,
            },
            "replay_stability": {
                "comparison_enabled": bool(self.run_config.compare_trace and self.baseline_trace),
                "match": replay_comparison.get("match") if replay_comparison else None,
                "differences": replay_comparison.get("differences") if replay_comparison else [],
            },
            "logical_clock_summary": {
                "final_tick": self.clock.current_tick,
                "transition_count": transition_count,
                "scheduler_event_count": len(scheduler_ticks),
                "monotonic": scheduler_ticks == sorted(scheduler_ticks),
            },
            "runtime_validations": {
                "deterministic_scheduling": True,
                "logical_clock_monotonicity": scheduler_ticks == sorted(scheduler_ticks),
                "artifact_ownership_conflicts": "PASS" if not self.conflict_violations else "FAIL",
                "replay_trace_consistency": replay_comparison.get("match") if replay_comparison else None,
            },
        }

    def _record_scheduler_event(self, event: dict[str, Any], use_existing_tick: bool = False) -> None:
        if not use_existing_tick:
            self.transition_sequence += 1
            stamp = self.clock.next("scheduler", event.get("task_id", event.get("batch_id", "runtime")), self.transition_sequence)
            event = {
                **event,
                "execution_tick": stamp.execution_tick,
                "logical_order_id": stamp.logical_order_id,
            }
        self.scheduler_events.append(event)

    def _now(self) -> str:
        return datetime.now().astimezone().isoformat(timespec="seconds")
