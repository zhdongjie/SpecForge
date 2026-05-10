from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate generated SQL assets for a SpecForge backend delivery."
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
    specs_root = runtime_root / "specs"
    build_plan_path = resolve_build_plan(repo_root, args.build_plan)
    build_plan = load_yaml(build_plan_path)
    output_root = resolve_runtime_output_dir(runtime_root, build_plan, build_plan_path)
    assembly_plan = load_yaml(specs_root / str(build_plan.get("project_assembly_plan", "project-assembly-plan.yaml")))

    sql_root = output_root / "src" / "main" / "resources" / "sql"
    findings: list[dict[str, str]] = []
    enabled_business_modules = [
        str(item.get("module", "")).strip()
        for item in assembly_plan.get("module_sequence", [])
        if isinstance(item, dict) and item.get("enabled") is True and item.get("semantic_role") == "business-domain"
    ]

    sql_files: list[dict[str, object]] = []
    if not sql_root.exists():
        findings.append({"code": "sql-root-missing", "details": f"Missing SQL directory: {sql_root}"})
    else:
        schema_path = sql_root / "schema.sql"
        if not schema_path.exists():
            findings.append({"code": "schema-missing", "details": "schema.sql was not generated"})
        else:
            schema_text = read_text(schema_path)
            if not schema_text.strip():
                findings.append({"code": "schema-empty", "details": "schema.sql is empty"})
            if "CREATE TABLE" not in schema_text.upper():
                findings.append({"code": "schema-create-table-missing", "details": "schema.sql contains no CREATE TABLE statements"})

        actual_generated_files = {path.name: path for path in sorted(sql_root.glob("*.generated.sql"))}
        for module_name in enabled_business_modules:
            expected_name = f"{module_name}.generated.sql"
            file_path = actual_generated_files.get(expected_name)
            if file_path is None:
                findings.append(
                    {
                        "code": "module-sql-missing",
                        "details": f"{module_name} is enabled but {expected_name} is missing",
                    }
                )
                continue

            text = read_text(file_path)
            if not text.strip():
                findings.append(
                    {
                        "code": "module-sql-empty",
                        "details": f"{expected_name} is empty",
                    }
                )
            if "CREATE TABLE" not in text.upper():
                findings.append(
                    {
                        "code": "module-sql-create-table-missing",
                        "details": f"{expected_name} contains no CREATE TABLE statements",
                    }
                )
            sql_files.append(
                {
                    "module": module_name,
                    "file": expected_name,
                    "size_bytes": file_path.stat().st_size,
                }
            )

    report = {
        "status": "PASS" if not findings else "FAIL",
        "run_id": args.run_id,
        "build_plan": str(build_plan_path),
        "output_root": str(output_root),
        "sql_root": str(sql_root),
        "enabled_business_modules": enabled_business_modules,
        "validated_sql_files": sql_files,
        "finding_count": len(findings),
        "findings": findings,
    }

    report_path = output_root / "logs" / "sql-asset-validation.yaml"
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
