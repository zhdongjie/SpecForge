from __future__ import annotations

from dataclasses import dataclass
import re
import shutil
from pathlib import Path
from typing import Any

import yaml


class CodegenError(RuntimeError):
    pass


def package_to_path(package_name: str) -> Path:
    return Path(*package_name.split("."))


def safe_load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise CodegenError(f"{path} must contain a top-level mapping")
    return data


def dump_yaml(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, sort_keys=False, allow_unicode=True)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)


def parse_package_name(source: str) -> str:
    match = re.search(r"^\s*package\s+([a-zA-Z0-9_.]+)\s*;", source, re.MULTILINE)
    if not match:
        raise CodegenError("Java source is missing a package declaration")
    return match.group(1)


def parse_request_mapping(source: str) -> str | None:
    match = re.search(r'@RequestMapping\("([^"]+)"\)', source)
    return match.group(1) if match else None


def parse_preauthorize_values(source: str) -> list[str]:
    return re.findall(r"@PreAuthorize\(\"hasAuthority\('([^']+)'\)\"\)", source)


def parse_operate_log_titles(source: str) -> list[str]:
    return re.findall(r'@OperateLog\(title = "([^"]+)"', source)


def parse_table_name(source: str) -> str | None:
    match = re.search(r'@Table\("([^"]+)"\)', source)
    return match.group(1) if match else None


def java_private_fields(source: str) -> list[str]:
    return re.findall(r"private\s+[A-Za-z0-9_<>, ?]+\s+([A-Za-z0-9_]+)\s*;", source)


def relative_java_path(java_source_root: Path, source_file: Path) -> str:
    return source_file.relative_to(java_source_root).as_posix()


def extract_sql_block(schema_sql: str, table_name: str) -> str:
    escaped = re.escape(table_name)
    pattern = (
        rf"-- ----------------------------\r?\n"
        rf"-- Table structure for {escaped}\r?\n"
        rf"-- ----------------------------\r?\n"
        rf"DROP TABLE IF EXISTS `{escaped}`;\r?\n"
        rf"CREATE TABLE `{escaped}`.*?;\r?\n"
    )
    match = re.search(pattern, schema_sql, re.DOTALL)
    if not match:
        raise CodegenError(f"Unable to locate SQL block for table {table_name}")
    return match.group(0).strip()


@dataclass(frozen=True)
class EmittedArtifact:
    emitter: str
    layer: str
    source: Path
    destination: Path

    def as_record(self, java_source_root: Path, output_root: Path) -> dict[str, Any]:
        return {
            "emitter": self.emitter,
            "layer": self.layer,
            "source_file": str(self.source),
            "relative_java_path": relative_java_path(java_source_root, self.source),
            "output_file": str(self.destination),
            "output_relative_path": self.destination.relative_to(output_root).as_posix(),
        }


class CodegenContext:
    def __init__(
        self,
        project_root: Path,
        backend_root: Path,
        output_root: Path,
        module_spec: dict[str, Any],
        resolved_schema: dict[str, Any],
    ) -> None:
        self.project_root = project_root
        self.backend_root = backend_root
        self.output_root = output_root
        self.module_spec = module_spec
        self.resolved_schema = resolved_schema

        self.package_root = resolved_schema["module_identity"]["package_root"]
        self.package_path = package_to_path(self.package_root)
        self.java_source_root = backend_root / "src" / "main" / "java"
        self.resource_root = backend_root / "src" / "main" / "resources"
        self.module_source_root = self.java_source_root / self.package_path
        self.generated_java_root = output_root / "src" / "main" / "java"
        self.generated_resource_root = output_root / "src" / "main" / "resources"

        if not self.module_source_root.exists():
            raise CodegenError(f"Module source root does not exist: {self.module_source_root}")

        self.capabilities = list(self.resolved_schema.get("normalized_capabilities", []))
        self.capabilities_by_resource: dict[str, list[dict[str, Any]]] = {}
        for capability in self.capabilities:
            resource = capability.get("route_binding", {}).get("resource")
            if resource:
                self.capabilities_by_resource.setdefault(resource, []).append(capability)

        self.api_group_routes = {
            group["aggregate"]: group["route_prefix"]
            for group in self.module_spec.get("api_groups", [])
        }
        self.resource_route_roots = {
            "DictionaryTypeResource": self.module_spec.get("module_identity", {})
            .get("route_namespace", {})
            .get("dictionary_type"),
            "DictionaryDataResource": self.module_spec.get("module_identity", {})
            .get("route_namespace", {})
            .get("dictionary_data"),
        }
        self.required_tables = list(
            self.resolved_schema.get("integration_points", {})
            .get("persistence", {})
            .get("required_tables", [])
        )
        self.audit_titles = (
            self.module_spec.get("audit_behavior", {})
            .get("operate_log", {})
            .get("titles", {})
        )

    def discover_layer_files(self, relative_dirs: list[str]) -> list[Path]:
        files: list[Path] = []
        for relative_dir in relative_dirs:
            directory = self.module_source_root / Path(relative_dir)
            if not directory.exists():
                continue
            files.extend(sorted(directory.rglob("*.java")))
        return sorted(files, key=lambda item: item.relative_to(self.java_source_root).as_posix())

    def emit_source_files(self, emitter: str, layer: str, source_files: list[Path]) -> list[EmittedArtifact]:
        emitted: list[EmittedArtifact] = []
        for source_file in source_files:
            destination = self.generated_java_root / source_file.relative_to(self.java_source_root)
            copy_file(source_file, destination)
            emitted.append(EmittedArtifact(emitter, layer, source_file, destination))
        return emitted
