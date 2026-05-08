from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check whether a repository is ready for SpecForge full-project compilation.")
    parser.add_argument("--repo-root", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    runtime_root = repo_root / "specforge-runtime"
    backend_root = repo_root / "backend"

    checks = {
        "repo_root": str(repo_root),
        "runtime_exists": runtime_root.exists(),
        "runtime_main_exists": (runtime_root / "main.py").exists(),
        "runtime_specs_exists": (runtime_root / "specs").exists(),
        "runtime_runtime_exists": (runtime_root / "runtime").exists(),
        "backend_exists": backend_root.exists(),
        "build_plan_exists": (runtime_root / "specs" / "build-plan.yaml").exists(),
        "project_assembly_plan_exists": (runtime_root / "specs" / "project-assembly-plan.yaml").exists(),
    }
    checks["ready"] = all(
        checks[key]
        for key in (
            "runtime_exists",
            "runtime_main_exists",
            "runtime_specs_exists",
            "runtime_runtime_exists",
            "build_plan_exists",
            "project_assembly_plan_exists",
        )
    )
    sys.stdout.write(json.dumps(checks, indent=2))
    sys.stdout.write("\n")
    return 0 if checks["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
