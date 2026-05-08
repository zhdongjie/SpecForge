from __future__ import annotations

from typing import Any


class Validator:
    def __init__(self, task_graph: dict[str, Any], resolved_schema: dict[str, Any]) -> None:
        self.task_graph = task_graph
        self.resolved_schema = resolved_schema
        self.allowed_package_roots = task_graph.get("architecture_boundary_enforcement", {}).get(
            "allowed_package_roots", []
        )
        self.module_identity = resolved_schema.get("module_identity", {})
        self.code_conventions = (
            resolved_schema.get("architectural_bindings", {}).get("code_conventions", {})
        )

    def run(
        self,
        task: dict[str, Any],
        planned_artifacts: list[dict[str, Any]],
        dependency_status_ok: bool,
    ) -> dict[str, Any]:
        hooks = []
        hooks.append(self._dependency_check(dependency_status_ok))
        hooks.append(self._naming_check(planned_artifacts))
        hooks.append(self._business_domain_check())
        hooks.append(self._architecture_boundary_check(planned_artifacts))
        overall = "PASS" if all(hook["status"] == "PASS" for hook in hooks) else "FAIL"
        return {"overall_status": overall, "hooks": hooks}

    def _dependency_check(self, dependency_status_ok: bool) -> dict[str, Any]:
        return {
            "hook": "dependency_check",
            "status": "PASS" if dependency_status_ok else "FAIL",
            "details": "All upstream dependencies succeeded"
            if dependency_status_ok
            else "One or more upstream dependencies did not succeed",
        }

    def _naming_check(self, planned_artifacts: list[dict[str, Any]]) -> dict[str, Any]:
        suffix_map = {
            "resource": self.code_conventions.get("resource_suffix", "Resource"),
            "manager": self.code_conventions.get("manager_suffix", "Manager"),
            "service": self.code_conventions.get("service_suffix", "Service"),
            "service_impl": self.code_conventions.get("service_impl_suffix", "ServiceImpl"),
            "mapper": self.code_conventions.get("mapper_suffix", "Mapper"),
            "entity": self.code_conventions.get("entity_suffix", "Entity"),
        }
        invalid: list[str] = []
        for artifact in planned_artifacts:
            kind = artifact["artifact_kind"]
            expected_suffix = suffix_map.get(kind)
            if expected_suffix and not artifact["artifact_name"].endswith(expected_suffix):
                invalid.append(artifact["artifact_name"])
        return {
            "hook": "naming_check",
            "status": "PASS" if not invalid else "FAIL",
            "details": "Naming conventions matched"
            if not invalid
            else f"Artifacts with unexpected naming: {', '.join(invalid)}",
        }

    def _architecture_boundary_check(self, planned_artifacts: list[dict[str, Any]]) -> dict[str, Any]:
        invalid = [
            artifact["package_root"]
            for artifact in planned_artifacts
            if not any(artifact["package_root"].startswith(root) for root in self.allowed_package_roots)
        ]
        return {
            "hook": "architecture_boundary_check",
            "status": "PASS" if not invalid else "FAIL",
            "details": "Artifact package roots stayed within allowed module boundary"
            if not invalid
            else f"Artifacts escaped boundary: {', '.join(sorted(set(invalid)))}",
        }

    def _business_domain_check(self) -> dict[str, Any]:
        semantic_role = self.module_identity.get("semantic_role", "")
        package_root = self.module_identity.get("package_root", "")
        if semantic_role != "business-domain":
            return {
                "hook": "business_domain_check",
                "status": "PASS",
                "details": "Module is not a business-domain module",
            }
        if package_root.startswith("org.eu.originalkeen.business."):
            return {
                "hook": "business_domain_check",
                "status": "PASS",
                "details": "Business-domain module package root is constrained to business/*",
            }
        return {
            "hook": "business_domain_check",
            "status": "FAIL",
            "details": f"Business-domain module must use org.eu.originalkeen.business.* package root, got {package_root}",
        }
