from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any, Callable

from .dag_engine import DagEngine


@dataclass(frozen=True)
class ScheduledWave:
    batch_id: str
    wave_index: int
    task_ids: tuple[str, ...]
    worker_slots: dict[str, int]


class ParallelScheduler:
    def __init__(
        self,
        dag: DagEngine,
        task_graph: dict[str, Any],
        max_workers: int = 4,
    ) -> None:
        self.dag = dag
        self.task_graph = task_graph
        self.max_workers = max_workers
        self.batch_specs = task_graph.get("parallel_batches", [])
        fallback = [task["task_id"] for task in task_graph.get("task_units", [])]
        self.order_reference = dag.serial_order or fallback
        self.order_index = {task_id: index for index, task_id in enumerate(self.order_reference)}

    def build_batches(self, affected_tasks: set[str], seeded_tasks: set[str]) -> list[dict[str, Any]]:
        batches: list[dict[str, Any]] = []
        included: set[str] = set()
        for batch_spec in self.batch_specs:
            task_ids = [
                task_id
                for task_id in batch_spec.get("tasks", [])
                if task_id in affected_tasks and task_id not in seeded_tasks
            ]
            if not task_ids:
                continue
            ordered_tasks = sorted(task_ids, key=self._sort_key)
            batches.append(
                {
                    "batch_id": batch_spec["batch_id"],
                    "mode": batch_spec.get("mode", "parallel"),
                    "task_ids": ordered_tasks,
                }
            )
            included.update(ordered_tasks)

        remaining = sorted(
            [task_id for task_id in affected_tasks if task_id not in seeded_tasks and task_id not in included],
            key=self._sort_key,
        )
        for task_id in remaining:
            batches.append({"batch_id": f"SERIAL-{task_id}", "mode": "serial", "task_ids": [task_id]})
        return batches

    def ready_tasks_for_batch(
        self,
        batch_tasks: list[str],
        completed_tasks: set[str],
        launched_tasks: set[str],
    ) -> list[str]:
        ready: list[str] = []
        for task_id in batch_tasks:
            if task_id in launched_tasks:
                continue
            if all(dep in completed_tasks for dep in self.dag.dependencies[task_id]):
                ready.append(task_id)
        return sorted(ready, key=self._sort_key)

    def make_wave(
        self,
        batch_id: str,
        wave_index: int,
        ready_tasks: list[str],
        mode: str,
    ) -> ScheduledWave:
        if mode.startswith("serial"):
            selected = ready_tasks[:1]
        else:
            selected = ready_tasks[: self.max_workers]
        worker_slots = {task_id: index for index, task_id in enumerate(selected)}
        return ScheduledWave(
            batch_id=batch_id,
            wave_index=wave_index,
            task_ids=tuple(selected),
            worker_slots=worker_slots,
        )

    def execute_wave(
        self,
        wave: ScheduledWave,
        worker_fn: Callable[[str, int], dict[str, Any]],
    ) -> list[dict[str, Any]]:
        if not wave.task_ids:
            return []
        results: dict[str, dict[str, Any]] = {}
        with ThreadPoolExecutor(max_workers=len(wave.task_ids), thread_name_prefix=wave.batch_id) as executor:
            future_map = {
                executor.submit(worker_fn, task_id, wave.worker_slots[task_id]): task_id
                for task_id in wave.task_ids
            }
            for future, task_id in future_map.items():
                results[task_id] = future.result()
        return [results[task_id] for task_id in sorted(results, key=self._sort_key)]

    def sort_task_ids(self, task_ids: list[str] | set[str] | tuple[str, ...]) -> list[str]:
        return sorted(task_ids, key=self._sort_key)

    def _sort_key(self, task_id: str) -> tuple[int, str]:
        return (self.order_index[task_id], task_id)
