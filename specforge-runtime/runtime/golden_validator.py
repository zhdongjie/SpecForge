from __future__ import annotations

from datetime import datetime
from pathlib import Path
import shutil
from typing import Any

import yaml

from .benchmark_runner import BenchmarkRunner
from .dag_engine import DagEngine
from .executor import RuntimeExecutor
from .golden_loader import GoldenLoader
from .loader import SpecLoader
from .replay_diff import ReplayDiffEngine
from .run_config import FailureInjection, RunConfig
from .semantic_equivalence import SemanticEquivalenceValidator
from .verifier import RuntimeVerifier


class GoldenValidator:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.specs_dir = root / "specs"
        self.runs_dir = root / "runs"
        self.golden_root = root / "runtime-golden"
        self.loader = GoldenLoader(self.golden_root)

    def run_regression_suite(self) -> dict[str, Any]:
        scenarios = self.loader.list_scenarios()
        results: list[dict[str, Any]] = []
        for scenario in scenarios:
            result = self._run_scenario(scenario)
            results.append(result)
        benchmark_summary = BenchmarkRunner(self.root).run()
        summary = {
            "recorded_at": self._now(),
            "scenario_count": len(results),
            "passed_count": sum(1 for result in results if result["passed"]),
            "failed_count": sum(1 for result in results if not result["passed"]),
            "benchmark_summary": benchmark_summary,
            "results": results,
        }
        output_path = self.root / "regression-summary.yaml"
        with output_path.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(summary, handle, sort_keys=False, allow_unicode=True)
        return summary

    def _run_scenario(self, scenario: dict[str, Any]) -> dict[str, Any]:
        manifest = scenario["manifest"]
        scenario_name = scenario["name"]
        scenario_dir = scenario["dir"]
        scenario_run_dir = self.runs_dir / f"golden-{scenario_name}"
        if scenario_run_dir.exists():
            shutil.rmtree(scenario_run_dir)

        loaded = SpecLoader(self.specs_dir).load_all()
        scenario_graph = self._load_optional_yaml(scenario_dir / "generation-task-graph.yaml")
        if scenario_graph:
            loaded["task_graph"] = scenario_graph
        run_id = scenario_run_dir.name
        execution_kind = manifest.get("execution_kind", "fresh")
        run_config = self._build_run_config(run_id, manifest, execution_kind)
        dag = DagEngine(loaded["task_graph"])
        dag.validate_acyclic()
        dag.validate_serial_order()
        executor = RuntimeExecutor(
            dag=dag,
            resolved_schema=loaded["resolved_schema"],
            task_graph=loaded["task_graph"],
            run_dir=scenario_run_dir,
            specs_dir=self.specs_dir,
            run_config=run_config,
        )
        verifier = RuntimeVerifier(self.specs_dir, scenario_run_dir)
        static_report = verifier.verify_static(loaded)
        if not static_report["passed"]:
            return {"scenario": scenario_name, "passed": False, "reason": "static-verification-failed"}

        execution_error: Exception | None = None
        try:
            executor.execute()
        except Exception as exc:
            execution_error = exc

        runtime_report = verifier.verify_runtime(
            loaded,
            replay_source_run_id=run_config.replay_source_run_id,
            affected_tasks=set(executor.affected_tasks) if run_config.mode == "partial-replay" else None,
        )
        bundle = self._collect_bundle(scenario_run_dir)
        golden_bundle = self.loader.load_golden_bundle(scenario_dir)
        bootstrap = not golden_bundle
        divergence_report = None
        semantic_report = {"passed": True, "difference_count": 0, "differences": []}
        if bootstrap:
            self._write_bundle(scenario_dir, bundle)
        else:
            semantic_report = SemanticEquivalenceValidator().compare(golden_bundle, scenario_run_dir)
            if not semantic_report["passed"]:
                divergence_report = ReplayDiffEngine().generate_report(golden_bundle, scenario_run_dir)

        expected_success = manifest.get("expected_success", True)
        actual_success = execution_error is None and runtime_report["passed"]
        passed = (actual_success == expected_success) and semantic_report["passed"]
        if bootstrap:
            passed = actual_success == expected_success
        return {
            "scenario": scenario_name,
            "bootstrap": bootstrap,
            "passed": passed,
            "expected_success": expected_success,
            "actual_success": actual_success,
            "semantic_equivalence": semantic_report,
            "runtime_report_passed": runtime_report["passed"],
            "execution_error": str(execution_error) if execution_error else None,
            "divergence_report": divergence_report,
        }

    def _build_run_config(self, run_id: str, manifest: dict[str, Any], execution_kind: str) -> RunConfig:
        injections = tuple(self._parse_injection(raw) for raw in manifest.get("inject_failure", []))
        partial_tasks = tuple(manifest.get("partial_replay_tasks", []))
        replay_source = manifest.get("replay_source_run_id")
        compare_trace = bool(replay_source)
        return RunConfig(
            run_id=run_id,
            replay_source_run_id=replay_source,
            partial_replay_tasks=partial_tasks,
            compare_trace=compare_trace,
            failure_injections=injections,
            max_workers=int(manifest.get("max_workers", 3)),
        )

    def _collect_bundle(self, run_dir: Path) -> dict[str, Any]:
        logs_dir = run_dir / "logs"
        bundle: dict[str, Any] = {}
        for filename in (
            "run-trace.yaml",
            "invalidation-report.yaml",
            "scheduler-trace.yaml",
            "replay-comparison.yaml",
            "verification-report.yaml",
            "logical-clock-summary.yaml",
            "lineage-report.yaml",
            "replay-divergence-report.yaml",
        ):
            path = logs_dir / filename
            if path.exists():
                bundle[filename] = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return bundle

    def _write_bundle(self, scenario_dir: Path, bundle: dict[str, Any]) -> None:
        scenario_dir.mkdir(parents=True, exist_ok=True)
        for filename, payload in bundle.items():
            with (scenario_dir / filename).open("w", encoding="utf-8") as handle:
                yaml.safe_dump(payload, handle, sort_keys=False, allow_unicode=True)

    def _parse_injection(self, raw: str) -> FailureInjection:
        parts = raw.split(":", 3)
        return FailureInjection(
            task_id=parts[0],
            failure_type=parts[1] if len(parts) > 1 and parts[1] else "validation",
            attempt=int(parts[2]) if len(parts) > 2 and parts[2] else 1,
            message=parts[3] if len(parts) > 3 and parts[3] else "Injected runtime failure",
        )

    def _load_optional_yaml(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    def _now(self) -> str:
        return datetime.now().astimezone().isoformat(timespec="seconds")
