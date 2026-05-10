from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml


def load_yaml(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check whether a repository is ready for SpecForge full-project compilation.")
    parser.add_argument("--repo-root", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    runtime_root = repo_root / "specforge-runtime"
    backend_root = repo_root / "backend"
    specs_root = runtime_root / "specs"
    skills_root = repo_root / "skills" / "specforge-full-project-compiler"
    build_plan_path = specs_root / "build-plan.yaml"
    assembly_plan_path = specs_root / "project-assembly-plan.yaml"

    if str(runtime_root) not in sys.path:
        sys.path.insert(0, str(runtime_root))

    toolchain_binding: dict[str, object]
    try:
        from runtime.toolchain import resolve_toolchain

        toolchain_binding = resolve_toolchain()["binding"]
    except Exception as exc:  # pragma: no cover - defensive readiness reporting
        toolchain_binding = {
            "error": f"toolchain-resolution-failed: {exc}",
            "java_home": None,
            "maven_command": None,
        }

    build_plan = load_yaml(build_plan_path)
    assembly_plan = load_yaml(assembly_plan_path)
    required_scripts = [
        skills_root / "scripts" / "check_specforge_workspace.py",
        skills_root / "scripts" / "run_requirement_project.py",
        skills_root / "scripts" / "run_specforge_autobuild.py",
        skills_root / "scripts" / "scaffold_requirement_project.py",
        skills_root / "scripts" / "validate_sql_assets.py",
        skills_root / "scripts" / "validate_auth_surface.py",
        skills_root / "scripts" / "validate_backend_delivery.py",
        skills_root / "scripts" / "summarize_specforge_outcome.py",
    ]

    checks = {
        "repo_root": str(repo_root),
        "runtime_exists": runtime_root.exists(),
        "runtime_main_exists": (runtime_root / "main.py").exists(),
        "runtime_specs_exists": (runtime_root / "specs").exists(),
        "runtime_runtime_exists": (runtime_root / "runtime").exists(),
        "backend_exists": backend_root.exists(),
        "skills_root_exists": skills_root.exists(),
        "build_plan_exists": build_plan_path.exists(),
        "project_assembly_plan_exists": assembly_plan_path.exists(),
        "required_scripts_present": all(path.exists() for path in required_scripts),
        "required_script_paths": [str(path) for path in required_scripts],
        "build_plan_valid": bool(build_plan.get("plan_id")) and bool(build_plan.get("final_output_dir")),
        "project_assembly_plan_valid": bool(assembly_plan.get("plan_id")) and isinstance(assembly_plan.get("module_sequence"), list),
        "enabled_business_module_count": len(
            [
                item
                for item in assembly_plan.get("module_sequence", [])
                if isinstance(item, dict) and item.get("enabled") is True and item.get("semantic_role") == "business-domain"
            ]
        ),
        "toolchain": {
            "java_home": toolchain_binding.get("java_home"),
            "maven_command": toolchain_binding.get("maven_command"),
            "java_home_source": toolchain_binding.get("java_home_source"),
            "maven_source": toolchain_binding.get("maven_source"),
            "minimum_java_major": toolchain_binding.get("minimum_java_major"),
            "minimum_maven_version": toolchain_binding.get("minimum_maven_version"),
            "java_ready": bool(toolchain_binding.get("java_home")),
            "maven_ready": bool(toolchain_binding.get("maven_command")),
        },
    }
    checks["ready"] = all(
        checks[key]
        for key in (
            "runtime_exists",
            "runtime_main_exists",
            "runtime_specs_exists",
            "runtime_runtime_exists",
            "build_plan_exists",
            "project_assembly_plan_exists",
            "build_plan_valid",
            "project_assembly_plan_valid",
            "required_scripts_present",
        )
    ) and bool(checks["toolchain"]["java_ready"]) and bool(checks["toolchain"]["maven_ready"])
    sys.stdout.write(json.dumps(checks, indent=2))
    sys.stdout.write("\n")
    return 0 if checks["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
