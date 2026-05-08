from __future__ import annotations

from typing import Any

from .common import CodegenContext


class DtoEmitter:
    emitter_name = "dto-emitter"

    def emit(self, context: CodegenContext) -> dict[str, Any]:
        source_files = context.discover_layer_files(
            [
                "type/domain/dto",
                "type/domain/vo",
                "type/domain/bo",
                "data/domain/dto",
                "data/domain/vo",
                "data/domain/bo",
            ]
        )
        emitted = context.emit_source_files(self.emitter_name, "dto", source_files)
        groups = {
            "dto": [],
            "vo": [],
            "bo": [],
        }
        for artifact in emitted:
            relative_path = artifact.destination.relative_to(context.generated_java_root).as_posix()
            if "/domain/dto/" in relative_path:
                groups["dto"].append(artifact.destination.stem)
            elif "/domain/vo/" in relative_path:
                groups["vo"].append(artifact.destination.stem)
            elif "/domain/bo/" in relative_path:
                groups["bo"].append(artifact.destination.stem)

        for key in groups:
            groups[key] = sorted(groups[key])

        return {
            "emitter": self.emitter_name,
            "layer": "dto",
            "artifact_count": len(emitted),
            "artifacts": [artifact.as_record(context.java_source_root, context.output_root) for artifact in emitted],
            "groups": groups,
        }
