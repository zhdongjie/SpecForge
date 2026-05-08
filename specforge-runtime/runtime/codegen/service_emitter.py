from __future__ import annotations

from typing import Any

from .common import CodegenContext


class ServiceEmitter:
    emitter_name = "service-emitter"

    def emit(self, context: CodegenContext) -> dict[str, Any]:
        source_files = context.discover_layer_files(
            [
                "type/service",
                "type/service/impl",
                "type/manager",
                "data/service",
                "data/service/impl",
                "data/manager",
            ]
        )
        emitted = context.emit_source_files(self.emitter_name, "service", source_files)
        groups = {
            "service": [],
            "service_impl": [],
            "manager": [],
        }
        for artifact in emitted:
            relative_path = artifact.destination.relative_to(context.generated_java_root).as_posix()
            if "/service/impl/" in relative_path:
                groups["service_impl"].append(artifact.destination.stem)
            elif "/service/" in relative_path:
                groups["service"].append(artifact.destination.stem)
            elif "/manager/" in relative_path:
                groups["manager"].append(artifact.destination.stem)

        for key in groups:
            groups[key] = sorted(groups[key])

        return {
            "emitter": self.emitter_name,
            "layer": "service",
            "artifact_count": len(emitted),
            "artifacts": [artifact.as_record(context.java_source_root, context.output_root) for artifact in emitted],
            "groups": groups,
        }
