from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate final SpecForge backend delivery against build and assembly contracts."
    )
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--build-plan", default="build-plan.yaml")
    parser.add_argument("--run-id", required=True)
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


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    runtime_root = repo_root / "specforge-runtime"
    specs_root = runtime_root / "specs"
    run_root = runtime_root / "runs" / args.run_id

    build_plan_path = resolve_build_plan(repo_root, args.build_plan)
    build_plan = load_yaml(build_plan_path)
    output_root = resolve_runtime_output_dir(runtime_root, build_plan, build_plan_path)
    auto_build_report = load_yaml(run_root / "logs" / "auto-build-report.yaml")
    assembly_plan = load_yaml(specs_root / str(build_plan.get("project_assembly_plan", "project-assembly-plan.yaml")))
    business_contract = load_yaml(output_root / "logs" / "api-smoke" / "business-contract-validation.yaml")
    coverage_contract = assembly_plan.get("coverage_contract", {})

    expected_modules = [
        {
            "module": str(item.get("module", "")),
            "export_package_root": str(item.get("export_package_root", "")),
            "semantic_role": str(item.get("semantic_role", "")),
            "business_center": str(item.get("business_center", "")),
        }
        for item in assembly_plan.get("module_sequence", [])
        if isinstance(item, dict) and item.get("enabled") is True and item.get("semantic_role") == "business-domain"
    ]
    actual_modules = {
        str(item.get("module_name", "")): item
        for item in business_contract.get("business_modules", [])
        if isinstance(item, dict)
    }
    required_module_names = [
        str(item)
        for item in coverage_contract.get("required_enabled_business_modules", [])
        if str(item).strip()
    ]
    required_business_centers = [
        str(item)
        for item in coverage_contract.get("required_business_centers", [])
        if str(item).strip()
    ]
    required_module_count = int(
        coverage_contract.get("required_enabled_business_module_count", len(required_module_names) or len(expected_modules))
    )
    expected_module_names = {item["module"] for item in expected_modules if item["module"]}
    expected_business_centers = [
        item["business_center"]
        for item in expected_modules
        if item.get("business_center")
    ]
    expected_business_center_set = set(expected_business_centers)

    findings: list[dict[str, str]] = []
    compile_status = str(auto_build_report.get("compile_status", "UNKNOWN"))
    boot_status = str(auto_build_report.get("boot_status", "UNKNOWN"))
    business_status = str((business_contract.get("validation") or {}).get("status", "UNKNOWN"))

    if compile_status != "PASS":
        findings.append({"code": "compile-status-failed", "details": f"compile_status={compile_status}"})
    if boot_status != "PASS":
        findings.append({"code": "boot-status-failed", "details": f"boot_status={boot_status}"})
    if business_status != "PASS":
        findings.append({"code": "business-contract-failed", "details": f"business_contract_status={business_status}"})
    if required_module_count and len(expected_modules) != required_module_count:
        findings.append(
            {
                "code": "assembly-coverage-count-mismatch",
                "details": f"coverage contract requires {required_module_count} business modules but assembly plan exposes {len(expected_modules)}",
            }
        )
    for required_name in required_module_names:
        if required_name not in expected_module_names:
            findings.append(
                {
                    "code": "assembly-required-module-not-enabled",
                    "details": f"{required_name} is required by coverage contract but missing from enabled module_sequence",
                }
            )
    duplicate_centers = sorted({center for center in expected_business_centers if expected_business_centers.count(center) > 1})
    for center in duplicate_centers:
        findings.append(
            {
                "code": "assembly-business-center-duplication",
                "details": f"{center} is assigned to multiple enabled business modules",
            }
        )
    for center in required_business_centers:
        if center not in expected_business_center_set:
            findings.append(
                {
                    "code": "assembly-required-business-center-missing",
                    "details": f"{center} is required by coverage contract but missing from enabled module_sequence",
                }
            )

    for module in expected_modules:
        package_root = module["export_package_root"]
        package_leaf = package_root.rsplit(".", 1)[-1] if package_root else ""
        matched = actual_modules.get(package_leaf)
        if matched is None:
            findings.append(
                {
                    "code": "expected-business-module-missing",
                    "details": f"{module['module']} expected package leaf {package_leaf} was not found in final backend",
                }
            )
            continue
        if int(matched.get("resource_count", 0)) <= 0:
            findings.append(
                {
                    "code": "expected-business-module-route-missing",
                    "details": f"{module['module']} exported without Resource routes",
                }
            )
        if int(matched.get("permission_constant_entry_count", 0)) <= 0:
            findings.append(
                {
                    "code": "expected-business-module-permission-missing",
                    "details": f"{module['module']} exported without permission constants",
                }
            )

    report = {
        "status": "PASS" if not findings else "FAIL",
        "run_id": args.run_id,
        "build_plan": str(build_plan_path),
        "output_root": str(output_root),
        "domain_profile": str(coverage_contract.get("domain_profile", "")),
        "platform_scope": str(coverage_contract.get("platform_scope", "")),
        "expected_business_module_count": len(expected_modules),
        "actual_business_module_count": len(actual_modules),
        "required_enabled_business_module_count": required_module_count,
        "compile_status": compile_status,
        "boot_status": boot_status,
        "business_contract_status": business_status,
        "findings": findings,
        "required_enabled_business_modules": required_module_names,
        "required_business_centers": required_business_centers,
        "expected_business_centers": sorted(expected_business_center_set),
        "expected_business_modules": expected_modules,
        "actual_business_modules": sorted(actual_modules.keys()),
    }

    delivery_report_path = output_root / "logs" / "delivery-validation.yaml"
    delivery_report_path.parent.mkdir(parents=True, exist_ok=True)
    delivery_report_path.write_text(
        yaml.safe_dump(report, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    sys.stdout.write(json.dumps(report, indent=2, ensure_ascii=False))
    sys.stdout.write("\n")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
