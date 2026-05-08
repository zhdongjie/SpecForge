from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bootstrap a portable SpecForge workspace bundle.")
    parser.add_argument("--source-repo", required=True)
    parser.add_argument("--target-workspace", required=True)
    parser.add_argument("--include-skill", action="store_true")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_repo = Path(args.source_repo).resolve()
    target_workspace = Path(args.target_workspace).resolve()

    required_sources = [
        source_repo / "specforge-runtime",
        source_repo / "backend",
    ]
    if args.include_skill:
        required_sources.append(source_repo / "skills" / "specforge-full-project-compiler")

    missing = [str(path) for path in required_sources if not path.exists()]
    if missing:
        for item in missing:
            print(f"[ERROR] Missing source path: {item}", file=sys.stderr)
        return 2

    target_workspace.mkdir(parents=True, exist_ok=True)
    copy_pairs = [
        (source_repo / "specforge-runtime", target_workspace / "specforge-runtime"),
        (source_repo / "backend", target_workspace / "backend"),
    ]
    if args.include_skill:
        copy_pairs.append(
            (
                source_repo / "skills" / "specforge-full-project-compiler",
                target_workspace / "skills" / "specforge-full-project-compiler",
            )
        )

    for source, target in copy_pairs:
        if target.exists():
            if not args.force:
                print(f"[ERROR] Target already exists: {target}", file=sys.stderr)
                print("[HINT] Re-run with --force to replace existing targets.", file=sys.stderr)
                return 3
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
        shutil.copytree(
            source,
            target,
            ignore=shutil.ignore_patterns("target", ".git", ".idea", "__pycache__", ".m2"),
        )
        print(f"[OK] Copied {source.name} -> {target}")

    print("[OK] SpecForge starter bundle initialized.")
    print(f"[INFO] Workspace: {target_workspace}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
