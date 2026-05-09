from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

import yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scaffold SpecForge project specs from a short requirement.")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--project-name", required=True)
    parser.add_argument("--requirement", default="")
    parser.add_argument("--requirement-file", default="")
    parser.add_argument("--domain", default="auto")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    specs_root = repo_root / "specforge-runtime" / "specs"
    templates_root = specs_root / "templates"
    requirement_text = load_requirement_text(args.requirement, args.requirement_file)
    blueprints = load_blueprints(Path(__file__).resolve().parent.parent / "references" / "module-blueprints.yaml")
    domain_key = infer_domain(args.project_name, requirement_text, args.domain, blueprints)
    domain_blueprint = blueprints["domains"][domain_key]

    write_project_spec(specs_root / "project-spec.md", args.project_name, requirement_text, domain_blueprint)
    write_project_assembly_plan(specs_root / "project-assembly-plan.yaml", args.project_name, domain_blueprint)
    write_build_plan(specs_root / "build-plan.yaml", args.project_name)
    write_template_modules(templates_root, domain_blueprint, force=args.force)
    return 0


def load_requirement_text(inline_text: str, file_path: str) -> str:
    if file_path:
        return Path(file_path).read_text(encoding="utf-8").strip()
    return inline_text.strip()


def load_blueprints(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def infer_domain(project_name: str, requirement_text: str, domain: str, blueprints: dict[str, Any]) -> str:
    if domain and domain != "auto":
        return domain

    haystack = f"{project_name}\n{requirement_text}".lower()
    keyword_map = [
        ("laboratory-management", ["equipment", "consumable", "experiment", "schedule", "calendar", "report", "statistics", "lab manager", "lab management"]),
        ("insurance-management", ["insurance", "claim", "policy", "premium", "underwriting", "agent", "beneficiary", "renewal"]),
        ("laboratory-reservation", ["laboratory", "lab ", "reservation", "experiment", "equipment", "consumable", "schedule", "booking"]),
    ]
    for domain_key, keywords in keyword_map:
        if any(keyword in haystack for keyword in keywords):
            return domain_key

    return next(iter(blueprints.get("domains", {})), "laboratory-reservation")


def write_project_spec(path: Path, project_name: str, requirement_text: str, blueprint: dict[str, Any]) -> None:
    project = blueprint["project"]
    modules = blueprint["modules"]
    payload = {
        "project": {
            "name": project_name,
            "type": "springboot-vue3",
        },
        "architecture": {
            "style": "modular-monolith",
            "description": "A modular-monolith Spring Boot backend compiled from SpecForge project and module specifications.",
        },
        "modules": [
            {
                "name": item["module"],
                "responsibility": item["purpose"],
                "boundaries": f"Owns {', '.join(item['entities'])} within {item['bounded_context']}.",
                "apis": [f"{item['module']} administration"],
                "entities": item["entities"],
            }
            for item in modules
        ],
        "features": [
            f"Support {normalize_title(item['module'])} workflows." for item in modules
        ],
        "auth": {
            "type": "jwt",
            "roles": project["primary_roles"],
        },
        "database": {
            "type": "mysql",
            "tables": [
                {"name": table, "purpose": f"Persistence for {item['module']}"}
                for item in modules
                for table in item["tables"]
            ],
        },
        "frontend": {"pages": []},
        "business_rules": project["business_rules"] + ([requirement_text] if requirement_text else []),
        "dependencies": {
            "backend": [
                "Spring Boot",
                "Spring Security",
                "Spring Validation",
                "MyBatis-Flex",
                "MySQL",
                "Redis",
                "Jose4j",
            ],
            "frontend": [],
        },
        "generation_contract": [
            "Preserve modular-monolith boundaries.",
            "Keep business-domain code under org.eu.originalkeen.business.*.",
            "Require compile and boot verification before success.",
        ],
    }
    write_yaml_as_markdown(path, payload)


def write_project_assembly_plan(path: Path, project_name: str, blueprint: dict[str, Any]) -> None:
    plan_id = slugify(project_name)
    modules = blueprint["modules"]
    payload = {
        "plan_id": plan_id,
        "target_backend_name": f"{plan_id}-backend",
        "description": f"deterministic backend assembly plan for {project_name}",
        "project_identity": {
            "name": project_name,
            "architecture": "modular-monolith",
            "package_root": "org.eu.originalkeen",
        },
        "platform_contract": {
            "auth_mode": "jwt",
            "response_wrapper": "unified",
            "pagination_contract": "pageNum-pageSize",
            "audit_mode": "centralized",
            "business_domain_rule": {
                "package_root_prefix": "org.eu.originalkeen.business.",
                "route_prefix": "/v1/business/",
                "authority_prefix": "business:",
            },
        },
        "module_sequence": [
            {
                "module": item["module"],
                "enabled": bool(item["enabled"]),
                "semantic_role": item["semantic_role"],
                "bounded_context": item["bounded_context"],
                "module_spec": (
                    "module-spec.yaml"
                    if item["module"] == "laboratory-reservation-management"
                    else f"templates/{item['module']}/module-spec.yaml"
                ),
                "module_schema": (
                    "module-schema.resolved.yaml"
                    if item["module"] == "laboratory-reservation-management"
                    else f"templates/{item['module']}/module-schema.resolved.yaml"
                ),
                "generation_mode": "synthesize-and-assemble",
                "dependencies": [],
                "export_package_root": item["package_root"],
            }
            for item in modules
        ],
        "assembly_contract": {
            "compile_required": True,
            "boot_verify_required": True,
            "auto_repair_enabled": True,
            "final_output_dir": f"outputs/{plan_id}-backend",
            "failure_bundle_required": True,
        },
    }
    write_yaml(path, payload)


def write_build_plan(path: Path, project_name: str) -> None:
    plan_id = slugify(project_name)
    payload = {
        "plan_id": plan_id,
        "default_run_id": f"{plan_id}-autobuild",
        "backend_root": "../backend",
        "final_output_dir": f"outputs/{plan_id}-backend",
        "project_assembly_plan": "project-assembly-plan.yaml",
        "module_spec": "module-spec.yaml",
        "module_schema": "module-schema.resolved.yaml",
        "auto_repair": True,
        "verify_boot": True,
        "repair_max_passes": 5,
        "goal": "bootable-generated-backend",
        "notes": [
            "use canonical specs in this directory",
            "project-level assembly is enabled",
            "compile and boot verification are mandatory",
        ],
    }
    write_yaml(path, payload)


def write_template_modules(templates_root: Path, blueprint: dict[str, Any], force: bool = False) -> None:
    for item in blueprint["modules"]:
        if item["module"] == "laboratory-reservation-management":
            continue
        module_root = templates_root / item["module"]
        module_root.mkdir(parents=True, exist_ok=True)
        module_spec_path = module_root / "module-spec.yaml"
        module_schema_path = module_root / "module-schema.resolved.yaml"
        if force or not module_spec_path.exists():
            write_yaml(module_spec_path, build_module_spec_blueprint(item))
        if force or not module_schema_path.exists():
            write_yaml(module_schema_path, build_module_schema_blueprint(item))


def build_module_spec_blueprint(item: dict[str, Any]) -> dict[str, Any]:
    token = semantic_token(item["module"])
    entity_prefix = normalize_title(item["module"]).replace(" ", "")
    route_segment = token.replace("_", "-")
    return {
        "compiler_context": {
            "source_spec_id": f"{token}-project-v1",
            "target_module_id": item["module"],
            "regeneration_mode": "create",
            "stability_goal": "deterministic",
            "planner_tags": ["bounded-module", item["bounded_context"], "default-enabled-blueprint"],
        },
        "module_identity": {
            "module_name": item["module"],
            "bounded_context": item["bounded_context"],
            "semantic_role": item["semantic_role"],
            "responsibility_code": token,
            "package_root": item["package_root"],
            "route_namespace": {
                route_segment: item["route_roots"][0],
            },
        },
        "generation_boundaries": {
            "single_module_only": True,
            "owns_aggregates": item["entities"],
            "may_reference": ["ResponseVo", "PageVo", "OperateLog", "PreAuthorize"],
            "must_not_generate": ["authentication flows", "user management", "role management"],
        },
        "api_groups": [
            {
                "group_id": token,
                "route_prefix": item["route_roots"][0],
                "aggregate": item["entities"][0],
                "capability_ids": [
                    f"create-{token}",
                    f"update-{token}",
                    f"batch-delete-{token}",
                    f"enquiry-{token}-page",
                    f"enquiry-{token}-details",
                    f"enquiry-{token}-list",
                ],
            }
        ],
        "capabilities": [
            build_capability(f"create-{token}", token, item, "POST", "/", f"Create{entity_prefix}Dto", "Void", "create-record"),
            build_capability(f"update-{token}", token, item, "PUT", "/", f"Update{entity_prefix}Dto", "Void", "update-record"),
            build_capability(f"batch-delete-{token}", token, item, "DELETE", "/", f"{entity_prefix}IdSet", "Void", "delete-record"),
            build_capability(f"enquiry-{token}-page", token, item, "GET", "/page", f"Enquiry{entity_prefix}PageDto", f"PageVo<{entity_prefix}PageVo>", "query-page"),
            build_capability(f"enquiry-{token}-details", token, item, "GET", "/{id}", f"{entity_prefix}IdPath", f"{entity_prefix}DetailsVo", "query-details"),
            build_capability(f"enquiry-{token}-list", token, item, "GET", "/list", "None", f"List<{entity_prefix}ListVo>", "query-list"),
        ],
        "entity_graph": {
            "entities": [
                {
                    "entity_id": entity,
                    "table": table,
                    "ownership": "owned",
                    "base_type": "PrimaryKeyEntity",
                    "aggregate_role": "root",
                    "relations": [],
                }
                for entity, table in zip(item["entities"], item["tables"])
            ]
        },
        "artifact_contract": {
            "resource": [f"{entity_prefix}Resource"],
            "manager": [f"{entity_prefix}Manager"],
            "service": [f"{entity_prefix}Service"],
            "service_impl": [f"{entity_prefix}ServiceImpl"],
            "mapper": [f"{entity_prefix}Mapper"],
            "entity": item["entities"],
            "dto": [f"Create{entity_prefix}Dto", f"Update{entity_prefix}Dto", f"Enquiry{entity_prefix}PageDto"],
            "vo": [f"{entity_prefix}DetailsVo", f"{entity_prefix}PageVo", f"{entity_prefix}ListVo"],
            "bo": [],
        },
        "validation_rules": {"uniqueness": [], "referential": [], "shape": []},
        "architecture_constraints": {
            "modular_monolith_mode": True,
            "response_wrapper_must_be": "ResponseVo",
            "page_wrapper_must_be": "PageVo",
            "security_annotation_required": True,
        },
        "persistence_conventions": {"framework": "mybatis-flex", "database": "mysql"},
        "localization_requirements": {"mandatory": False, "languages": [], "localized_aggregates": [], "localized_fields": {}, "fallback_policy": "none"},
        "audit_behavior": {"access_log": "none", "operate_log": {"enabled": True, "target_capabilities": [f"create-{token}", f"update-{token}", f"batch-delete-{token}"]}},
        "generation_contract": {
            "deterministic_output_required": True,
            "preserve_project_contracts": ["modular-monolith-boundaries", "centralized-authority-based-security"],
            "blueprint_status": "default-enabled-validated-blueprint",
        },
    }


def build_module_schema_blueprint(item: dict[str, Any]) -> dict[str, Any]:
    token = semantic_token(item["module"])
    entity_prefix = normalize_title(item["module"]).replace(" ", "")
    return {
        "resolution_context": {
            "source_module_spec": "module-spec.yaml",
            "resolved_schema_id": f"{token}-resolved-v1",
            "target_module_id": item["module"],
            "bounded_context": item["bounded_context"],
            "regeneration_mode": "create",
            "stability_goal": "deterministic",
            "compiler_stage": "resolved-generation-plan",
            "dag_compatible": True,
            "multi_agent_safe": True,
        },
        "module_identity": {
            "module_name": item["module"],
            "semantic_role": item["semantic_role"],
            "responsibility_code": token,
            "package_root": item["package_root"],
            "route_roots": item["route_roots"],
        },
        "api_groups": [
            {
                "group_id": token,
                "route_prefix": item["route_roots"][0],
                "aggregate": item["entities"][0],
                "capability_ids": [
                    f"create-{token}",
                    f"update-{token}",
                    f"batch-delete-{token}",
                    f"enquiry-{token}-page",
                    f"enquiry-{token}-details",
                    f"enquiry-{token}-list",
                ],
            }
        ],
        "capabilities": [],
        "entity_graph": {
            "entities": [
                {
                    "entity_id": entity,
                    "table": table,
                    "ownership": "owned",
                    "base_type": "PrimaryKeyEntity",
                    "aggregate_role": "root",
                    "relations": [],
                }
                for entity, table in zip(item["entities"], item["tables"])
            ]
        },
        "validation_rules": {"uniqueness": [], "referential": [], "shape": []},
        "architectural_bindings": {
            "code_conventions": {
                "resource_suffix": "Resource",
                "manager_suffix": "Manager",
                "service_suffix": "Service",
                "service_impl_suffix": "ServiceImpl",
                "mapper_suffix": "Mapper",
            },
            "response_bindings": {"wrapper_type": "ResponseVo", "page_type": "PageVo", "mutation_payload": "Void"},
            "persistence_bindings": {"framework": "mybatis-flex", "aggregate_identity_style": "primary-key-entity"},
        },
        "persistence_conventions": {"framework": "mybatis-flex", "database": "mysql"},
        "localization_requirements": {"mandatory": False, "languages": [], "localized_aggregates": [], "localized_fields": {}, "fallback_policy": "none"},
        "audit_behavior": {"access_log": "none", "operate_log": {"enabled": True, "target_capabilities": [f"create-{token}", f"update-{token}", f"batch-delete-{token}"]}},
        "integration_points": {
            "security": {"mode": "centralized-method-security", "authority_families": item["authorities"]},
            "persistence": {"database": "mysql", "required_tables": item["tables"]},
        },
        "code_conventions": {
            "naming_stability": "strict",
            "route_style": "business-domain-aligned",
            "transaction_style": "manager-boundary",
        },
        "validation_hooks": {
            "pre_generation": ["hook-discovery-baseline-complete"],
            "post_unit": ["hook-artifact-name-convention", "hook-package-placement-check"],
            "final": ["hook-module-boundary-check", "hook-deterministic-layout-check"],
        },
        "blueprint_status": f"default-enabled-validated-blueprint-for-{entity_prefix}",
    }


def build_capability(capability_id: str, token: str, item: dict[str, Any], method: str, route: str, input_dto: str, output_vo: str, intent: str) -> dict[str, Any]:
    return {
        "capability_id": capability_id,
        "semantic_intent": intent,
        "deterministic_pattern": infer_pattern(intent),
        "stability_class": "stable",
        "api_group": token,
        "http_method": method,
        "route": route,
        "authority": item["authorities"][0].replace("*", capability_action(capability_id)),
        "transaction": "read-only" if method == "GET" else "read-write",
        "input_dto": input_dto,
        "output_vo": output_vo,
        "touched_entities": item["entities"],
    }


def capability_action(capability_id: str) -> str:
    if capability_id.startswith("create-"):
        return "create"
    if capability_id.startswith("update-"):
        return "update"
    if capability_id.startswith("batch-delete-"):
        return "delete"
    if capability_id.endswith("-page"):
        return "page"
    if capability_id.endswith("-details"):
        return "details"
    return "list"


def infer_pattern(intent: str) -> str:
    mapping = {
        "create-record": "create",
        "update-record": "update",
        "delete-record": "batch-delete",
        "query-page": "page",
        "query-details": "details",
        "query-list": "list",
    }
    return mapping[intent]


def write_yaml_as_markdown(path: Path, payload: dict[str, Any]) -> None:
    text = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_yaml(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, sort_keys=False, allow_unicode=True)


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "generated-project"


def normalize_title(value: str) -> str:
    return " ".join(part.capitalize() for part in value.replace("-", " ").replace("_", " ").split())


def semantic_token(value: str) -> str:
    return value.replace("-", "_")


if __name__ == "__main__":
    raise SystemExit(main())
