from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize the final outcome of a SpecForge build attempt."
    )
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--build-plan", default="build-plan.yaml")
    return parser.parse_args()


def load_yaml(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def resolve_build_plan(repo_root: Path, build_plan: str) -> Path:
    candidate = Path(build_plan)
    if candidate.is_absolute():
        return candidate
    if (repo_root / build_plan).exists():
        return (repo_root / build_plan).resolve()
    return (repo_root / "specforge-runtime" / "specs" / build_plan).resolve()


def resolve_output_dir(runtime_root: Path, build_plan: dict[str, object], build_plan_path: Path) -> Path:
    raw_output = str(build_plan.get("final_output_dir", f"outputs/{build_plan_path.stem}"))
    candidate = Path(raw_output)
    return candidate if candidate.is_absolute() else (runtime_root / candidate).resolve()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    runtime_root = repo_root / "specforge-runtime"
    run_root = runtime_root / "runs" / args.run_id
    build_plan_path = resolve_build_plan(repo_root, args.build_plan)
    build_plan = load_yaml(build_plan_path)
    output_root = resolve_output_dir(runtime_root, build_plan, build_plan_path)

    auto_build_report = load_yaml(run_root / "logs" / "auto-build-report.yaml")
    project_health_report = load_yaml(run_root / "generated-project" / "logs" / "project-health-report.yaml")
    delivery_validation = load_yaml(output_root / "logs" / "delivery-validation.yaml")
    business_contract = load_yaml(output_root / "logs" / "api-smoke" / "business-contract-validation.yaml")
    sql_asset_validation = load_yaml(output_root / "logs" / "sql-asset-validation.yaml")
    auth_surface_validation = load_yaml(output_root / "logs" / "auth-surface-validation.yaml")

    compile_status = str(
        auto_build_report.get(
            "compile_status",
            project_health_report.get("compile_status", "UNKNOWN"),
        )
    )
    boot_status = str(
        auto_build_report.get(
            "boot_status",
            project_health_report.get("boot_status", "UNKNOWN"),
        )
    )
    delivery_status = str(delivery_validation.get("status", "UNKNOWN"))
    business_status = str((business_contract.get("validation") or {}).get("status", "UNKNOWN"))
    sql_asset_status = str(sql_asset_validation.get("status", "UNKNOWN"))
    auth_surface_status = str(auth_surface_validation.get("status", "UNKNOWN"))

    status = "FAIL"
    if (
        compile_status == "PASS"
        and boot_status == "PASS"
        and delivery_status == "PASS"
        and business_status == "PASS"
        and sql_asset_status == "PASS"
        and auth_surface_status == "PASS"
    ):
        status = "PASS"

    summary = {
        "status": status,
        "run_id": args.run_id,
        "build_plan": str(build_plan_path),
        "compile_status": compile_status,
        "boot_status": boot_status,
        "business_contract_status": business_status,
        "delivery_validation_status": delivery_status,
        "sql_asset_status": sql_asset_status,
        "auth_surface_status": auth_surface_status,
        "final_output_dir": str(output_root),
        "delivery_validation_report": str(output_root / "logs" / "delivery-validation.yaml"),
        "business_contract_report": str(output_root / "logs" / "api-smoke" / "business-contract-validation.yaml"),
        "sql_asset_validation_report": str(output_root / "logs" / "sql-asset-validation.yaml"),
        "auth_surface_validation_report": str(output_root / "logs" / "auth-surface-validation.yaml"),
        "auto_build_report": str(run_root / "logs" / "auto-build-report.yaml"),
        "project_health_report": str(run_root / "generated-project" / "logs" / "project-health-report.yaml"),
        "failure_bundle": {
            "compile_diagnostics": str(run_root / "generated-project" / "logs" / "compile-diagnostics.yaml"),
            "compile_repair_report": str(run_root / "generated-project" / "logs" / "compile-repair-report.yaml"),
            "boot_diagnostics": str(run_root / "generated-project" / "logs" / "boot-diagnostics.yaml"),
            "boot_repair_report": str(run_root / "generated-project" / "logs" / "boot-repair-report.yaml"),
            "project_health_report": str(run_root / "generated-project" / "logs" / "project-health-report.yaml"),
            "auto_build_report": str(run_root / "logs" / "auto-build-report.yaml"),
            "delivery_validation_report": str(output_root / "logs" / "delivery-validation.yaml"),
            "business_contract_report": str(output_root / "logs" / "api-smoke" / "business-contract-validation.yaml"),
            "sql_asset_validation_report": str(output_root / "logs" / "sql-asset-validation.yaml"),
            "auth_surface_validation_report": str(output_root / "logs" / "auth-surface-validation.yaml"),
        },
    }
    sys.stdout.write(json.dumps(summary, indent=2, ensure_ascii=False))
    sys.stdout.write("\n")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
