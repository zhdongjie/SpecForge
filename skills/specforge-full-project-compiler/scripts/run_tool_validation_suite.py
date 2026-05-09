from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the portable SpecForge tool validation scenarios."
    )
    parser.add_argument("--repo-root", required=True)
    parser.add_argument(
        "--scenario",
        choices=["all", "lab-inline-auto", "lab-platform-file-auto", "insurance-inline-auto", "insurance-file-auto"],
        default="all",
    )
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def build_scenarios(repo_root: Path) -> list[dict[str, object]]:
    script_root = Path(__file__).resolve().parent
    wrapper = script_root / "run_requirement_project.py"
    return [
        {
            "name": "lab-inline-auto",
            "command": [
                sys.executable,
                str(wrapper),
                "--repo-root",
                str(repo_root),
                "--project-name",
                "Laboratory Management Platform",
                "--requirement",
                "Build a complete modular-monolith Spring Boot laboratory management backend covering laboratory resources, experiment projects, equipment, consumables, reservations, approvals, access control, notifications, schedule calendar, and statistics reporting.",
                "--run-id",
                "validation-lab-inline-auto-001",
            ],
        },
        {
            "name": "lab-platform-file-auto",
            "command": [
                sys.executable,
                str(wrapper),
                "--repo-root",
                str(repo_root),
                "--project-name",
                "Laboratory Management Platform",
                "--requirement-file",
                "sandbox/laboratory-management-requirement.txt",
                "--run-id",
                "validation-lab-platform-file-auto-001",
            ],
        },
        {
            "name": "insurance-inline-auto",
            "command": [
                sys.executable,
                str(wrapper),
                "--repo-root",
                str(repo_root),
                "--project-name",
                "Insurance Operations Platform",
                "--requirement",
                "Build a complete modular-monolith Spring Boot insurance operations backend covering insured customer management, claim management, premium payments, policy renewals, underwriting approvals, and channel agent management.",
                "--run-id",
                "validation-insurance-inline-auto-001",
            ],
        },
        {
            "name": "insurance-file-auto",
            "command": [
                sys.executable,
                str(wrapper),
                "--repo-root",
                str(repo_root),
                "--project-name",
                "Insurance Operations Platform",
                "--requirement-file",
                "sandbox/insurance-operations-requirement.txt",
                "--run-id",
                "validation-insurance-file-auto-001",
            ],
        },
    ]


def run_scenario(command: list[str], cwd: Path, name: str, force: bool) -> int:
    effective_command = list(command)
    if force:
        effective_command.append("--force")
    print(f"[SCENARIO] {name}")
    completed = subprocess.run(effective_command, cwd=cwd, check=False)
    if completed.returncode != 0:
        print(f"[FAIL] {name} (exit={completed.returncode})", file=sys.stderr)
        return completed.returncode
    print(f"[PASS] {name}")
    return 0


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    scenarios = build_scenarios(repo_root)

    selected = scenarios
    if args.scenario != "all":
        selected = [item for item in scenarios if item["name"] == args.scenario]

    for scenario in selected:
        exit_code = run_scenario(
            scenario["command"],  # type: ignore[arg-type]
            repo_root,
            str(scenario["name"]),
            args.force,
        )
        if exit_code != 0:
            return exit_code

    print("[DONE] validation suite completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
