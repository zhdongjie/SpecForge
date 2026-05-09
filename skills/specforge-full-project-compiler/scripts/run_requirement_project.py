from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the full SpecForge requirement-to-backend pipeline from one command."
    )
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--project-name", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--requirement", default="")
    parser.add_argument("--requirement-file", default="")
    parser.add_argument("--domain", default="auto")
    parser.add_argument("--build-plan", default="build-plan.yaml")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def run_step(command: list[str], cwd: Path, label: str) -> int:
    print(f"[STEP] {label}")
    completed = subprocess.run(command, cwd=cwd, check=False)
    if completed.returncode != 0:
        print(f"[FAIL] {label} (exit={completed.returncode})", file=sys.stderr)
        return completed.returncode
    print(f"[PASS] {label}")
    return 0


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    scripts_root = Path(__file__).resolve().parent

    readiness_command = [
        sys.executable,
        str(scripts_root / "check_specforge_workspace.py"),
        "--repo-root",
        str(repo_root),
    ]
    readiness_result = run_step(readiness_command, repo_root, "workspace-readiness")
    if readiness_result != 0:
        return readiness_result

    domain_key = infer_domain(args.project_name, args.requirement, args.requirement_file, args.domain, repo_root)
    print(f"[DOMAIN] {domain_key}")

    scaffold_command = [
        sys.executable,
        str(scripts_root / "scaffold_requirement_project.py"),
        "--repo-root",
        str(repo_root),
        "--project-name",
        args.project_name,
        "--domain",
        domain_key,
    ]
    if args.requirement:
        scaffold_command.extend(["--requirement", args.requirement])
    if args.requirement_file:
        scaffold_command.extend(["--requirement-file", args.requirement_file])
    if args.force:
        scaffold_command.append("--force")

    scaffold_result = run_step(scaffold_command, repo_root, "scaffold-specs")
    if scaffold_result != 0:
        return scaffold_result

    if args.force:
        reset_run_directory(repo_root, args.run_id)

    autobuild_command = [
        sys.executable,
        str(scripts_root / "run_specforge_autobuild.py"),
        "--repo-root",
        str(repo_root),
        "--run-id",
        args.run_id,
        "--build-plan",
        args.build_plan,
    ]
    autobuild_result = run_step(autobuild_command, repo_root, "auto-build")
    if autobuild_result != 0:
        return autobuild_result

    print("[DONE] requirement-to-backend pipeline completed")
    print(
        f"[FINAL_OUTPUT] {repo_root / 'specforge-runtime' / 'outputs'}",
    )
    return 0


def reset_run_directory(repo_root: Path, run_id: str) -> None:
    run_root = repo_root / "specforge-runtime" / "runs" / run_id
    if run_root.exists():
        shutil.rmtree(run_root)


def infer_domain(project_name: str, requirement_text: str, requirement_file: str, domain: str, repo_root: Path) -> str:
    if domain and domain != "auto":
        return domain

    text = requirement_text.strip()
    if requirement_file:
        requirement_path = Path(requirement_file)
        if not requirement_path.is_absolute():
            requirement_path = repo_root / requirement_path
        if requirement_path.exists():
            text = requirement_path.read_text(encoding="utf-8").strip() or text

    haystack = f"{project_name}\n{text}".lower()
    keyword_map = [
        ("laboratory-management", ["equipment", "consumable", "experiment", "schedule", "calendar", "report", "statistics", "lab manager", "lab management"]),
        ("insurance-management", ["insurance", "claim", "policy", "premium", "underwriting", "agent", "beneficiary", "renewal"]),
        ("laboratory-reservation", ["laboratory", "lab ", "reservation", "experiment", "equipment", "consumable", "schedule", "booking"]),
    ]
    for domain_key, keywords in keyword_map:
        if any(keyword in haystack for keyword in keywords):
            return domain_key

    return "laboratory-reservation"


if __name__ == "__main__":
    raise SystemExit(main())
