from __future__ import annotations

from typing import Any

from .dag_engine import DagEngine


class GraphValidator:
    def validate(self, task_graph: dict[str, Any]) -> dict[str, Any]:
        findings: list[dict[str, str]] = []
        task_units = task_graph.get("task_units", [])
        task_ids = [task.get("task_id", "") for task in task_units if task.get("task_id")]
        known_tasks = set(task_ids)

        self._check_duplicate_task_ids(task_ids, findings)
        self._check_dependency_references(task_graph, known_tasks, findings)
        self._check_parallel_batches(task_graph, known_tasks, findings)
        self._check_integration_checkpoints(task_graph, known_tasks, findings)
        self._check_boundary_enforcement(task_graph, findings)
        self._check_dag_validity(task_graph, findings)

        return {
            "validator": "graph-validator",
            "passed": not any(finding["severity"] == "ERROR" for finding in findings),
            "finding_count": len(findings),
            "findings": findings,
        }

    def _check_duplicate_task_ids(self, task_ids: list[str], findings: list[dict[str, str]]) -> None:
        seen: set[str] = set()
        duplicates: list[str] = []
        for task_id in task_ids:
            if task_id in seen and task_id not in duplicates:
                duplicates.append(task_id)
            seen.add(task_id)
        if duplicates:
            findings.append(
                self._finding(
                    "ERROR",
                    "duplicate-task-ids",
                    f"Task graph contains duplicate task ids: {', '.join(sorted(duplicates))}",
                )
            )

    def _check_dependency_references(
        self,
        task_graph: dict[str, Any],
        known_tasks: set[str],
        findings: list[dict[str, str]],
    ) -> None:
        unknown_nodes: set[str] = set()
        for edge in task_graph.get("dependency_edges", []):
            src = edge.get("from", "")
            dst = edge.get("to", "")
            if src not in known_tasks:
                unknown_nodes.add(src)
            if dst not in known_tasks:
                unknown_nodes.add(dst)
        if unknown_nodes:
            findings.append(
                self._finding(
                    "ERROR",
                    "unknown-dependency-node",
                    f"Dependency edges reference unknown tasks: {', '.join(sorted(unknown_nodes))}",
                )
            )

    def _check_parallel_batches(
        self,
        task_graph: dict[str, Any],
        known_tasks: set[str],
        findings: list[dict[str, str]],
    ) -> None:
        batch_membership: dict[str, list[str]] = {}
        batch_ids: set[str] = set()
        batch_order: dict[str, int] = {}
        serial_index = {
            task_id: index
            for index, task_id in enumerate(task_graph.get("execution_order", {}).get("serial_order", []))
        }
        dependency_pairs = {
            (edge.get("from", ""), edge.get("to", ""))
            for edge in task_graph.get("dependency_edges", [])
        }

        batches = task_graph.get("parallel_batches", [])
        for batch_index, batch in enumerate(batches):
            batch_id = batch.get("batch_id", "")
            if not batch_id:
                findings.append(self._finding("ERROR", "missing-batch-id", "Parallel batch is missing batch_id"))
                continue
            if batch_id in batch_ids:
                findings.append(
                    self._finding("ERROR", "duplicate-batch-id", f"Parallel batch id is duplicated: {batch_id}")
                )
            batch_ids.add(batch_id)
            batch_order[batch_id] = batch_index
            task_list = batch.get("tasks", [])
            for task_id in task_list:
                if task_id not in known_tasks:
                    findings.append(
                        self._finding(
                            "ERROR",
                            "unknown-batch-task",
                            f"Parallel batch {batch_id} references unknown task {task_id}",
                        )
                    )
                    continue
                batch_membership.setdefault(task_id, []).append(batch_id)

            self._check_batch_ordering(batch_id, task_list, serial_index, findings)
            self._check_intra_batch_dependencies(batch, dependency_pairs, findings)

        duplicated_membership = {
            task_id: batches_for_task
            for task_id, batches_for_task in batch_membership.items()
            if len(batches_for_task) > 1
        }
        for task_id, batches_for_task in sorted(duplicated_membership.items()):
            findings.append(
                self._finding(
                    "ERROR",
                    "duplicate-batch-membership",
                    f"Task {task_id} appears in multiple batches: {', '.join(sorted(batches_for_task))}",
                )
            )

        self._check_cross_batch_dependencies(task_graph, batch_membership, batch_order, findings)

    def _check_batch_ordering(
        self,
        batch_id: str,
        task_list: list[str],
        serial_index: dict[str, int],
        findings: list[dict[str, str]],
    ) -> None:
        indexes = [serial_index.get(task_id, -1) for task_id in task_list]
        if indexes != sorted(indexes):
            findings.append(
                self._finding(
                    "ERROR",
                    "non-monotonic-batch-ordering",
                    f"Parallel batch {batch_id} tasks are not ordered by serial execution order",
                )
            )

    def _check_intra_batch_dependencies(
        self,
        batch: dict[str, Any],
        dependency_pairs: set[tuple[str, str]],
        findings: list[dict[str, str]],
    ) -> None:
        batch_id = batch.get("batch_id", "")
        mode = batch.get("mode", "")
        task_list = batch.get("tasks", [])
        if mode != "parallel":
            return
        for src in task_list:
            for dst in task_list:
                if src == dst:
                    continue
                if (src, dst) in dependency_pairs:
                    findings.append(
                        self._finding(
                            "ERROR",
                            "illegal-intra-batch-dependency",
                            f"Parallel batch {batch_id} contains dependency edge {src} -> {dst}",
                        )
                    )

    def _check_cross_batch_dependencies(
        self,
        task_graph: dict[str, Any],
        batch_membership: dict[str, list[str]],
        batch_order: dict[str, int],
        findings: list[dict[str, str]],
    ) -> None:
        for edge in task_graph.get("dependency_edges", []):
            src = edge.get("from", "")
            dst = edge.get("to", "")
            src_batches = batch_membership.get(src, [])
            dst_batches = batch_membership.get(dst, [])
            if not src_batches or not dst_batches:
                continue
            src_order = min(batch_order[batch_id] for batch_id in src_batches)
            dst_order = min(batch_order[batch_id] for batch_id in dst_batches)
            if src_order > dst_order:
                findings.append(
                    self._finding(
                        "ERROR",
                        "replay-unsafe-batch-dependency",
                        f"Dependency edge {src} -> {dst} crosses batches in reverse order",
                    )
                )

        for checkpoint in task_graph.get("integration_checkpoints", []):
            producer = checkpoint.get("produced_by", "")
            consumers = checkpoint.get("required_for", [])
            producer_batches = batch_membership.get(producer, [])
            if not producer_batches:
                continue
            producer_order = min(batch_order[batch_id] for batch_id in producer_batches)
            for consumer in consumers:
                consumer_batches = batch_membership.get(consumer, [])
                if not consumer_batches:
                    continue
                consumer_order = min(batch_order[batch_id] for batch_id in consumer_batches)
                if consumer_order < producer_order:
                    findings.append(
                        self._finding(
                            "ERROR",
                            "cross-batch-invalidation-leak",
                            f"Checkpoint consumer {consumer} is scheduled before producer {producer}",
                        )
                    )

    def _check_integration_checkpoints(
        self,
        task_graph: dict[str, Any],
        known_tasks: set[str],
        findings: list[dict[str, str]],
    ) -> None:
        for checkpoint in task_graph.get("integration_checkpoints", []):
            produced_by = checkpoint.get("produced_by", "")
            if produced_by and produced_by not in known_tasks:
                findings.append(
                    self._finding(
                        "ERROR",
                        "unknown-checkpoint-producer",
                        f"Checkpoint {checkpoint.get('checkpoint_id', '<unknown>')} references unknown producer {produced_by}",
                    )
                )
            for task_id in checkpoint.get("required_for", []):
                if task_id not in known_tasks:
                    findings.append(
                        self._finding(
                            "ERROR",
                            "unknown-checkpoint-consumer",
                            f"Checkpoint {checkpoint.get('checkpoint_id', '<unknown>')} references unknown consumer {task_id}",
                        )
                    )

    def _check_boundary_enforcement(
        self,
        task_graph: dict[str, Any],
        findings: list[dict[str, str]],
    ) -> None:
        boundary = task_graph.get("architecture_boundary_enforcement", {})
        allowed_roots = boundary.get("allowed_package_roots", [])
        hooks = boundary.get("enforcement_hooks", [])
        if not allowed_roots:
            findings.append(
                self._finding(
                    "ERROR",
                    "missing-allowed-package-roots",
                    "Architecture boundary enforcement must declare at least one allowed package root",
                )
            )
        if not hooks:
            findings.append(
                self._finding(
                    "WARNING",
                    "missing-enforcement-hooks",
                    "Architecture boundary enforcement should declare enforcement hooks",
                )
            )
        if any(root.startswith("org.eu.originalkeen.business.") for root in allowed_roots):
            forbidden_roots = set(boundary.get("forbidden_package_roots", []))
            for required_forbidden in ("org.eu.originalkeen.core", "org.eu.originalkeen.system"):
                if required_forbidden not in forbidden_roots:
                    findings.append(
                        self._finding(
                            "ERROR",
                            "incomplete-business-boundary-guard",
                            f"Business module boundaries must explicitly forbid {required_forbidden} package roots",
                        )
                    )

    def _check_dag_validity(self, task_graph: dict[str, Any], findings: list[dict[str, str]]) -> None:
        try:
            dag = DagEngine(task_graph)
            dag.validate_acyclic()
            dag.validate_serial_order()
        except ValueError as exc:
            findings.append(self._finding("ERROR", "dag-validation-failed", str(exc)))

    def _finding(self, severity: str, code: str, message: str) -> dict[str, str]:
        return {
            "severity": severity,
            "code": code,
            "message": message,
        }
