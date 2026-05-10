from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from runtime.codegen.common import dump_yaml, safe_load_yaml
from runtime.codegen import CodegenPipeline
from runtime.dag_engine import DagEngine
from runtime.hardening import HardeningPipeline
from runtime.executor import RuntimeExecutor
from runtime.golden_validator import GoldenValidator
from runtime.ir_lowering import IRLoweringPipeline
from runtime.loader import SpecLoader
from runtime.mutation import MutationEngine
from runtime.platform_compiler import ProjectCompiler
from runtime.run_config import FailureInjection, RunConfig
from runtime.synthesis import SynthesisPipeline
from runtime.verifier import RuntimeVerifier


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SpecForge compiler runtime simulator")
    parser.add_argument("--run-id", default="run-001")
    parser.add_argument("--auto-build", action="store_true")
    parser.add_argument("--build-plan", default="build-plan.yaml")
    parser.add_argument("--project-assembly-plan", default="")
    parser.add_argument("--replay-source-run")
    parser.add_argument("--partial-replay", default="")
    parser.add_argument("--inject-failure", action="append", default=[])
    parser.add_argument("--no-compare-trace", action="store_true")
    parser.add_argument("--max-workers", type=int, default=4)
    parser.add_argument("--run-regression-suite", action="store_true")
    parser.add_argument("--emit-code", action="store_true")
    parser.add_argument("--mutate-module", action="store_true")
    parser.add_argument("--backend-root", default="../backend")
    parser.add_argument("--verify-compile", action="store_true")
    parser.add_argument("--mutation-spec", default="mutation-spec.yaml")
    parser.add_argument("--synthesize-module", action="store_true")
    parser.add_argument("--field-schema", default="field-schema.resolved.yaml")
    parser.add_argument("--lower-ir", action="store_true")
    parser.add_argument("--module-schema", default="module-schema.resolved.yaml")
    parser.add_argument("--compile-backend", action="store_true")
    parser.add_argument("--skip-boot-verify", action="store_true")
    parser.add_argument("--harden-backend", action="store_true")
    parser.add_argument("--auto-repair", action="store_true")
    parser.add_argument("--verify-boot", action="store_true")
    parser.add_argument("--repair-max-passes", type=int, default=5)
    return parser.parse_args()


def resolve_build_plan_path(root: Path, build_plan: str) -> Path:
    candidate = Path(build_plan)
    if candidate.is_absolute():
        return candidate
    root_relative = root / candidate
    if root_relative.exists():
        return root_relative
    return root / "specs" / candidate


def resolve_output_path(root: Path, raw_path: str | None, fallback: str) -> Path:
    candidate = Path(raw_path) if raw_path else Path(fallback)
    return candidate if candidate.is_absolute() else (root / candidate)


def _is_transient_log_path(path: Path) -> bool:
    return path.suffix.lower() == ".log" and "logs" in path.parts


def _clear_output_directory(path: Path) -> list[str]:
    preserved: list[str] = []
    if not path.exists():
        return preserved
    for child in sorted(path.iterdir(), key=lambda item: (item.is_file(), str(item)), reverse=True):
        _remove_output_path(child, preserved)
    return preserved


def _remove_output_path(path: Path, preserved: list[str]) -> None:
    if not path.exists():
        return
    if path.is_dir():
        for child in sorted(path.iterdir(), key=lambda item: (item.is_file(), str(item)), reverse=True):
            _remove_output_path(child, preserved)
        try:
            path.rmdir()
        except FileNotFoundError:
            return
        except OSError:
            try:
                remaining = list(path.iterdir())
            except FileNotFoundError:
                return
            if remaining:
                if all(_is_transient_log_path(item) for item in remaining if item.is_file()):
                    return
            raise
        return

    try:
        path.unlink()
    except PermissionError:
        if _is_transient_log_path(path):
            preserved.append(str(path))
            return
        raise


def export_final_backend(source_root: Path, destination_root: Path) -> None:
    preserved_paths = _clear_output_directory(destination_root)
    destination_root.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        source_root,
        destination_root,
        ignore=shutil.ignore_patterns(".m2", "target", "__pycache__", "*.log"),
        dirs_exist_ok=True,
    )
    if preserved_paths:
        dump_yaml(
            destination_root / "logs" / "output-export-report.yaml",
            {
                "status": "PASS",
                "preserved_transient_paths": preserved_paths,
                "notes": [
                    "Transient locked log files from a previous output were preserved during export.",
                    "Source artifacts were recopied with deterministic overwrite semantics except *.log files.",
                ],
            },
        )


def run_auto_build(args: argparse.Namespace, root: Path) -> None:
    build_plan_path = resolve_build_plan_path(root, args.build_plan)
    build_plan = safe_load_yaml(build_plan_path)

    plan_id = build_plan.get("plan_id", build_plan_path.stem)
    module_schema_name = build_plan.get("module_schema", args.module_schema)
    module_spec_name = build_plan.get("module_spec", "module-spec.yaml")
    project_assembly_plan_name = build_plan.get("project_assembly_plan", args.project_assembly_plan)
    backend_root_arg = build_plan.get("backend_root", args.backend_root)
    auto_repair = bool(build_plan.get("auto_repair", True))
    verify_boot = bool(build_plan.get("verify_boot", True))
    repair_max_passes = int(build_plan.get("repair_max_passes", args.repair_max_passes))
    final_output_dir = resolve_output_path(
        root,
        build_plan.get("final_output_dir"),
        f"outputs/{plan_id}",
    )
    run_id = (
        str(build_plan.get("default_run_id", plan_id))
        if args.run_id == "run-001"
        else args.run_id
    )

    run_root = root / "runs" / run_id
    specs_dir = root / "specs"
    backend_root = (root / str(backend_root_arg)).resolve()

    summary = HardeningPipeline(
        project_root=root.parent,
        backend_root=backend_root,
        run_root=run_root,
        specs_dir=specs_dir,
    ).run(
        module_schema_name=str(module_schema_name),
        module_spec_name=str(module_spec_name),
        project_assembly_plan_name=str(project_assembly_plan_name) if project_assembly_plan_name else None,
        auto_repair=auto_repair,
        verify_boot=verify_boot,
        repair_max_passes=max(1, repair_max_passes),
    )

    generated_project_root = Path(summary["generated_project_root"])
    export_final_backend(generated_project_root, final_output_dir)

    auto_build_report = {
        "status": summary["status"],
        "plan_id": plan_id,
        "build_plan": str(build_plan_path),
        "run_id": run_id,
        "module_schema": str(module_schema_name),
        "module_spec": str(module_spec_name),
        "project_assembly_plan": str(project_assembly_plan_name) if project_assembly_plan_name else None,
        "backend_root": str(backend_root),
        "auto_repair": auto_repair,
        "verify_boot": verify_boot,
        "repair_max_passes": repair_max_passes,
        "generated_project_root": str(generated_project_root),
        "final_output_dir": str(final_output_dir),
        "compile_status": summary.get("compile_status"),
        "boot_status": summary.get("boot_status"),
    }
    dump_yaml(run_root / "logs" / "auto-build-report.yaml", auto_build_report)
    dump_yaml(final_output_dir / "logs" / "final-output-report.yaml", auto_build_report)
    if summary["status"] == "FAIL":
        raise RuntimeError("Auto build failed verification")


def build_run_config(args: argparse.Namespace) -> RunConfig:
    partial_replay_tasks = tuple(
        task_id.strip() for task_id in args.partial_replay.split(",") if task_id.strip()
    )
    injections: list[FailureInjection] = []
    for raw in args.inject_failure:
        parts = raw.split(":", 3)
        task_id = parts[0]
        failure_type = parts[1] if len(parts) > 1 and parts[1] else "validation"
        attempt = int(parts[2]) if len(parts) > 2 and parts[2] else 1
        message = parts[3] if len(parts) > 3 and parts[3] else "Injected runtime failure"
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


def main() -> None:
    args = parse_args()
    root = Path(__file__).resolve().parent
    if args.auto_build:
        run_auto_build(args, root)
        return
    if args.emit_code:
        output_root = root / "runs" / args.run_id / "generated-module"
        specs_dir = root / "specs"
        backend_root = (root / args.backend_root).resolve()
        summary = CodegenPipeline(
            project_root=root.parent,
            backend_root=backend_root,
            output_root=output_root,
            specs_dir=specs_dir,
        ).run(verify_compile=args.verify_compile)
        if summary["status"] != "PASS":
            raise RuntimeError("Code generation failed verification")
        return
    if args.mutate_module:
        output_root = root / "runs" / args.run_id / "mutated-module"
        specs_dir = root / "specs"
        backend_root = (root / args.backend_root).resolve()
        mutation_spec_path = specs_dir / args.mutation_spec
        summary = MutationEngine(
            project_root=root.parent,
            backend_root=backend_root,
            output_root=output_root,
            specs_dir=specs_dir,
            mutation_spec_path=mutation_spec_path,
        ).run(verify_compile=args.verify_compile)
        if summary["status"] != "PASS":
            raise RuntimeError("Module mutation failed verification")
        return
    if args.synthesize_module:
        output_root = root / "runs" / args.run_id / "generated-module"
        specs_dir = root / "specs"
        backend_root = (root / args.backend_root).resolve()
        summary = SynthesisPipeline(
            project_root=root.parent,
            backend_root=backend_root,
            output_root=output_root,
            specs_dir=specs_dir,
        ).run(verify_compile=args.verify_compile, field_schema_name=args.field_schema)
        if summary["status"] != "PASS":
            raise RuntimeError("Field-level synthesis failed verification")
        return
    if args.lower_ir:
        output_root = root / "runs" / args.run_id
        specs_dir = root / "specs"
        summary = IRLoweringPipeline(
            output_root=output_root,
            specs_dir=specs_dir,
        ).run(module_schema_name=args.module_schema)
        if summary["status"] != "PASS":
            raise RuntimeError("IR lowering failed verification")
        return
    if args.compile_backend:
        output_root = root / "runs" / args.run_id
        specs_dir = root / "specs"
        backend_root = (root / args.backend_root).resolve()
        summary = ProjectCompiler(
            project_root=root.parent,
            backend_root=backend_root,
            run_root=output_root,
            specs_dir=specs_dir,
        ).run(
            module_schema_name=args.module_schema,
            module_spec_name="module-spec.yaml",
            project_assembly_plan_name=args.project_assembly_plan or None,
            run_compile=True,
            run_boot=not args.skip_boot_verify,
        )
        if summary["status"] == "FAIL":
            raise RuntimeError("Backend compilation failed verification")
        return
    if args.harden_backend:
        output_root = root / "runs" / args.run_id
        specs_dir = root / "specs"
        backend_root = (root / args.backend_root).resolve()
        summary = HardeningPipeline(
            project_root=root.parent,
            backend_root=backend_root,
            run_root=output_root,
            specs_dir=specs_dir,
        ).run(
            module_schema_name=args.module_schema,
            module_spec_name="module-spec.yaml",
            project_assembly_plan_name=args.project_assembly_plan or None,
            auto_repair=args.auto_repair,
            verify_boot=args.verify_boot,
            repair_max_passes=max(1, args.repair_max_passes),
        )
        if summary["status"] == "FAIL":
            raise RuntimeError("Backend hardening failed verification")
        return

    if args.run_regression_suite:
        summary = GoldenValidator(root).run_regression_suite()
        if summary["failed_count"] > 0:
            raise RuntimeError("Regression suite failed")
        return

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
        affected_tasks=set(executor.affected_tasks) if run_config.mode == "partial-replay" else None,
    )

    if execution_error is not None:
        raise execution_error
    if not runtime_report["passed"]:
        raise RuntimeError("Runtime verification failed")


if __name__ == "__main__":
    main()
