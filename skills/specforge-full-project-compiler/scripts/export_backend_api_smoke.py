from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export route index and Postman smoke assets from a generated backend."
    )
    parser.add_argument("--backend-root", required=True)
    parser.add_argument("--base-url", default="http://localhost:8080/api")
    parser.add_argument("--output-dir")
    parser.add_argument("--validate-business-contract", action="store_true")
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_package_name(source: str) -> str:
    match = re.search(r"^\s*package\s+([a-zA-Z0-9_.]+)\s*;", source, re.MULTILINE)
    return match.group(1) if match else ""


def parse_request_mapping(source: str) -> str | None:
    match = re.search(r'@RequestMapping\("([^"]+)"\)', source)
    return match.group(1) if match else None


def parse_methods(source: str) -> list[dict[str, object]]:
    method_pattern = re.compile(r"((?:@[A-Za-z]+(?:\([^\n]*?\))?\s*)+)public\s+ResponseEntity<", re.DOTALL)
    methods: list[dict[str, object]] = []
    for match in method_pattern.finditer(source):
        annotation_block = match.group(1)
        mapping = re.search(r'@(Get|Post|Put|Delete)Mapping(?:\("([^"]*)"\))?', annotation_block)
        if not mapping:
            continue
        authorization = re.search(r"@PreAuthorize\(\"hasAuthority\('([^']+)'\)\"\)", annotation_block)
        methods.append(
            {
                "http_method": mapping.group(1).upper(),
                "sub_path": mapping.group(2) or "",
                "authority": authorization.group(1) if authorization else None,
                "auth_required": bool(authorization),
            }
        )
    return methods


def parse_resources(java_root: Path) -> list[dict[str, object]]:
    routes: list[dict[str, object]] = []
    for source_file in sorted(java_root.rglob("*Resource.java")):
        source = read_text(source_file)
        if source_file.parent.name != "resource" and "@RestController" not in source:
            continue
        package_name = parse_package_name(source)
        request_mapping = parse_request_mapping(source)
        methods = parse_methods(source)
        if request_mapping is None:
            continue
        routes.append(
            {
                "class_name": source_file.stem,
                "package_name": package_name,
                "request_mapping": request_mapping,
                "methods": methods,
            }
        )
    return routes


def parse_permission_constants(java_root: Path) -> list[dict[str, object]]:
    constants: list[dict[str, object]] = []
    pattern = re.compile(r'public static final String ([A-Z0-9_]+) = "([^"]+)";')
    for source_file in sorted(java_root.rglob("*PermissionConstant.java")):
        source = read_text(source_file)
        package_name = parse_package_name(source)
        entries = [
            {
                "constant_name": match.group(1),
                "authority": match.group(2),
            }
            for match in pattern.finditer(source)
        ]
        constants.append(
            {
                "class_name": source_file.stem,
                "package_name": package_name,
                "constant_count": len(entries),
                "constants": entries,
            }
        )
    return constants


def build_postman_collection(base_url: str, routes: list[dict[str, object]]) -> dict[str, object]:
    items: list[dict[str, object]] = []
    for route in routes:
        request_mapping = str(route["request_mapping"])
        route_items: list[dict[str, object]] = []
        for method in route["methods"]:  # type: ignore[index]
            http_method = str(method["http_method"])
            sub_path = str(method["sub_path"])
            raw_path = request_mapping.rstrip("/")
            if sub_path:
                raw_path = raw_path + "/" + sub_path.lstrip("/")
            full_url = base_url.rstrip("/") + raw_path
            headers = [{"key": "Content-Type", "value": "application/json"}]
            if method["auth_required"]:
                headers.append({"key": "Authorization", "value": "Bearer {{accessToken}}"})

            request_payload: dict[str, object] = {
                "method": http_method,
                "header": headers,
                "url": {"raw": full_url, "host": [base_url], "path": raw_path.strip("/").split("/")},
            }
            if http_method in {"POST", "PUT"}:
                request_payload["body"] = {
                    "mode": "raw",
                    "raw": "{}",
                }

            route_items.append(
                {
                    "name": f"{http_method} {raw_path}",
                    "request": request_payload,
                }
            )

        items.append(
            {
                "name": str(route["class_name"]),
                "item": route_items,
            }
        )

    items.insert(
        0,
        {
            "name": "AuthorizeResource",
            "item": [
                {
                    "name": "POST /v1/authorize/login",
                    "request": {
                        "method": "POST",
                        "header": [{"key": "Content-Type", "value": "application/json"}],
                        "url": {
                            "raw": base_url.rstrip("/") + "/v1/authorize/login",
                            "host": [base_url],
                            "path": ["v1", "authorize", "login"],
                        },
                        "body": {
                            "mode": "raw",
                            "raw": json.dumps({"username": "{{username}}", "password": "{{password}}"}),
                        },
                    },
                }
            ],
        },
    )

    return {
        "info": {
            "name": "SpecForge Generated Backend Smoke Collection",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "variable": [
            {"key": "baseUrl", "value": base_url},
            {"key": "username", "value": "Admin"},
            {"key": "password", "value": ""},
            {"key": "accessToken", "value": ""},
        ],
        "item": items,
    }


def build_summary(routes: list[dict[str, object]]) -> dict[str, object]:
    business_routes = [
        route for route in routes if ".business." in str(route["package_name"])
    ]
    return {
        "resource_count": len(routes),
        "business_resource_count": len(business_routes),
        "route_count": sum(len(route["methods"]) for route in routes),
        "business_route_count": sum(len(route["methods"]) for route in business_routes),
    }


def build_business_module_index(java_root: Path, routes: list[dict[str, object]], permission_constants: list[dict[str, object]]) -> list[dict[str, object]]:
    module_names: set[str] = set()
    business_root = java_root / "org" / "eu" / "originalkeen" / "business"
    if business_root.exists():
        for child in sorted(business_root.iterdir()):
            if child.is_dir():
                module_names.add(child.name)

    route_map: dict[str, list[dict[str, object]]] = {}
    for route in routes:
        package_name = str(route["package_name"])
        marker = ".business."
        if marker not in package_name:
            continue
        suffix = package_name.split(marker, 1)[1]
        module_name = suffix.split(".", 1)[0]
        route_map.setdefault(module_name, []).append(route)

    permission_map: dict[str, list[dict[str, object]]] = {}
    for permission_constant in permission_constants:
        package_name = str(permission_constant["package_name"])
        marker = ".business."
        if marker not in package_name:
            continue
        suffix = package_name.split(marker, 1)[1]
        module_name = suffix.split(".", 1)[0]
        permission_map.setdefault(module_name, []).append(permission_constant)

    module_index: list[dict[str, object]] = []
    for module_name in sorted(module_names):
        if module_name == "personal":
            continue
        module_dir = business_root / module_name
        java_files = sorted(module_dir.rglob("*.java")) if module_dir.exists() else []
        if not java_files:
            continue
        module_routes = route_map.get(module_name, [])
        module_permission_constants = permission_map.get(module_name, [])
        module_index.append(
            {
                "module_name": module_name,
                "java_file_count": len(java_files),
                "resource_count": len(module_routes),
                "route_count": sum(len(route["methods"]) for route in module_routes),
                "permission_constant_class_count": len(module_permission_constants),
                "permission_constant_entry_count": sum(
                    int(item["constant_count"]) for item in module_permission_constants
                ),
                "resources": [route["class_name"] for route in module_routes],
                "permission_constant_classes": [item["class_name"] for item in module_permission_constants],
            }
        )
    return module_index


def validate_business_contract(module_index: list[dict[str, object]]) -> dict[str, object]:
    findings: list[dict[str, str]] = []
    for module in module_index:
        module_name = str(module["module_name"])
        if int(module["resource_count"]) == 0:
            findings.append(
                {
                    "code": "business-resource-missing",
                    "details": f"{module_name} does not expose any Resource route",
                }
            )
        if int(module["permission_constant_class_count"]) == 0:
            findings.append(
                {
                    "code": "business-permission-constant-missing",
                    "details": f"{module_name} does not define any PermissionConstant class",
                }
            )
        if int(module["permission_constant_entry_count"]) == 0:
            findings.append(
                {
                    "code": "business-permission-constant-empty",
                    "details": f"{module_name} PermissionConstant classes contain no authorities",
                }
            )

    return {
        "status": "PASS" if not findings else "FAIL",
        "finding_count": len(findings),
        "findings": findings,
        "module_count": len(module_index),
    }


def main() -> int:
    args = parse_args()
    backend_root = Path(args.backend_root).resolve()
    java_root = backend_root / "src" / "main" / "java"
    output_dir = Path(args.output_dir).resolve() if args.output_dir else (backend_root / "logs" / "api-smoke")
    output_dir.mkdir(parents=True, exist_ok=True)

    routes = parse_resources(java_root)
    permission_constants = parse_permission_constants(java_root)
    summary = build_summary(routes)
    module_index = build_business_module_index(java_root, routes, permission_constants)
    validation = validate_business_contract(module_index)
    collection = build_postman_collection(args.base_url, routes)

    route_index = {
        "backend_root": str(backend_root),
        "base_url": args.base_url,
        "summary": summary,
        "routes": routes,
    }
    permission_index = {
        "backend_root": str(backend_root),
        "permission_constants": permission_constants,
    }
    module_report = {
        "backend_root": str(backend_root),
        "business_modules": module_index,
        "validation": validation,
    }

    with (output_dir / "route-index.yaml").open("w", encoding="utf-8") as handle:
        yaml.safe_dump(route_index, handle, sort_keys=False, allow_unicode=True)
    with (output_dir / "business-permission-index.yaml").open("w", encoding="utf-8") as handle:
        yaml.safe_dump(permission_index, handle, sort_keys=False, allow_unicode=True)
    with (output_dir / "business-contract-validation.yaml").open("w", encoding="utf-8") as handle:
        yaml.safe_dump(module_report, handle, sort_keys=False, allow_unicode=True)
    with (output_dir / "postman-collection.json").open("w", encoding="utf-8") as handle:
        json.dump(collection, handle, indent=2, ensure_ascii=False)

    sys.stdout.write(
        json.dumps(
            {
                "output_dir": str(output_dir),
                "summary": summary,
                "validation": validation,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    sys.stdout.write("\n")
    if args.validate_business_contract and validation["status"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
