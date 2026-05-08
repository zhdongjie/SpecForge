from __future__ import annotations

from typing import Any

from .common import (
    CodegenContext,
    parse_operate_log_titles,
    parse_preauthorize_values,
    parse_request_mapping,
    read_text,
)


class ControllerEmitter:
    emitter_name = "controller-emitter"

    def emit(self, context: CodegenContext) -> dict[str, Any]:
        source_files = context.discover_layer_files(["type/resource", "data/resource"])
        emitted = context.emit_source_files(self.emitter_name, "controller", source_files)

        resource_bindings: dict[str, dict[str, Any]] = {}
        for artifact in emitted:
            source = read_text(artifact.destination)
            resource_name = artifact.destination.stem
            resource_bindings[resource_name] = {
                "request_mapping": parse_request_mapping(source),
                "authorities": sorted(parse_preauthorize_values(source)),
                "operate_log_titles": sorted(parse_operate_log_titles(source)),
                "capability_count": len(context.capabilities_by_resource.get(resource_name, [])),
            }

        return {
            "emitter": self.emitter_name,
            "layer": "controller",
            "artifact_count": len(emitted),
            "artifacts": [artifact.as_record(context.java_source_root, context.output_root) for artifact in emitted],
            "resource_bindings": resource_bindings,
        }
