from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the canonical SpecForge auto-build pipeline.")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--build-plan", default="build-plan.yaml")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    runtime_root = repo_root / "specforge-runtime"
    main_py = runtime_root / "main.py"
    if not main_py.exists():
        print(f"[ERROR] Missing runtime entrypoint: {main_py}", file=sys.stderr)
        return 2

    command = [
        sys.executable,
        str(main_py),
        "--auto-build",
        "--build-plan",
        args.build_plan,
        "--run-id",
        args.run_id,
    ]
    completed = subprocess.run(command, cwd=runtime_root, check=False)
    if completed.returncode != 0:
        return completed.returncode

    build_plan_path = resolve_build_plan(repo_root, args.build_plan)
    build_plan = yaml.safe_load(build_plan_path.read_text(encoding="utf-8")) or {}
    final_output_dir = resolve_output_dir(runtime_root, build_plan, build_plan_path)
    validation_command = [
        sys.executable,
        str(Path(__file__).resolve().parent / "export_backend_api_smoke.py"),
        "--backend-root",
        str(final_output_dir),
        "--validate-business-contract",
    ]
    validation = subprocess.run(validation_command, cwd=repo_root, check=False)
    return validation.returncode


def resolve_build_plan(repo_root: Path, build_plan: str) -> Path:
    candidate = Path(build_plan)
    if candidate.is_absolute():
        return candidate
    if (repo_root / build_plan).exists():
        return (repo_root / build_plan).resolve()
    return (repo_root / "specforge-runtime" / "specs" / build_plan).resolve()


def resolve_output_dir(runtime_root: Path, build_plan: dict[str, object], build_plan_path: Path) -> Path:
    raw_output = str(build_plan.get("final_output_dir", f"outputs/{build_plan_path.stem}"))
    candidate = Path(raw_output)
    if candidate.is_absolute():
        return candidate
    return (runtime_root / candidate).resolve()


if __name__ == "__main__":
    raise SystemExit(main())
