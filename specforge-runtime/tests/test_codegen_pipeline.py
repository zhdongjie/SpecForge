from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.codegen import CodegenPipeline
from runtime.loader import SpecLoader
from runtime.replay import load_yaml

SPECS_DIR = ROOT / "specs"
BACKEND_ROOT = ROOT.parent / "backend"


class CodegenPipelineTests(unittest.TestCase):
    def test_codegen_pipeline_emits_expected_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_root = Path(temp_dir) / "generated-module"
            summary = CodegenPipeline(
                project_root=ROOT.parent,
                backend_root=BACKEND_ROOT,
                output_root=output_root,
                specs_dir=SPECS_DIR,
            ).run(verify_compile=False)

            manifest = load_yaml(output_root / "logs" / "codegen-manifest.yaml")
            validation = load_yaml(output_root / "logs" / "codegen-validation.yaml")

            self.assertEqual(summary["validation_status"], "PASS")
            self.assertEqual(validation["status"], "PASS")
            self.assertTrue((output_root / "src" / "main" / "resources" / "sql" / "dictionary-management.generated.sql").exists())

            emitter_names = [result["emitter"] for result in manifest["emitters"]]
            self.assertEqual(
                emitter_names,
                [
                    "entity-emitter",
                    "mapper-emitter",
                    "dto-emitter",
                    "service-emitter",
                    "controller-emitter",
                    "sql-emitter",
                ],
            )

    def test_codegen_manifest_covers_required_artifacts(self) -> None:
        expected = SpecLoader(SPECS_DIR).load_yaml("module-spec.yaml")["artifact_contract"]
        with tempfile.TemporaryDirectory() as temp_dir:
            output_root = Path(temp_dir) / "generated-module"
            CodegenPipeline(
                project_root=ROOT.parent,
                backend_root=BACKEND_ROOT,
                output_root=output_root,
                specs_dir=SPECS_DIR,
            ).run(verify_compile=False)
            manifest = load_yaml(output_root / "logs" / "codegen-manifest.yaml")
            emitted_classes = {
                self._strip_java_suffix(artifact["relative_java_path"].split("/")[-1])
                for result in manifest["emitters"]
                for artifact in result.get("artifacts", [])
                if artifact.get("relative_java_path", "").endswith(".java")
            }

            for artifact_kind, class_names in expected.items():
                if artifact_kind == "bo":
                    continue
                for class_name in class_names:
                    self.assertIn(class_name, emitted_classes)

    def _strip_java_suffix(self, filename: str) -> str:
        return filename[:-5] if filename.endswith(".java") else filename


if __name__ == "__main__":
    unittest.main()
