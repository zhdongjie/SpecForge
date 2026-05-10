from __future__ import annotations

import argparse
import json
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
        choices=[
            "all",
            "lab-inline-auto",
            "lab-platform-file-auto",
            "insurance-inline-auto",
            "insurance-file-auto",
            "library-inline-auto",
            "course-inline-auto",
            "dormitory-inline-auto",
        ],
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
                "Build a complete modular-monolith Spring Boot insurance operations backend covering product center, customer center, policy center, claim center, premium payment center, renewal center, underwriting center, channel agent center, notification center, and statistics reporting center.",
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
        {
            "name": "library-inline-auto",
            "command": [
                sys.executable,
                str(wrapper),
                "--repo-root",
                str(repo_root),
                "--project-name",
                "Library Management Platform",
                "--requirement",
                "Build a complete modular-monolith Spring Boot library management backend covering book catalog center, reader membership center, circulation borrowing center, return inspection center, reservation queue center, acquisition supplier center, shelf inventory center, notification center, and statistics reporting center.",
                "--run-id",
                "validation-library-inline-auto-001",
            ],
        },
        {
            "name": "course-inline-auto",
            "command": [
                sys.executable,
                str(wrapper),
                "--repo-root",
                str(repo_root),
                "--project-name",
                "Course Management Platform",
                "--requirement",
                "Build a complete modular-monolith Spring Boot course management backend covering course catalog center, teaching class center, enrollment selection center, timetable scheduling center, exam assessment center, teaching resource center, notification center, and statistics reporting center.",
                "--run-id",
                "validation-course-inline-auto-001",
            ],
        },
        {
            "name": "dormitory-inline-auto",
            "command": [
                sys.executable,
                str(wrapper),
                "--repo-root",
                str(repo_root),
                "--project-name",
                "Dormitory Management Platform",
                "--requirement",
                "Build a complete modular-monolith Spring Boot dormitory management backend covering dormitory building center, room bed allocation center, move-in move-out center, repair maintenance center, visitor access center, fee billing center, hygiene inspection center, notification center, and statistics reporting center.",
                "--run-id",
                "validation-dormitory-inline-auto-001",
            ],
        },
    ]


def summarize_run(repo_root: Path, run_id: str) -> dict[str, object]:
    script_root = Path(__file__).resolve().parent
    summary_script = script_root / "summarize_specforge_outcome.py"
    completed = subprocess.run(
        [
            sys.executable,
            str(summary_script),
            "--repo-root",
            str(repo_root),
            "--run-id",
            run_id,
        ],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"summary failed for run_id={run_id}: exit={completed.returncode}\n{completed.stdout}\n{completed.stderr}"
        )
    return json.loads(completed.stdout)


def run_scenario(command: list[str], cwd: Path, name: str, force: bool) -> int:
    effective_command = list(command)
    if force:
        effective_command.append("--force")
    print(f"[SCENARIO] {name}")
    completed = subprocess.run(effective_command, cwd=cwd, check=False)
    if completed.returncode != 0:
        print(f"[FAIL] {name} (exit={completed.returncode})", file=sys.stderr)
        return completed.returncode
    run_id = effective_command[effective_command.index("--run-id") + 1]
    summary = summarize_run(cwd, run_id)
    if summary.get("status") != "PASS":
        print(
            f"[FAIL] {name} summary status={summary.get('status')} run_id={run_id}",
            file=sys.stderr,
        )
        return 1
    print(
        f"[SUMMARY] {name} compile={summary.get('compile_status')} boot={summary.get('boot_status')} "
        f"business={summary.get('business_contract_status')} delivery={summary.get('delivery_validation_status')} "
        f"sql={summary.get('sql_asset_status')} auth={summary.get('auth_surface_status')}"
    )
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
