from __future__ import annotations

from pathlib import Path
from typing import Any

from runtime.codegen.common import write_text


class SqlSynthesizer:
    def emit(self, context: dict[str, Any]) -> dict[str, Any]:
        sql_blocks: list[str] = ["SET NAMES utf8mb4;", "SET FOREIGN_KEY_CHECKS = 0;", ""]
        tables: list[str] = []
        for entity_name, entity_spec in sorted(context["schema"].get("entities", {}).items()):
            tables.append(entity_spec["table"])
            sql_blocks.append(self._table_block(context, entity_name, entity_spec))
            sql_blocks.append("")
        sql_blocks.append("SET FOREIGN_KEY_CHECKS = 1;")
        destination = (
            context["output_root"]
            / "src"
            / "main"
            / "resources"
            / "sql"
            / f"{context['schema']['module']['name']}.generated.sql"
        )
        write_text(destination, "\n".join(sql_blocks))
        return {"artifact_count": 1, "artifacts": [str(destination)], "tables": tables}

    def _table_block(self, context: dict[str, Any], entity_name: str, entity_spec: dict[str, Any]) -> str:
        columns = [
            "  `id` BIGINT NOT NULL,",
        ]
        for field in entity_spec.get("fields", []):
            if field.get("primary_key"):
                continue
            column_name = context["naming"].to_snake_case(field["name"])
            sql_type = context["field_type_system"].sql_column_type(field)
            nullable = "NOT NULL" if field.get("required") else "DEFAULT NULL"
            unique = " UNIQUE" if field.get("unique") else ""
            columns.append(f"  `{column_name}` {sql_type} {nullable}{unique},")
        columns.extend(
            [
                "  `created_time` DATETIME DEFAULT NULL,",
                "  `created_by` BIGINT DEFAULT NULL,",
                "  `last_modified_time` DATETIME DEFAULT NULL,",
                "  `last_modified_by` BIGINT DEFAULT NULL,",
                "  `deleted` TINYINT(1) NOT NULL DEFAULT 0,",
                "  PRIMARY KEY (`id`)",
            ]
        )
        for relation in context["relations"].get(entity_name, []):
            if relation["type"] == "many_to_one":
                constraint_name = f"fk_{entity_spec['table']}_{relation['target_table']}"
                columns.append(
                    f",  CONSTRAINT `{constraint_name}` FOREIGN KEY (`{context['naming'].to_snake_case(relation['self_field'])}`) REFERENCES `{relation['target_table']}` (`{context['naming'].to_snake_case(relation['target_field'])}`)"
                )
        return (
            f"-- ----------------------------\n"
            f"-- Table structure for {entity_spec['table']}\n"
            f"-- ----------------------------\n"
            f"DROP TABLE IF EXISTS `{entity_spec['table']}`;\n"
            f"CREATE TABLE `{entity_spec['table']}` (\n"
            f"{chr(10).join(columns)}\n"
            f") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;\n"
        )
