from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from runtime.codegen.common import dump_yaml, extract_sql_block, read_text, safe_load_yaml, write_text

from .artifact_graph_mutator import ArtifactGraphMutator
from .dto_mutator import DtoMutator
from .entity_mutator import EntityMutator
from .mutation_diff import MutationDiffBuilder
from .mutation_validator import MutationValidator
from .naming_transformer import NamingTransformer
from .permission_mutator import PermissionMutator
from .route_mutator import RouteMutator
from .semantic_rewriter import SemanticRewriter
from .sql_mutator import SqlMutator


@dataclass(frozen=True)
class MutationArtifact:
    source_file: Path
    destination_file: Path
    source_relative_path: str
    destination_relative_path: str
    layer: str


class MutationEngine:
    def __init__(
        self,
        project_root: Path,
        backend_root: Path,
        output_root: Path,
        specs_dir: Path,
        mutation_spec_path: Path | None = None,
    ) -> None:
        self.project_root = project_root
        self.backend_root = backend_root
        self.output_root = output_root
        self.specs_dir = specs_dir
        self.mutation_spec_path = mutation_spec_path or (specs_dir / "mutation-spec.yaml")

    def run(self, verify_compile: bool = False) -> dict[str, Any]:
        module_spec = safe_load_yaml(self.specs_dir / "module-spec.yaml")
        resolved_schema = safe_load_yaml(self.specs_dir / "module-schema.resolved.yaml")
        mutation_spec = safe_load_yaml(self.mutation_spec_path)
        naming_transformer = NamingTransformer(module_spec, resolved_schema, mutation_spec)
        rewriter = SemanticRewriter(naming_transformer)
        graph_mutator = ArtifactGraphMutator(naming_transformer)
        entity_mutator = EntityMutator(rewriter)
        route_mutator = RouteMutator(rewriter)
        permission_mutator = PermissionMutator(rewriter)
        dto_mutator = DtoMutator(rewriter)
        sql_mutator = SqlMutator(rewriter)

        source_root = self.backend_root / "src" / "main" / "java" / Path(*naming_transformer.source_package_root.split("."))
        destination_root = self.output_root / "src" / "main" / "java"
        artifact_records: list[dict[str, Any]] = []

        for source_file in sorted(source_root.rglob("*.java")):
            original = read_text(source_file)
            rewritten, layer = self._rewrite_source(
                original,
                source_file,
                entity_mutator,
                route_mutator,
                permission_mutator,
                dto_mutator,
            )
            destination_file, path_record = graph_mutator.rewrite_path(
                self.backend_root / "src" / "main" / "java",
                source_file,
                destination_root,
            )
            write_text(destination_file, rewritten)
            artifact_records.append(
                {
                    **path_record,
                    "layer": layer,
                    "source_file": str(source_file),
                    "destination_file": str(destination_file),
                }
            )

        sql_source = self.backend_root / "src" / "main" / "resources" / "sql" / "schema.sql"
        sql_destination = self.output_root / "src" / "main" / "resources" / "sql" / f"{mutation_spec['target_module']['name']}.sql"
        schema_sql = read_text(sql_source)
        source_tables = list(mutation_spec.get("semantic_mutations", {}).get("tables", {}).keys())
        module_sql = "SET NAMES utf8mb4;\nSET FOREIGN_KEY_CHECKS = 0;\n\n"
        module_sql += "\n\n".join(extract_sql_block(schema_sql, table_name) for table_name in source_tables)
        module_sql += "\n\nSET FOREIGN_KEY_CHECKS = 1;\n"
        sql_rewritten, _ = sql_mutator.mutate(module_sql)
        write_text(sql_destination, sql_rewritten)

        mutation_plan = {
            "source_module": mutation_spec["source_module"],
            "target_module": mutation_spec["target_module"],
            "naming": naming_transformer.mapping_report(),
            "artifact_count": len(artifact_records),
        }
        dump_yaml(self.output_root / "logs" / "mutation-plan.yaml", mutation_plan)

        validator = MutationValidator(self.backend_root, self.output_root, naming_transformer)
        validation_report = validator.validate()
        compile_report = validator.compile_check() if verify_compile else {"status": "SKIPPED"}

        diff_builder = MutationDiffBuilder()
        diff_report = diff_builder.build(mutation_spec, artifact_records, validation_report, compile_report)
        dump_yaml(self.output_root / "logs" / "mutation-diff.yaml", diff_report)

        mutation_report = {
            "source_module": mutation_spec["source_module"],
            "target_module": mutation_spec["target_module"]["name"],
            "status": "PASS" if validation_report["status"] == "PASS" and compile_report["status"] != "FAIL" else "FAIL",
            "output_root": str(self.output_root),
            "artifact_count": len(artifact_records),
            "validation_status": validation_report["status"],
            "compile_verification_status": compile_report["status"],
            "preserved_invariants": diff_report["preserved_invariants"],
        }
        dump_yaml(self.output_root / "logs" / "mutation-report.yaml", mutation_report)
        return mutation_report

    def _rewrite_source(
        self,
        original: str,
        source_file: Path,
        entity_mutator: EntityMutator,
        route_mutator: RouteMutator,
        permission_mutator: PermissionMutator,
        dto_mutator: DtoMutator,
    ) -> tuple[str, str]:
        rewritten = original
        relative = source_file.as_posix()
        if "/domain/entity/" in relative:
            rewritten, _ = entity_mutator.mutate(rewritten)
            return rewritten, "entity"
        if "/resource/" in relative:
            rewritten, _ = route_mutator.mutate(rewritten)
            rewritten, _ = permission_mutator.mutate(rewritten)
            return rewritten, "resource"
        if "/domain/dto/" in relative or "/domain/vo/" in relative or "/domain/bo/" in relative:
            rewritten, _ = dto_mutator.mutate(rewritten)
            return rewritten, "domain"
        rewritten, _ = entity_mutator.mutate(rewritten)
        return rewritten, "service"
