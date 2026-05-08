from __future__ import annotations

from typing import Any

from .common import CodegenContext, extract_sql_block, read_text, write_text


class SqlEmitter:
    emitter_name = "sql-emitter"

    def emit(self, context: CodegenContext) -> dict[str, Any]:
        schema_path = context.resource_root / "sql" / "schema.sql"
        schema_sql = read_text(schema_path)
        blocks = [extract_sql_block(schema_sql, table_name) for table_name in context.required_tables]
        content = "SET NAMES utf8mb4;\nSET FOREIGN_KEY_CHECKS = 0;\n\n"
        content += "\n\n".join(blocks)
        content += "\n\nSET FOREIGN_KEY_CHECKS = 1;\n"
        destination = context.generated_resource_root / "sql" / "dictionary-management.generated.sql"
        write_text(destination, content)

        return {
            "emitter": self.emitter_name,
            "layer": "sql",
            "artifact_count": len(context.required_tables),
            "artifacts": [
                {
                    "emitter": self.emitter_name,
                    "layer": "sql",
                    "source_file": str(schema_path),
                    "output_file": str(destination),
                    "output_relative_path": destination.relative_to(context.output_root).as_posix(),
                }
            ],
            "tables": list(context.required_tables),
        }
