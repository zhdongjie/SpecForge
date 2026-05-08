from __future__ import annotations

from pathlib import Path
from typing import Any

from runtime.codegen.common import dump_yaml, safe_load_yaml

from .application_yaml_synthesizer import ApplicationYamlSynthesizer
from .audit_synthesizer import AuditSynthesizer
from .auth_context_synthesizer import AuthContextSynthesizer
from .base_entity_synthesizer import BaseEntitySynthesizer
from .bootstrap_synthesizer import BootstrapSynthesizer
from .datasource_synthesizer import DatasourceSynthesizer
from .exception_handler_synthesizer import ExceptionHandlerSynthesizer
from .jwt_synthesizer import JwtSynthesizer
from .operation_log_synthesizer import OperationLogSynthesizer
from .package_structure_resolver import PackageStructureResolver
from .pagination_synthesizer import PaginationSynthesizer
from .permission_infrastructure_synthesizer import PermissionInfrastructureSynthesizer
from .pom_synthesizer import PomSynthesizer
from .redis_synthesizer import RedisSynthesizer
from .response_wrapper_synthesizer import ResponseWrapperSynthesizer
from .security_synthesizer import SecuritySynthesizer


class PlatformPipeline:
    def __init__(self, output_root: Path, run_root: Path, backend_root: Path) -> None:
        self.output_root = output_root
        self.run_root = run_root
        self.backend_root = backend_root

    def run(self, field_schema_path: Path) -> dict[str, Any]:
        field_schema = safe_load_yaml(field_schema_path)
        package_structure = PackageStructureResolver().resolve(field_schema)
        platform_schema = self._build_platform_schema(field_schema, package_structure)
        generated_ir_root = self.run_root / "generated-ir"
        dump_yaml(generated_ir_root / "platform-schema.generated.yaml", platform_schema)

        context = {
            "output_root": self.output_root,
            "run_root": self.run_root,
            "backend_root": self.backend_root,
            "field_schema": field_schema,
            "platform_schema": platform_schema,
            "platform_package": package_structure.platform_package,
            "application_package": package_structure.application_package,
            "application_class": package_structure.application_class,
            "artifact_id": package_structure.artifact_id,
            "project_name": package_structure.project_name,
        }

        emitters = [
            ("bootstrap-synthesizer", BootstrapSynthesizer().emit(context)),
            ("pom-synthesizer", PomSynthesizer().emit(context)),
            ("application-yaml-synthesizer", ApplicationYamlSynthesizer().emit(context)),
            ("security-synthesizer", SecuritySynthesizer().emit(context)),
            ("jwt-synthesizer", JwtSynthesizer().emit(context)),
            ("auth-context-synthesizer", AuthContextSynthesizer().emit(context)),
            ("permission-infrastructure-synthesizer", PermissionInfrastructureSynthesizer().emit(context)),
            ("response-wrapper-synthesizer", ResponseWrapperSynthesizer().emit(context)),
            ("pagination-synthesizer", PaginationSynthesizer().emit(context)),
            ("exception-handler-synthesizer", ExceptionHandlerSynthesizer().emit(context)),
            ("base-entity-synthesizer", BaseEntitySynthesizer().emit(context)),
            ("audit-synthesizer", AuditSynthesizer().emit(context)),
            ("operation-log-synthesizer", OperationLogSynthesizer().emit(context)),
            ("datasource-synthesizer", DatasourceSynthesizer().emit(context)),
            ("redis-synthesizer", RedisSynthesizer().emit(context)),
        ]

        manifest = {
            "status": "PASS",
            "artifact_count": sum(item["artifact_count"] for _, item in emitters),
            "emitters": [{"emitter": name, **result} for name, result in emitters],
            "platform_schema_path": str(generated_ir_root / "platform-schema.generated.yaml"),
        }
        dump_yaml(self.output_root / "logs" / "platform-report.yaml", manifest)
        return {
            "status": "PASS",
            "field_schema": field_schema,
            "platform_schema": platform_schema,
            "manifest": manifest,
        }

    def _build_platform_schema(self, field_schema: dict[str, Any], package_structure: Any) -> dict[str, Any]:
        architecture_contract = field_schema.get("architecture_contract", {})
        return {
            "platform": {
                "package_root": package_structure.platform_package,
                "application_package": package_structure.application_package,
                "application_class": package_structure.application_class,
                "artifact_id": package_structure.artifact_id,
                "project_name": package_structure.project_name,
            },
            "security": {
                "auth_type": "jwt",
                "authority_model": "centralized",
                "token": {
                    "access_expire_minutes": 120,
                    "refresh_expire_days": 7,
                },
            },
            "pagination": {
                "request_fields": ["currentPage", "pageSize"],
            },
            "response_wrapper": {
                "enabled": True,
                "type": architecture_contract.get("response_wrapper", "ResponseVo"),
            },
            "audit": {
                "operation_log": True,
                "access_log": True,
            },
            "database": {
                "type": field_schema["module"].get("database", "mysql"),
            },
            "redis": {
                "enabled": True,
            },
            "code_style": {
                "layering": ["resource", "manager", "service", "mapper", "entity"],
            },
            "generation_contracts": [
                "centralized_security",
                "unified_response_structure",
                "deterministic_package_layout",
                "audit_consistency",
                "compile_viability",
            ],
        }
