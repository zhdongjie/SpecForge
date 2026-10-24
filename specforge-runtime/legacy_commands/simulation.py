"""Historical DAG, replay and failure-injection execution."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from runtime.run_config import RunConfig


def build_run_config(args: argparse.Namespace) -> RunConfig:
    from runtime.run_config import FailureInjection, RunConfig

    partial_replay_tasks = tuple(
        task_id.strip() for task_id in args.partial_replay.split(",") if task_id.strip()
    )
    injections: list[FailureInjection] = []
    for raw in args.inject_failure:
        parts = raw.split(":", 3)
        task_id = parts[0]
        failure_type = parts[1] if len(parts) > 1 and parts[1] else "validation"
        attempt = int(parts[2]) if len(parts) > 2 and parts[2] else 1
        message = (
            parts[3] if len(parts) > 3 and parts[3] else "Injected runtime failure"
        )
        injections.append(
            FailureInjection(
                task_id=task_id,
                failure_type=failure_type,
                attempt=attempt,
                message=message,
            )
        )
    return RunConfig(
        run_id=args.run_id,
        replay_source_run_id=args.replay_source_run,
        partial_replay_tasks=partial_replay_tasks,
        compare_trace=bool(args.replay_source_run and not args.no_compare_trace),
        failure_injections=tuple(injections),
        max_workers=max(1, args.max_workers),
    )


def run_simulation(args: argparse.Namespace, root: Path) -> None:
    """Retain the historical default simulation without loading it for builds."""
    from runtime.dag_engine import DagEngine
    from runtime.executor import RuntimeExecutor
    from runtime.loader import SpecLoader
    from runtime.verifier import RuntimeVerifier

    specs_dir = root / "specs"
    run_config = build_run_config(args)
    run_dir = root / "runs" / run_config.run_id

    loader = SpecLoader(specs_dir)
    loaded = loader.load_all()

    dag = DagEngine(loaded["task_graph"])
    dag.validate_acyclic()
    dag.validate_serial_order()

    executor = RuntimeExecutor(
        dag=dag,
        resolved_schema=loaded["resolved_schema"],
        task_graph=loaded["task_graph"],
        run_dir=run_dir,
        specs_dir=specs_dir,
        run_config=run_config,
    )
    verifier = RuntimeVerifier(specs_dir=specs_dir, run_dir=run_dir)
    static_report = verifier.verify_static(loaded)
    if not static_report["passed"]:
        raise RuntimeError("Static task graph verification failed")
    execution_error: Exception | None = None
    try:
        executor.execute()
    except Exception as exc:
        execution_error = exc

    runtime_report = verifier.verify_runtime(
        loaded,
        replay_source_run_id=run_config.replay_source_run_id,
        affected_tasks=(
            set(executor.affected_tasks)
            if run_config.mode == "partial-replay"
            else None
        ),
    )

    if execution_error is not None:
        raise execution_error
    if not runtime_report["passed"]:
        raise RuntimeError("Runtime verification failed")
