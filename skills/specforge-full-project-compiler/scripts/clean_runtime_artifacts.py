from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Remove SpecForge runtime artifacts in one step."
    )
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--include-root-logs",
        action="store_true",
        help="Also remove the repository root logs/ directory.",
    )
    return parser.parse_args()


def build_targets(repo_root: Path, include_root_logs: bool) -> list[Path]:
    targets = [
        repo_root / "specforge-runtime" / "runs",
        repo_root / "specforge-runtime" / "outputs",
        repo_root / "sandbox",
    ]
    if include_root_logs:
        targets.append(repo_root / "logs")
    return targets


def remove_target(path: Path, repo_root: Path, dry_run: bool) -> dict[str, object]:
    entry: dict[str, object] = {
        "path": str(path),
        "exists": path.exists(),
        "status": "SKIPPED",
    }
    if not path.exists():
        entry["reason"] = "missing"
        return entry

    try:
        resolved = path.resolve()
        resolved.relative_to(repo_root.resolve())
    except Exception:
        entry["status"] = "BLOCKED"
        entry["reason"] = "outside-repo-root"
        return entry

    if dry_run:
        entry["status"] = "PLANNED"
        return entry

    shutil.rmtree(resolved)
    entry["status"] = "REMOVED"
    return entry


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    targets = build_targets(repo_root, args.include_root_logs)
    results = [remove_target(target, repo_root, args.dry_run) for target in targets]

    report = {
        "repo_root": str(repo_root),
        "dry_run": args.dry_run,
        "include_root_logs": args.include_root_logs,
        "results": results,
    }
    sys.stdout.write(json.dumps(report, indent=2))
    sys.stdout.write("\n")

    blocked = any(item["status"] == "BLOCKED" for item in results)
    return 1 if blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
