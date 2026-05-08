from __future__ import annotations

from typing import Any

from .common import CodegenContext, java_private_fields, parse_table_name, read_text


class EntityEmitter:
    emitter_name = "entity-emitter"

    def emit(self, context: CodegenContext) -> dict[str, Any]:
        source_files = context.discover_layer_files(["type/domain/entity", "data/domain/entity"])
        emitted = context.emit_source_files(self.emitter_name, "entity", source_files)

        entity_tables: dict[str, str] = {}
        entity_fields: dict[str, list[str]] = {}
        for artifact in emitted:
            source = read_text(artifact.destination)
            class_name = artifact.destination.stem
            table_name = parse_table_name(source)
            if table_name:
                entity_tables[class_name] = table_name
            entity_fields[class_name] = java_private_fields(source)

        return {
            "emitter": self.emitter_name,
            "layer": "entity",
            "artifact_count": len(emitted),
            "artifacts": [artifact.as_record(context.java_source_root, context.output_root) for artifact in emitted],
            "entity_tables": entity_tables,
            "entity_fields": entity_fields,
        }
