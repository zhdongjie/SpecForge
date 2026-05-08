from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


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
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
