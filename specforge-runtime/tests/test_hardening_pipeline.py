from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.codegen.common import dump_yaml
from runtime.hardening.compile_error_classifier import CompileErrorClassifier
from runtime.hardening.compile_repair_engine import CompileRepairEngine
from runtime.hardening.hardening_pipeline import HardeningPipeline
from runtime.hardening.project_health_reporter import ProjectHealthReporter
from runtime.replay import load_yaml

SPECS_DIR = ROOT / "specs"
BACKEND_ROOT = ROOT.parent / "backend"


class CompileErrorClassifierTests(unittest.TestCase):
    def test_classifier_detects_real_generated_failure_patterns(self) -> None:
        output = """
[ERROR] E:/Project/Generate/SpecForge/specforge-runtime/runs/backend-compiler-smoke/generated-project/src/main/java/org/eu/originalkeen/system/dictionary/resource/DictionaryTypeResource.java:[32,86] cannot find symbol
[ERROR]   symbol:   variable SYSTEM_DICTIONARY-TYPE_CREATE
[ERROR]   location: class org.eu.originalkeen.system.dictionary.constant.DictionaryManagementPermissionConstant
[ERROR] E:/Project/Generate/SpecForge/specforge-runtime/runs/backend-compiler-smoke/generated-project/src/main/java/org/eu/originalkeen/system/dictionary/domain/dto/EnquiryDictionaryDataPageDto.java:[11,1] constructor EnquiryDictionaryDataPageDto in class org.eu.originalkeen.system.dictionary.domain.dto.EnquiryDictionaryDataPageDto cannot be applied to given types;
"""
        findings = CompileErrorClassifier().classify(output)
        categories = {item["category"] for item in findings}
        self.assertIn("unresolved_symbol", categories)
        self.assertIn("duplicate_constructor", categories)


class CompileRepairEngineTests(unittest.TestCase):
    def test_compile_repair_engine_normalizes_permission_constants_and_empty_query_dto(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            logs_root = project_root / "logs"
            resource_path = project_root / "src" / "main" / "java" / "demo" / "DictionaryTypeResource.java"
            dto_path = project_root / "src" / "main" / "java" / "demo" / "EnquiryDictionaryDataPageDto.java"
            resource_path.parent.mkdir(parents=True, exist_ok=True)
            resource_path.write_text(
                '@PreAuthorize("hasAuthority(\'" + Permission.SYSTEM_DICTIONARY-TYPE_CREATE + "\')")\n',
                encoding="utf-8",
            )
            dto_path.write_text(
                "import lombok.AllArgsConstructor;\n"
                "import lombok.NoArgsConstructor;\n"
                "@NoArgsConstructor\n"
                "@AllArgsConstructor\n"
                "public class EnquiryDictionaryDataPageDto extends EnquiryPageDto {\n"
                "    private static final long serialVersionUID = 1L;\n"
                "}\n",
                encoding="utf-8",
            )
            diagnostics = {
                "compile_errors": [
                    {"category": "unresolved_symbol", "file": str(resource_path), "symbol": "SYSTEM_DICTIONARY-TYPE_CREATE"},
                    {"category": "duplicate_constructor", "file": str(dto_path)},
                ]
            }
            report = CompileRepairEngine(project_root, logs_root).apply(diagnostics)
            self.assertEqual(report["status"], "PASS")
            self.assertIn("SYSTEM_DICTIONARY_TYPE_CREATE", resource_path.read_text(encoding="utf-8"))
            self.assertNotIn("@AllArgsConstructor", dto_path.read_text(encoding="utf-8"))
            self.assertTrue((logs_root / "compile-repair-report.yaml").exists())
            self.assertTrue((logs_root / "dependency-resolution-report.yaml").exists())


    def test_compile_repair_engine_normalizes_mybatis_flex_table_def_suffix_alignment(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            logs_root = project_root / "logs"
            table_def_path = project_root / "target" / "generated-sources" / "annotations" / "org" / "eu" / "originalkeen" / "business" / "role" / "domain" / "entity" / "table" / "RoleEntityTableDef.java"
            source_path = project_root / "src" / "main" / "java" / "org" / "eu" / "originalkeen" / "business" / "role" / "resource" / "RoleResource.java"
            table_def_path.parent.mkdir(parents=True, exist_ok=True)
            source_path.parent.mkdir(parents=True, exist_ok=True)
            table_def_path.write_text(
                "public class RoleEntityTableDef {\n"
                "    public static final RoleEntityTableDef ROLE_ENTITY = new RoleEntityTableDef();\n"
                "    public final QueryColumn ID = new QueryColumn();\n"
                "    public final QueryColumn ROLE_NAME = new QueryColumn();\n"
                "}\n",
                encoding="utf-8",
            )
            source_path.write_text(
                "import static org.eu.originalkeen.business.role.domain.entity.table.RoleTableDef.role;\n"
                "\n"
                "public class RoleResource {\n"
                "    private final String select = role.roleName.toString() + role.id.toString();\n"
                "}\n",
                encoding="utf-8",
            )

            repairs = CompileRepairEngine(project_root, logs_root).normalize_generated_table_def_imports()

            updated = source_path.read_text(encoding="utf-8")
            self.assertTrue(repairs)
            self.assertEqual(repairs[0]["repair_type"], "mybatis_flex_table_def_entity_suffix_alignment")
            self.assertIn("RoleEntityTableDef.ROLE_ENTITY", updated)
            self.assertIn("ROLE_ENTITY.ROLE_NAME", updated)
            self.assertIn("ROLE_ENTITY.ID", updated)


class ProjectHealthReporterTests(unittest.TestCase):
    def test_health_report_marks_unrepaired_compile_failures_as_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            logs_root = Path(temp_dir) / "logs"
            logs_root.mkdir(parents=True, exist_ok=True)

            report = ProjectHealthReporter(logs_root).write(
                compile_diagnostics={
                    "status": "FAIL",
                    "compile_errors": [
                        {"category": "unresolved_symbol"},
                        {"category": "duplicate_constructor"},
                    ],
                },
                compile_repair_report={
                    "status": "NO_ACTION",
                    "repairs": [],
                    "post_repair_status": "FAIL",
                },
                boot_diagnostics={
                    "status": "BLOCKED",
                    "boot_failures": [],
                    "reason": "compile_failed",
                },
                boot_repair_report={
                    "status": "SKIPPED",
                    "repairs": [],
                    "post_repair_status": "BLOCKED",
                },
                compile_repair_validation={"status": "PASS", "repair_count": 0},
                boot_repair_validation={"status": "PASS", "repair_count": 0},
                deterministic_validation={"status": "PASS"},
            )

            self.assertEqual(report["status"], "FAIL")
            self.assertEqual(report["compile_status"], "FAIL")
            self.assertEqual(report["compile_post_repair_status"], "FAIL")
            self.assertEqual(report["compile_error_count"], 2)
            self.assertEqual(report["boot_status"], "BLOCKED")
            self.assertEqual(report["boot_post_repair_status"], "BLOCKED")
            self.assertEqual(report["compile_repair_count"], 0)
            self.assertEqual(report["boot_repair_count"], 0)
            self.assertEqual(load_yaml(logs_root / "project-health-report.yaml"), report)

    def test_health_report_marks_boot_failures_as_fail_even_after_compile_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            logs_root = Path(temp_dir) / "logs"
            logs_root.mkdir(parents=True, exist_ok=True)

            report = ProjectHealthReporter(logs_root).write(
                compile_diagnostics={"status": "PASS", "compile_errors": []},
                compile_repair_report={
                    "status": "SKIPPED",
                    "repairs": [],
                    "post_repair_status": "PASS",
                },
                boot_diagnostics={
                    "status": "FAIL",
                    "boot_failures": [{"category": "port_conflict"}],
                },
                boot_repair_report={
                    "status": "NO_ACTION",
                    "repairs": [],
                    "post_repair_status": "FAIL",
                },
                compile_repair_validation={"status": "PASS", "repair_count": 0},
                boot_repair_validation={"status": "PASS", "repair_count": 0},
                deterministic_validation={"status": "PASS"},
            )

            self.assertEqual(report["status"], "FAIL")
            self.assertEqual(report["compile_status"], "PASS")
            self.assertEqual(report["boot_status"], "FAIL")
            self.assertEqual(report["boot_post_repair_status"], "FAIL")
            self.assertEqual(report["boot_failure_count"], 1)


class HardeningPipelineTests(unittest.TestCase):
    def test_hardening_pipeline_writes_reports_for_repairable_compile_failures(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_root = Path(temp_dir) / "hardening-run"
            generated_project_root = run_root / "generated-project"
            logs_root = generated_project_root / "logs"
            resource_path = generated_project_root / "src" / "main" / "java" / "demo" / "DictionaryTypeResource.java"
            dto_path = generated_project_root / "src" / "main" / "java" / "demo" / "EnquiryDictionaryDataPageDto.java"
            resource_path.parent.mkdir(parents=True, exist_ok=True)
            resource_path.write_text(
                '@PreAuthorize("hasAuthority(\'" + Permission.SYSTEM_DICTIONARY-TYPE_CREATE + "\')")\n',
                encoding="utf-8",
            )
            dto_path.write_text(
                "import lombok.AllArgsConstructor;\n"
                "import lombok.NoArgsConstructor;\n"
                "@NoArgsConstructor\n"
                "@AllArgsConstructor\n"
                "public class EnquiryDictionaryDataPageDto extends EnquiryPageDto {\n"
                "    private static final long serialVersionUID = 1L;\n"
                "}\n",
                encoding="utf-8",
            )

            failure_diagnostics = {
                "status": "FAIL",
                "compile_errors": [
                    {"category": "unresolved_symbol", "file": str(resource_path), "symbol": "SYSTEM_DICTIONARY-TYPE_CREATE"},
                    {"category": "duplicate_constructor", "file": str(dto_path)},
                ],
            }
            success_diagnostics = {
                "status": "PASS",
                "compile_errors": [],
            }

            def compile_run_side_effect(*args, **kwargs):  # type: ignore[no-untyped-def]
                compile_run_side_effect.calls += 1
                payload = failure_diagnostics if compile_run_side_effect.calls == 1 else success_diagnostics
                dump_yaml(logs_root / "compile-diagnostics.yaml", payload)
                return payload

            compile_run_side_effect.calls = 0

            with patch("runtime.hardening.hardening_pipeline.ProjectCompiler.run", return_value={"status": "PASS"}), patch(
                "runtime.hardening.hardening_pipeline.CompileDiagnostics.run",
                side_effect=compile_run_side_effect,
            ):
                summary = HardeningPipeline(
                    project_root=ROOT.parent,
                    backend_root=BACKEND_ROOT,
                    run_root=run_root,
                    specs_dir=SPECS_DIR,
                ).run(auto_repair=True, verify_boot=False)

            self.assertEqual(summary["status"], "PASS")
            self.assertTrue((logs_root / "compile-diagnostics.yaml").exists())
            self.assertTrue((logs_root / "compile-repair-report.yaml").exists())
            self.assertTrue((logs_root / "dependency-resolution-report.yaml").exists())
            self.assertTrue((logs_root / "boot-diagnostics.yaml").exists())
            self.assertTrue((logs_root / "boot-repair-report.yaml").exists())
            health_report = load_yaml(logs_root / "project-health-report.yaml")
            self.assertEqual(health_report["status"], "PASS")
            self.assertEqual(health_report["compile_repair_count"], 2)
            self.assertEqual(
                set(health_report["compile_repaired_categories"]),
                {"empty_query_dto_constructor_alignment", "permission_constant_normalization"},
            )


if __name__ == "__main__":
    unittest.main()
