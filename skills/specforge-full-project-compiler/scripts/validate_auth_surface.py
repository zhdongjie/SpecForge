from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate generated auth/login surface for a SpecForge backend delivery."
    )
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--build-plan", default="build-plan.yaml")
    return parser.parse_args()


def load_yaml(path: Path) -> dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(str(path))
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def resolve_build_plan(repo_root: Path, build_plan: str) -> Path:
    candidate = Path(build_plan)
    if candidate.is_absolute():
        return candidate
    if (repo_root / build_plan).exists():
        return (repo_root / build_plan).resolve()
    return (repo_root / "specforge-runtime" / "specs" / build_plan).resolve()


def resolve_runtime_output_dir(runtime_root: Path, build_plan: dict[str, object], build_plan_path: Path) -> Path:
    raw_output = str(build_plan.get("final_output_dir", f"outputs/{build_plan_path.stem}"))
    candidate = Path(raw_output)
    return candidate if candidate.is_absolute() else (runtime_root / candidate).resolve()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    runtime_root = repo_root / "specforge-runtime"
    build_plan_path = resolve_build_plan(repo_root, args.build_plan)
    build_plan = load_yaml(build_plan_path)
    output_root = resolve_runtime_output_dir(runtime_root, build_plan, build_plan_path)

    findings: list[dict[str, str]] = []
    auth_resource_path = output_root / "src" / "main" / "java" / "org" / "eu" / "originalkeen" / "authorize" / "resource" / "AuthorizeResource.java"
    postman_path = output_root / "logs" / "api-smoke" / "postman-collection.json"
    postman_environment_path = output_root / "logs" / "api-smoke" / "postman-environment.json"
    demo_access_path = output_root / "logs" / "demo-access.yaml"
    demo_password_reset_path = output_root / "src" / "main" / "resources" / "sql" / "demo-password-reset.sql"
    schema_path = output_root / "src" / "main" / "resources" / "sql" / "schema.sql"

    auth_checks = {
        "authorize_resource_exists": auth_resource_path.exists(),
        "request_mapping_present": False,
        "login_endpoint_present": False,
        "postman_login_present": False,
        "seed_admin_present": False,
        "postman_environment_present": postman_environment_path.exists(),
        "demo_access_present": demo_access_path.exists(),
        "demo_password_reset_present": demo_password_reset_path.exists(),
    }

    if not auth_resource_path.exists():
        findings.append(
            {
                "code": "authorize-resource-missing",
                "details": f"Missing authorize resource: {auth_resource_path}",
            }
        )
    else:
        source = read_text(auth_resource_path)
        auth_checks["request_mapping_present"] = '@RequestMapping("/v1/authorize")' in source
        auth_checks["login_endpoint_present"] = '@PostMapping("/login")' in source
        if not auth_checks["request_mapping_present"]:
            findings.append(
                {
                    "code": "authorize-request-mapping-missing",
                    "details": 'AuthorizeResource missing @RequestMapping("/v1/authorize")',
                }
            )
        if not auth_checks["login_endpoint_present"]:
            findings.append(
                {
                    "code": "authorize-login-endpoint-missing",
                    "details": 'AuthorizeResource missing @PostMapping("/login")',
                }
            )

    if not postman_path.exists():
        findings.append(
            {
                "code": "postman-collection-missing",
                "details": f"Missing Postman collection: {postman_path}",
            }
        )
    else:
        postman_text = read_text(postman_path)
        auth_checks["postman_login_present"] = "POST /v1/authorize/login" in postman_text
        if not auth_checks["postman_login_present"]:
            findings.append(
                {
                    "code": "postman-login-missing",
                    "details": "Postman smoke collection does not include POST /v1/authorize/login",
                }
            )

    if not postman_environment_path.exists():
        findings.append(
            {
                "code": "postman-environment-missing",
                "details": f"Missing Postman environment: {postman_environment_path}",
            }
        )

    if not demo_access_path.exists():
        findings.append(
            {
                "code": "demo-access-missing",
                "details": f"Missing demo access handoff file: {demo_access_path}",
            }
        )
    else:
        demo_access_text = read_text(demo_access_path)
        if "Admin@123456" not in demo_access_text or "/v1/authorize/login" not in demo_access_text:
            findings.append(
                {
                    "code": "demo-access-incomplete",
                    "details": "demo-access.yaml does not expose the expected login endpoint and demo credentials",
                }
            )

    if not demo_password_reset_path.exists():
        findings.append(
            {
                "code": "demo-password-reset-missing",
                "details": f"Missing deterministic demo password reset SQL: {demo_password_reset_path}",
            }
        )
    else:
        reset_sql_text = read_text(demo_password_reset_path)
        if "Admin@123456" in reset_sql_text:
            findings.append(
                {
                    "code": "demo-password-reset-plaintext-leak",
                    "details": "demo-password-reset.sql should store encoded passwords instead of plaintext credentials",
                }
            )
        if "UPDATE `SYSTEM_USER`" not in reset_sql_text.upper():
            findings.append(
                {
                    "code": "demo-password-reset-update-missing",
                    "details": "demo-password-reset.sql does not contain expected system_user update statements",
                }
            )

    if not schema_path.exists():
        findings.append(
            {
                "code": "schema-missing",
                "details": f"Missing schema.sql: {schema_path}",
            }
        )
    else:
        schema_text = read_text(schema_path)
        has_user_seed = "system_user" in schema_text and "Admin" in schema_text and "INSERT INTO" in schema_text.upper()
        auth_checks["seed_admin_present"] = has_user_seed
        if not has_user_seed:
            findings.append(
                {
                    "code": "admin-seed-missing",
                    "details": "schema.sql does not expose expected Admin/system_user seed data",
                }
            )

    report = {
        "status": "PASS" if not findings else "FAIL",
        "run_id": args.run_id,
        "build_plan": str(build_plan_path),
        "output_root": str(output_root),
        "checks": auth_checks,
        "finding_count": len(findings),
        "findings": findings,
    }

    report_path = output_root / "logs" / "auth-surface-validation.yaml"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        yaml.safe_dump(report, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    sys.stdout.write(json.dumps(report, indent=2, ensure_ascii=False))
    sys.stdout.write("\n")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
