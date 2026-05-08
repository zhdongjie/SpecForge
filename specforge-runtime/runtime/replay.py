from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a top-level mapping")
    return data


def load_task_records(run_dir: Path) -> dict[str, dict[str, Any]]:
    records_dir = run_dir / "task-records"
    records: dict[str, dict[str, Any]] = {}
    if not records_dir.exists():
        return records
    for path in sorted(records_dir.glob("*.task-run-record.yaml")):
        payload = load_yaml(path)
        task_id = payload.get("execution_identity", {}).get("task_id")
        if task_id:
            records[task_id] = payload
    return records


def load_run_trace(run_dir: Path) -> dict[str, Any]:
    return load_yaml(run_dir / "logs" / "run-trace.yaml")


def build_trace_signature(trace: dict[str, Any]) -> str:
    canonical = json.dumps(trace, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _filter_scheduler_event(event: dict[str, Any], task_subset: set[str] | None) -> dict[str, Any] | None:
    if task_subset is None:
        return dict(event)

    event_task_id = event.get("task_id")
    event_task_ids = event.get("task_ids", [])
    if event_task_id is not None and event_task_id not in task_subset:
        return None
    if event_task_ids and not any(task_id in task_subset for task_id in event_task_ids):
        return None

    filtered_event = dict(event)
    if event_task_ids:
        filtered_event["task_ids"] = [task_id for task_id in event_task_ids if task_id in task_subset]
    if "worker_slots" in filtered_event:
        kept_task_ids = filtered_event.get("task_ids", [])
        filtered_slots = {
            task_id: slot
            for task_id, slot in filtered_event["worker_slots"].items()
            if task_id in task_subset
        }
        if kept_task_ids:
            filtered_event["worker_slots"] = {
                task_id: index
                for index, task_id in enumerate(kept_task_ids)
            }
        else:
            filtered_event["worker_slots"] = filtered_slots
    if "completed_states" in filtered_event:
        filtered_event["completed_states"] = {
            task_id: state
            for task_id, state in filtered_event["completed_states"].items()
            if task_id in task_subset
        }
    if "executed_tasks" in filtered_event:
        filtered_event["executed_tasks"] = [
            task_id for task_id in filtered_event["executed_tasks"] if task_id in task_subset
        ]
    if "worker_slot" in filtered_event and event_task_id is not None:
        filtered_event["worker_slot"] = 0
    return filtered_event


def _rebase_scheduler_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not events:
        return []

    batch_wave_index: dict[str, dict[int, int]] = {}
    for event in events:
        batch_id = event.get("batch_id")
        wave_index = event.get("wave_index")
        if batch_id is None or wave_index is None:
            continue
        mapping = batch_wave_index.setdefault(batch_id, {})
        if wave_index not in mapping:
            mapping[wave_index] = len(mapping)

    tick_map = {
        tick: index
        for index, tick in enumerate(
            sorted(
                {
                    event["execution_tick"]
                    for event in events
                    if "execution_tick" in event
                }
            ),
            start=1,
        )
    }

    rebased: list[dict[str, Any]] = []
    for event in events:
        normalized = dict(event)
        if "wave_index" in normalized and "batch_id" in normalized:
            normalized["wave_index"] = batch_wave_index[normalized["batch_id"]][normalized["wave_index"]]
        if "execution_tick" in normalized:
            rebased_tick = tick_map[normalized["execution_tick"]]
            normalized["execution_tick"] = rebased_tick
            normalized["logical_order_id"] = f"rebased:{rebased_tick:05d}"
        rebased.append(normalized)
    return rebased


def _rebase_task_results(task_results: list[dict[str, Any]], scheduler_events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    used_ticks = sorted(
        {
            tick
            for item in task_results
            for tick in item.get("logical_ticks", [])
        }
    )
    if not used_ticks:
        return task_results
    tick_map = {tick: index for index, tick in enumerate(used_ticks, start=1)}
    rebased: list[dict[str, Any]] = []
    for item in task_results:
        normalized = dict(item)
        normalized["logical_ticks"] = [tick_map[tick] for tick in item.get("logical_ticks", [])]
        rebased.append(normalized)
    return rebased


def normalize_trace(trace: dict[str, Any], task_subset: set[str] | None = None) -> dict[str, Any]:
    task_results = trace.get("task_results", [])
    normalized_results: list[dict[str, Any]] = []
    for item in task_results:
        task_id = item.get("task_id")
        if task_subset is not None and task_id not in task_subset:
            continue
        normalized_results.append(
            {
                "task_id": task_id,
                "final_state": item.get("final_state"),
                "attempts": item.get("attempts"),
                "validation_status": item.get("validation_status"),
                "artifact_files": sorted(item.get("artifact_files", [])),
                "seeded": item.get("seeded", False),
                "logical_ticks": list(item.get("logical_ticks", [])),
            }
        )
    scheduler_events = [
        filtered_event
        for event in trace.get("scheduler_events", [])
        if (filtered_event := _filter_scheduler_event(event, task_subset)) is not None
    ]
    if task_subset is not None:
        scheduler_events = _rebase_scheduler_events(scheduler_events)
        normalized_results = _rebase_task_results(normalized_results, scheduler_events)

    logical_ticks = [
        event["execution_tick"]
        for event in scheduler_events
        if "execution_tick" in event
    ]
    normalized = {
        "affected_tasks": sorted(
            task_id
            for task_id in trace.get("affected_tasks", [])
            if task_subset is None or task_id in task_subset
        ),
        "seeded_tasks": sorted(
            task_id
            for task_id in trace.get("seeded_tasks", [])
            if task_subset is None or task_id in task_subset
        ),
        "executed_tasks": [
            task_id
            for task_id in trace.get("executed_tasks", [])
            if task_subset is None or task_id in task_subset
        ],
        "task_results": normalized_results,
        "scheduler_events": scheduler_events,
        "logical_clock_summary": {
            "final_tick": logical_ticks[-1] if logical_ticks else 0,
            "monotonic": logical_ticks == sorted(logical_ticks),
            "transition_count": sum(1 for event in scheduler_events if event.get("event") == "task-transition"),
            "scheduler_event_count": len(logical_ticks),
        },
    }
    normalized["signature"] = build_trace_signature(normalized)
    return normalized


def compare_traces(
    baseline_trace: dict[str, Any],
    current_trace: dict[str, Any],
    task_subset: set[str] | None = None,
) -> dict[str, Any]:
    baseline_normalized = normalize_trace(baseline_trace, task_subset=task_subset)
    current_normalized = normalize_trace(current_trace, task_subset=task_subset)
    differences: list[str] = []
    if baseline_normalized["executed_tasks"] != current_normalized["executed_tasks"]:
        differences.append("executed_tasks_mismatch")
    if baseline_normalized["task_results"] != current_normalized["task_results"]:
        differences.append("task_results_mismatch")
    if baseline_normalized["scheduler_events"] != current_normalized["scheduler_events"]:
        differences.append("scheduler_events_mismatch")
    if baseline_normalized["logical_clock_summary"] != current_normalized["logical_clock_summary"]:
        differences.append("logical_clock_summary_mismatch")
    return {
        "match": not differences,
        "differences": differences,
        "baseline_signature": baseline_normalized["signature"],
        "current_signature": current_normalized["signature"],
        "baseline_trace": baseline_normalized,
        "current_trace": current_normalized,
    }
