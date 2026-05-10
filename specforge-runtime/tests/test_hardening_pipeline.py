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
from runtime.hardening.boot_diagnostics import BootDiagnostics
from runtime.hardening.compile_error_classifier import CompileErrorClassifier
from runtime.hardening.compile_repair_engine import CompileRepairEngine
from runtime.hardening.hardening_pipeline import HardeningPipeline
from runtime.platform_compiler.boot_verifier import BootVerifier
from runtime.replay import load_yaml

SPECS_DIR = ROOT / "specs"
BACKEND_ROOT = ROOT.parent / "backend"


class FakeStdout:
    def __init__(self, lines: list[str]) -> None:
        self._lines = list(lines)

    def readline(self) -> str:
        if self._lines:
            return self._lines.pop(0)
        return ""


class FakeProcess:
    def __init__(self, lines: list[str], exit_code: int | None = None) -> None:
        self.stdout = FakeStdout(lines)
        self._exit_code = exit_code
        self.returncode = exit_code
        self.terminated = False
        self.killed = False

    def poll(self) -> int | None:
        if self.stdout._lines:
            return None
        return self.returncode

    def terminate(self) -> None:
        self.terminated = True
        if self.returncode is None:
            self.returncode = 0

    def wait(self, timeout: int | None = None) -> int:
        return 0 if self.returncode is None else self.returncode

    def kill(self) -> None:
        self.killed = True
        if self.returncode is None:
            self.returncode = -9


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


class BootVerificationTests(unittest.TestCase):
    def test_boot_diagnostics_passes_when_started_marker_is_observed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            logs_root = project_root / "logs"
            logs_root.mkdir(parents=True, exist_ok=True)
            process = FakeProcess(
                [
                    "Downloading dependencies\n",
                    "Started BackendApplication in 8.123 seconds\n",
                ],
                exit_code=None,
            )
            environment = {
                "maven_command": "mvn",
                "env": {},
                "binding": {"java_home": "fake", "maven_command": "mvn"},
            }
            with patch(
                "runtime.hardening.boot_diagnostics.CompileDiagnostics._resolve_environment",
                return_value=environment,
            ), patch(
                "runtime.hardening.boot_diagnostics.subprocess.Popen",
                return_value=process,
            ), patch(
                "runtime.hardening.boot_diagnostics.time.time",
                side_effect=[0, 0, 1, 1, 1, 1],
            ):
                diagnostics = BootDiagnostics(project_root, logs_root).run(timeout_seconds=30, idle_timeout_seconds=10)

            self.assertEqual(diagnostics["status"], "PASS")
            self.assertIn("-ntp", diagnostics["command"])
            self.assertEqual(diagnostics["failure_reason"], None)
            written = load_yaml(logs_root / "boot-diagnostics.yaml")
            self.assertEqual(written["status"], "PASS")

    def test_boot_verifier_reports_idle_timeout_deterministically(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            process = FakeProcess([], exit_code=None)
            toolchain = {
                "maven_command": "mvn",
                "binding": {"java_home": "fake", "maven_command": "mvn"},
                "env": {},
            }
            with patch(
                "runtime.platform_compiler.boot_verifier.resolve_toolchain",
                return_value=toolchain,
            ), patch(
                "runtime.platform_compiler.boot_verifier.subprocess.Popen",
                return_value=process,
            ), patch(
                "runtime.platform_compiler.boot_verifier.time.time",
                side_effect=[0, 0, 181, 181],
            ):
                result = BootVerifier(project_root).boot_check(timeout_seconds=900, idle_timeout_seconds=180)

            self.assertEqual(result["status"], "FAIL")
            self.assertEqual(result["reason"], "startup-idle-timeout")
            self.assertEqual(result["idle_timeout_seconds"], 180)
            self.assertEqual(result["timeout_seconds"], 900)


if __name__ == "__main__":
    unittest.main()
