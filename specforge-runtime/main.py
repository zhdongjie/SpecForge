from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from runtime.run_config import RunConfig


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


def export_final_backend(source_root: Path, destination_root: Path) -> None:
    if destination_root.exists():
        shutil.rmtree(destination_root)
    destination_root.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        source_root,
        destination_root,
        ignore=shutil.ignore_patterns(".m2", "target", "__pycache__"),
    )


def run_auto_build(args: argparse.Namespace, root: Path) -> None:
    from runtime.codegen.common import dump_yaml, safe_load_yaml
    from runtime.hardening import HardeningPipeline

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
    """Compatibility forwarding for callers importing the historical helper."""
    from legacy_commands.simulation import build_run_config as build

    return build(args)


def run_simulation(args: argparse.Namespace, root: Path) -> None:
    """Compatibility forwarding for the historical default command."""
    from legacy_commands.simulation import run_simulation as run

    run(args, root)


def main() -> None:
    args = parse_args()
    root = Path(__file__).resolve().parent
    if args.auto_build:
        run_auto_build(args, root)
        return

    from legacy_commands import dispatch

    if not dispatch(args, root):
        run_simulation(args, root)


if __name__ == "__main__":
    main()
