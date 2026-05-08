from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PackageStructure:
    module_package: str
    platform_package: str
    application_package: str
    application_class: str
    artifact_id: str
    project_name: str


class PackageStructureResolver:
    def resolve(self, field_schema: dict[str, Any]) -> PackageStructure:
        module_package = field_schema["module"]["package_root"]
        segments = module_package.split(".")
        platform_index = segments.index("system") if "system" in segments else max(len(segments) - 1, 1)
        platform_package = ".".join(segments[:platform_index])
        if not platform_package:
            platform_package = module_package
        project_name = field_schema["module"]["name"]
        artifact_id = f"{project_name}-backend"
        return PackageStructure(
            module_package=module_package,
            platform_package=platform_package,
            application_package=platform_package,
            application_class="BackendApplication",
            artifact_id=artifact_id,
            project_name=project_name,
        )
