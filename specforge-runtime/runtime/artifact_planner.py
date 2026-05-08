from __future__ import annotations

from pathlib import Path
from typing import Any


class ArtifactPlanner:
    OPERATION_TO_UNIT_KIND = {
        "domain-artifact-generation": "domain",
        "persistence-binding-generation": "persistence",
        "service-orchestration-generation": "service-layer",
        "resource-layer-generation": "resource-layer",
    }

    CATEGORY_PACKAGE_SUFFIX = {
        "resource": "",
        "manager": "",
        "service": "",
        "service_impl": ".impl",
        "mapper": "",
        "entity": ".domain.entity",
        "dto": ".domain.dto",
        "vo": ".domain.vo",
        "bo": ".domain.bo",
    }

    def __init__(self, resolved_schema: dict[str, Any], artifacts_dir: Path) -> None:
        self.resolved_schema = resolved_schema
        self.artifacts_dir = artifacts_dir
        self.generation_units = resolved_schema.get("generation_units", [])
        self.package_root = resolved_schema.get("module_identity", {}).get("package_root", "")
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

    def plan_for_task(self, task: dict[str, Any]) -> list[dict[str, Any]]:
        operation = task.get("semantic_operation")
        unit_kind = self.OPERATION_TO_UNIT_KIND.get(operation)
        if unit_kind is None:
            return []
        matched_unit = self._match_generation_unit(task["task_id"], unit_kind)
        if matched_unit is None:
            return []
        produced = matched_unit.get("produces", [])
        planned: list[dict[str, Any]] = []
        for artifact_name in produced:
            artifact_kind = self._infer_artifact_kind(artifact_name)
            package_root = self._artifact_package_root(task["task_id"], artifact_kind)
            file_name = self._artifact_file_name(artifact_name, artifact_kind)
            planned.append(
                {
                    "artifact_name": artifact_name,
                    "artifact_file_name": file_name,
                    "artifact_kind": artifact_kind,
                    "package_root": package_root,
                    "unit_id": matched_unit["unit_id"],
                    "planned_path": str(self.artifacts_dir / file_name),
                }
            )
        return planned

    def materialize(self, planned_artifacts: list[dict[str, Any]], task_id: str) -> None:
        for artifact in planned_artifacts:
            path = Path(artifact["planned_path"])
            content = [
                f"// planned by SpecForge runtime simulation",
                f"// task_id: {task_id}",
                f"// artifact_kind: {artifact['artifact_kind']}",
                f"// package_root: {artifact['package_root']}",
                f"// artifact_name: {artifact['artifact_name']}",
                f"// artifact_file_name: {artifact['artifact_file_name']}",
                "",
            ]
            path.write_text("\n".join(content), encoding="utf-8")

    def _match_generation_unit(self, task_id: str, unit_kind: str) -> dict[str, Any] | None:
        scope_hint = "DictionaryType" if "dictionary-type" in task_id else "DictionaryData" if "dictionary-data" in task_id else None
        for unit in self.generation_units:
            if unit.get("kind") != unit_kind:
                continue
            if scope_hint and unit.get("scope") != scope_hint:
                continue
            return unit
        return None

    def _infer_artifact_kind(self, artifact_name: str) -> str:
        if artifact_name.endswith("Resource"):
            return "resource"
        if artifact_name.endswith("Manager"):
            return "manager"
        if artifact_name.endswith("ServiceImpl"):
            return "service_impl"
        if artifact_name.endswith("Service"):
            return "service"
        if artifact_name.endswith("Mapper"):
            return "mapper"
        if artifact_name.endswith("Entity"):
            return "entity"
        if artifact_name.endswith("Dto"):
            return "dto"
        if artifact_name.endswith("Vo"):
            return "vo"
        if artifact_name.endswith("Bo"):
            return "bo"
        return "unknown"

    def _artifact_package_root(self, task_id: str, artifact_kind: str) -> str:
        segment = ".type" if "dictionary-type" in task_id else ".data" if "dictionary-data" in task_id else ""
        suffix = self.CATEGORY_PACKAGE_SUFFIX.get(artifact_kind, "")
        if artifact_kind in {"resource", "manager", "service", "mapper"}:
            suffix = f".{artifact_kind}" if artifact_kind != "service" else ".service"
        if artifact_kind == "service_impl":
            suffix = ".service.impl"
        return f"{self.package_root}{segment}{suffix}"

    def _artifact_file_name(self, artifact_name: str, artifact_kind: str) -> str:
        if artifact_kind == "unknown" or artifact_name.endswith(".java"):
            return artifact_name
        return f"{artifact_name}.java"
