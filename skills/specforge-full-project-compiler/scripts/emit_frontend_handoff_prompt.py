from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Emit a portable zero-context Codex prompt for frontend handoff against a generated SpecForge backend."
    )
    parser.add_argument("--backend-output", required=True)
    parser.add_argument("--project-name", default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    backend_output = str(Path(args.backend_output))
    project_name = args.project_name.strip() or "<project-name>"
    print(build_prompt(project_name, backend_output))
    return 0


def build_prompt(project_name: str, backend_output: str) -> str:
    return "\n".join(
        [
            "Use this repository's generated backend as the only backend contract source.",
            "Do not ask me to restate the backend API manually.",
            f'The target project is "{project_name}".',
            "Read these files first:",
            f"1. {backend_output}/logs/demo-access.yaml",
            f"2. {backend_output}/logs/api-smoke/postman-collection.json",
            f"3. {backend_output}/logs/api-smoke/postman-environment.json",
            f"4. {backend_output}/logs/delivery-validation.yaml",
            f"5. {backend_output}/logs/api-smoke/business-contract-validation.yaml",
            "",
            "Execution contract:",
            "1. Infer the frontend login flow, token usage, route groups, and business modules from those backend delivery assets.",
            "2. Treat /v1/authorize/login as the canonical login entry.",
            "3. Use the demo credentials and baseUrl contract from demo-access.yaml and postman-environment.json.",
            "4. Build or adapt the frontend against the real generated business routes instead of inventing mock APIs.",
            "5. Keep going until the frontend can complete login and call at least one representative business endpoint successfully.",
            "6. If there is a backend/frontend mismatch, report the exact backend asset file that proves the contract.",
            "7. Do not ask me for step-by-step confirmation unless there is a destructive risk.",
            "",
            "Success return:",
            "- backend output path used",
            "- login endpoint used",
            "- token handling convention used",
            "- business route groups consumed",
            "- remaining backend contract gaps, if any",
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
