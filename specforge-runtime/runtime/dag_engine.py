from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Any

from .task_state import TaskState


@dataclass(frozen=True)
class TaskNode:
    task_id: str
    payload: dict[str, Any]


class DagEngine:
    def __init__(self, task_graph: dict[str, Any]) -> None:
        self.task_graph = task_graph
        self.task_payloads = {
            task["task_id"]: task for task in task_graph.get("task_units", [])
        }
        self.dependencies: dict[str, set[str]] = defaultdict(set)
        self.dependents: dict[str, set[str]] = defaultdict(set)
        for edge in task_graph.get("dependency_edges", []):
            src = edge["from"]
            dst = edge["to"]
            self.dependencies[dst].add(src)
            self.dependents[src].add(dst)

        for task_id in self.task_payloads:
            self.dependencies.setdefault(task_id, set())
            self.dependents.setdefault(task_id, set())

        self.serial_order = task_graph.get("execution_order", {}).get("serial_order", [])

    def validate_acyclic(self) -> None:
        indegree = {task_id: len(deps) for task_id, deps in self.dependencies.items()}
        queue = deque(sorted(task_id for task_id, degree in indegree.items() if degree == 0))
        visited: list[str] = []
        while queue:
            current = queue.popleft()
            visited.append(current)
            for dependent in sorted(self.dependents[current]):
                indegree[dependent] -= 1
                if indegree[dependent] == 0:
                    queue.append(dependent)
        if len(visited) != len(indegree):
            raise ValueError("Cyclic dependency detected in generation task graph")

    def validate_serial_order(self) -> None:
        if not self.serial_order:
            return
        known = set(self.task_payloads)
        listed = set(self.serial_order)
        if known != listed:
            missing = sorted(known - listed)
            extra = sorted(listed - known)
            raise ValueError(f"Serial order mismatch. Missing={missing}, extra={extra}")
        positions = {task_id: index for index, task_id in enumerate(self.serial_order)}
        for task_id, deps in self.dependencies.items():
            for dep in deps:
                if positions[dep] > positions[task_id]:
                    raise ValueError(
                        f"Invalid serial order: dependency {dep} appears after {task_id}"
                    )

    def get_execution_sequence(self) -> list[TaskNode]:
        if self.serial_order:
            return [TaskNode(task_id=task_id, payload=self.task_payloads[task_id]) for task_id in self.serial_order]
        indegree = {task_id: len(deps) for task_id, deps in self.dependencies.items()}
        queue = deque(sorted(task_id for task_id, degree in indegree.items() if degree == 0))
        ordered: list[TaskNode] = []
        while queue:
            current = queue.popleft()
            ordered.append(TaskNode(task_id=current, payload=self.task_payloads[current]))
            for dependent in sorted(self.dependents[current]):
                indegree[dependent] -= 1
                if indegree[dependent] == 0:
                    queue.append(dependent)
        return ordered

    def dependencies_satisfied(self, task_id: str, states: dict[str, TaskState]) -> bool:
        return all(states[dep] == TaskState.SUCCESS for dep in self.dependencies[task_id])

    def downstream_for(self, task_id: str) -> list[str]:
        return sorted(self.dependents.get(task_id, set()))

    def transitive_downstream_for(self, task_ids: list[str] | set[str] | tuple[str, ...]) -> list[str]:
        pending = deque(sorted(task_ids))
        visited: set[str] = set()
        while pending:
            current = pending.popleft()
            for dependent in sorted(self.dependents.get(current, set())):
                if dependent in visited:
                    continue
                visited.add(dependent)
                pending.append(dependent)
        return sorted(visited)
