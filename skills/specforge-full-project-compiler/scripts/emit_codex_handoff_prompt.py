from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Emit a portable zero-context Codex prompt for SpecForge."
    )
    parser.add_argument("--project-name", required=True)
    parser.add_argument("--requirement", default="")
    parser.add_argument("--requirement-file", default="")
    parser.add_argument("--mode", choices=["inline", "file"], default="inline")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.mode == "file":
        requirement_file = normalize_requirement_file(args.requirement_file)
        prompt = build_file_prompt(args.project_name, requirement_file)
    else:
        prompt = build_inline_prompt(args.project_name, args.requirement)
    print(prompt)
    return 0


def normalize_requirement_file(raw: str) -> str:
    if not raw:
        return "<absolute-or-repo-relative-requirement-file>"
    return str(Path(raw))


def build_inline_prompt(project_name: str, requirement: str) -> str:
    requirement_text = requirement.strip() or "<one-line requirement>"
    return "\n".join(
        [
            "Use $specforge-full-project-compiler in this repository.",
            "Read README.md, WORKSPACE_LAYOUT.md, specforge-runtime/docs/PROJECT_COMPILER_PROTOCOL.md, and specforge-runtime/docs/ENVIRONMENT_MIGRATION_RUNBOOK.md.",
            f'Then compile a complete Spring Boot backend for the project "{project_name}" from this requirement:',
            "",
            requirement_text,
            "",
            "Execution contract:",
            "1. Check workspace readiness.",
            "2. Scaffold canonical specs from the requirement.",
            "3. Run the canonical auto-build pipeline.",
            "4. Continue until compile, boot, and delivery validation all pass, or return a reproducible failure bundle.",
            "5. Treat specforge-runtime/outputs/ as the only final deliverable.",
            "6. Read specforge-runtime/outputs/<project-backend>/logs/delivery-validation.yaml before claiming success.",
            "7. If the run fails, summarize the failure bundle paths under specforge-runtime/runs/<run-id>/generated-project/logs/ and specforge-runtime/runs/<run-id>/logs/auto-build-report.yaml.",
            "8. Do not ask me for step-by-step confirmation unless there is a destructive risk or a major architecture ambiguity.",
        ]
    )


def build_file_prompt(project_name: str, requirement_file: str) -> str:
    return "\n".join(
        [
            "Use $specforge-full-project-compiler in this repository.",
            "Read README.md, WORKSPACE_LAYOUT.md, specforge-runtime/docs/PROJECT_COMPILER_PROTOCOL.md, and specforge-runtime/docs/ENVIRONMENT_MIGRATION_RUNBOOK.md.",
            f'Then compile a complete Spring Boot backend for the project "{project_name}" from the requirement document at:',
            "",
            requirement_file,
            "",
            "Execution contract:",
            "1. Check workspace readiness.",
            "2. Normalize the requirement document into project scope.",
            "3. Scaffold or update canonical specs.",
            "4. Run the canonical auto-build pipeline.",
            "5. Continue until compile, boot, and delivery validation all pass, or return a reproducible failure bundle.",
            "6. Treat specforge-runtime/outputs/ as the only final deliverable.",
            "7. Read specforge-runtime/outputs/<project-backend>/logs/delivery-validation.yaml before claiming success.",
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
