from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from runtime.benchmark_runner import BenchmarkRunner
from runtime.dag_engine import DagEngine
from runtime.executor import RuntimeExecutor
from runtime.golden_validator import GoldenValidator
from runtime.graph_validator import GraphValidator
from runtime.loader import SpecLoader
from runtime.replay import compare_traces, load_run_trace, load_yaml
from runtime.run_config import FailureInjection, RunConfig
from runtime.verifier import RuntimeVerifier


ROOT = Path(__file__).resolve().parents[1]
SPECS_DIR = ROOT / "specs"
SCENARIOS_DIR = ROOT / "runtime-scenarios"


def load_default_specs() -> dict[str, dict]:
    return SpecLoader(SPECS_DIR).load_all()


def load_scenario(name: str) -> dict:
    return load_yaml(SCENARIOS_DIR / name / "scenario.yaml")


def load_scenario_graph(name: str) -> dict:
    return load_yaml(SCENARIOS_DIR / name / "generation-task-graph.yaml")


class RuntimeVerificationTests(unittest.TestCase):
    def test_cycle_detection_static_verifier(self) -> None:
        scenario = load_scenario("cycle-detection")
        graph = load_scenario_graph("cycle-detection")
        report = GraphValidator().validate(graph)
        self.assertEqual(report["passed"], scenario["expected"]["passed"])
        self.assertIn(
            scenario["expected"]["finding_code"],
            [finding["code"] for finding in report["findings"]],
        )

    def test_parallel_failure_runtime_semantics(self) -> None:
        scenario = load_scenario("parallel-failure")
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = self._run_default_runtime(
                Path(temp_dir),
                "parallel-failure-run",
                failure_specs=scenario["inject_failure"],
                expect_error=True,
            )
            summary = load_yaml(run_dir / "logs" / "run-summary.yaml")
            self.assertEqual(summary["execution_summary"]["failed_tasks"], scenario["expected"]["failed_tasks"])
            self.assertEqual(
                summary["execution_summary"]["invalidated_tasks"],
                scenario["expected"]["invalidated_tasks"],
            )
            verification = load_yaml(run_dir / "logs" / "verification-report.yaml")
            self.assertTrue(verification["passed"])

    def test_artifact_conflict_runtime_semantics(self) -> None:
        scenario = load_scenario("artifact-conflict")
        graph = load_scenario_graph("artifact-conflict")
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = self._run_runtime_with_graph(
                Path(temp_dir),
                "artifact-conflict-run",
                graph,
                expect_error=True,
            )
            summary = load_yaml(run_dir / "logs" / "run-summary.yaml")
            conflicts = summary["artifact_summary"]["concurrency_conflicts"]
            self.assertTrue(conflicts)
            self.assertEqual(conflicts[0]["conflict_type"], scenario["expected"]["conflict_code"])
            verification = load_yaml(run_dir / "logs" / "verification-report.yaml")
            self.assertTrue(verification["passed"])

    def test_rollback_chain_invalidation_cleanup(self) -> None:
        scenario = load_scenario("rollback-chain")
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = self._run_default_runtime(
                Path(temp_dir),
                "rollback-chain-run",
                failure_specs=scenario["inject_failure"],
                expect_error=True,
            )
            invalidation_report = load_yaml(run_dir / "logs" / "invalidation-report.yaml")
            reasons = {event.get("reason") for event in invalidation_report.get("events", [])}
            self.assertIn(scenario["expected"]["invalidation_reason"], reasons)
            verification = load_yaml(run_dir / "logs" / "verification-report.yaml")
            self.assertTrue(verification["passed"])

    def test_replay_divergence_is_detected(self) -> None:
        scenario = load_scenario("replay-divergence")
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            baseline_run = self._run_default_runtime(temp_root, "replay-base")
            current_run = self._run_default_runtime(temp_root, "replay-current")
            current_trace_path = current_run / "logs" / "run-trace.yaml"
            current_trace = load_yaml(current_trace_path)
            current_trace["executed_tasks"] = list(reversed(current_trace["executed_tasks"]))
            self._write_yaml(current_trace_path, current_trace)

            loaded = load_default_specs()
            verifier = RuntimeVerifier(SPECS_DIR, current_run)
            report = verifier.verify_runtime(
                loaded,
                replay_source_run_id=baseline_run.name,
            )
            self.assertEqual(report["passed"], scenario["expected"]["passed"])
            replay_codes = [finding["code"] for finding in report["replay_validation"]["findings"]]
            self.assertIn(scenario["expected"]["finding_code"], replay_codes)

    def test_parallel_scheduler_stress_replays_are_deterministic(self) -> None:
        scenario = load_scenario("scheduler-race")
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            run_dirs: list[Path] = []
            for index in range(scenario["iterations"]):
                run_dir = self._run_default_runtime(
                    temp_root,
                    f"scheduler-race-{index}",
                    max_workers=scenario["max_workers"][index % len(scenario["max_workers"])],
                )
                run_dirs.append(run_dir)

            baseline_trace = load_run_trace(run_dirs[0])
            for run_dir in run_dirs[1:]:
                current_trace = load_run_trace(run_dir)
                comparison = compare_traces(baseline_trace, current_trace)
                self.assertEqual(comparison["match"], scenario["expected"]["all_match"])

    def test_logical_clock_drift_is_detected(self) -> None:
        scenario = load_scenario("logical-clock-drift")
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = self._run_default_runtime(Path(temp_dir), "logical-clock-run")
            trace_path = run_dir / "logs" / "run-trace.yaml"
            scheduler_path = run_dir / "logs" / "scheduler-trace.yaml"
            run_trace = load_yaml(trace_path)
            scheduler_trace = load_yaml(scheduler_path)
            run_trace["scheduler_events"][1]["execution_tick"] = 999
            scheduler_trace["events"][1]["execution_tick"] = 999
            self._write_yaml(trace_path, run_trace)
            self._write_yaml(scheduler_path, scheduler_trace)

            loaded = load_default_specs()
            verifier = RuntimeVerifier(SPECS_DIR, run_dir)
            report = verifier.verify_runtime(loaded)
            self.assertEqual(report["passed"], scenario["expected"]["passed"])
            semantic_codes = [finding["code"] for finding in report["semantic_validation"]["findings"]]
            self.assertIn(scenario["expected"]["finding_code"], semantic_codes)

    def test_runtime_verifier_emits_extended_reports(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = self._run_default_runtime(Path(temp_dir), "extended-report-run")
            verification = load_yaml(run_dir / "logs" / "verification-report.yaml")
            logical_clock = load_yaml(run_dir / "logs" / "logical-clock-summary.yaml")
            lineage = load_yaml(run_dir / "logs" / "lineage-report.yaml")

            self.assertIn("checkpoint_validation", verification)
            self.assertIn("semantic_equivalence_status", verification)
            self.assertIn("scheduler_determinism_score", verification)
            self.assertTrue(logical_clock.get("monotonic"))
            self.assertIn("artifact_lineage", lineage)

    def test_regression_suite_bootstraps_and_replays(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            self._copy_runtime_fixture(temp_root)

            validator = GoldenValidator(temp_root)
            first = validator.run_regression_suite()
            second = validator.run_regression_suite()

            self.assertEqual(first["failed_count"], 0)
            self.assertEqual(second["failed_count"], 0)
            self.assertTrue(any(result["bootstrap"] for result in first["results"]))
            self.assertTrue(all(not result["bootstrap"] for result in second["results"]))

    def test_benchmark_runner_emits_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            self._copy_runtime_fixture(temp_root)
            self._run_default_runtime(temp_root, "benchmark-a", max_workers=2)
            self._run_default_runtime(temp_root, "benchmark-b", max_workers=3)

            summary = BenchmarkRunner(temp_root).run()
            written = load_yaml(temp_root / "benchmark-summary.yaml")

            self.assertEqual(summary["sample_count"], 2)
            self.assertEqual(written["sample_count"], 2)
            self.assertIn("scheduler_stability", summary)

    def _run_default_runtime(
        self,
        temp_root: Path,
        run_id: str,
        failure_specs: list[str] | None = None,
        expect_error: bool = False,
        max_workers: int = 3,
    ) -> Path:
        loaded = load_default_specs()
        return self._execute_runtime(
            temp_root=temp_root,
            run_id=run_id,
            loaded=loaded,
            failure_specs=failure_specs or [],
            expect_error=expect_error,
            max_workers=max_workers,
        )

    def _run_runtime_with_graph(
        self,
        temp_root: Path,
        run_id: str,
        task_graph: dict,
        expect_error: bool = False,
    ) -> Path:
        loaded = load_default_specs()
        loaded = {
            "module_spec": loaded["module_spec"],
            "resolved_schema": loaded["resolved_schema"],
            "task_graph": task_graph,
        }
        return self._execute_runtime(
            temp_root=temp_root,
            run_id=run_id,
            loaded=loaded,
            failure_specs=[],
            expect_error=expect_error,
            max_workers=2,
        )

    def _execute_runtime(
        self,
        temp_root: Path,
        run_id: str,
        loaded: dict[str, dict],
        failure_specs: list[str],
        expect_error: bool,
        max_workers: int,
    ) -> Path:
        run_dir = temp_root / "runs" / run_id
        dag = DagEngine(loaded["task_graph"])
        dag.validate_acyclic()
        dag.validate_serial_order()

        config = RunConfig(
            run_id=run_id,
            max_workers=max_workers,
            failure_injections=tuple(self._parse_injection(spec) for spec in failure_specs),
        )
        executor = RuntimeExecutor(
            dag=dag,
            resolved_schema=loaded["resolved_schema"],
            task_graph=loaded["task_graph"],
            run_dir=run_dir,
            specs_dir=SPECS_DIR,
            run_config=config,
        )
        verifier = RuntimeVerifier(SPECS_DIR, run_dir)
        static_report = verifier.verify_static(loaded)
        self.assertTrue(static_report["passed"])

        error = None
        try:
            executor.execute()
        except Exception as exc:  # pragma: no cover - exercised intentionally in failure scenarios
            error = exc

        verifier.verify_runtime(loaded, replay_source_run_id=config.replay_source_run_id)
        if expect_error:
            self.assertIsNotNone(error)
        else:
            self.assertIsNone(error)
        return run_dir

    def _parse_injection(self, raw: str) -> FailureInjection:
        parts = raw.split(":", 3)
        return FailureInjection(
            task_id=parts[0],
            failure_type=parts[1] if len(parts) > 1 else "validation",
            attempt=int(parts[2]) if len(parts) > 2 else 1,
            message=parts[3] if len(parts) > 3 else "Injected runtime failure",
        )

    def _write_yaml(self, path: Path, payload: dict) -> None:
        import yaml

        with path.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(payload, handle, sort_keys=False, allow_unicode=True)

    def _copy_runtime_fixture(self, destination_root: Path) -> None:
        import shutil

        shutil.copytree(SPECS_DIR, destination_root / "specs")
        shutil.copytree(ROOT / "runtime-golden", destination_root / "runtime-golden")
        (destination_root / "runs").mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    unittest.main()
