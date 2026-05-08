from __future__ import annotations

from typing import Any

from .common import CodegenContext, read_text


class MapperEmitter:
    emitter_name = "mapper-emitter"

    def emit(self, context: CodegenContext) -> dict[str, Any]:
        source_files = context.discover_layer_files(["type/mapper", "data/mapper"])
        emitted = context.emit_source_files(self.emitter_name, "mapper", source_files)

        mapper_contracts: dict[str, str] = {}
        for artifact in emitted:
            source = read_text(artifact.destination)
            mapper_contracts[artifact.destination.stem] = "BaseMapper" if "BaseMapper<" in source else "unknown"

        return {
            "emitter": self.emitter_name,
            "layer": "mapper",
            "artifact_count": len(emitted),
            "artifacts": [artifact.as_record(context.java_source_root, context.output_root) for artifact in emitted],
            "mapper_contracts": mapper_contracts,
        }
