from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.replay import load_yaml
from runtime.synthesis import SynthesisPipeline

SPECS_DIR = ROOT / "specs"
BACKEND_ROOT = ROOT.parent / "backend"


class SynthesisPipelineTests(unittest.TestCase):
    def test_synthesis_pipeline_emits_expected_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_root = Path(temp_dir) / "generated-module"
            summary = SynthesisPipeline(
                project_root=ROOT.parent,
                backend_root=BACKEND_ROOT,
                output_root=output_root,
                specs_dir=SPECS_DIR,
            ).run(verify_compile=False)

            report = load_yaml(output_root / "logs" / "synthesis-report.yaml")
            manifest = load_yaml(output_root / "logs" / "synthesis-manifest.yaml")

            self.assertEqual(summary["validation_status"], "PASS")
            self.assertEqual(report["status"], "PASS")
            self.assertTrue((output_root / "src" / "main" / "resources" / "sql" / "inventory-management.generated.sql").exists())
            self.assertIn("entity-synthesizer", [item["emitter"] for item in manifest["emitters"]])
            self.assertTrue((output_root / "src" / "main" / "java").exists())

    def test_synthesis_output_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as left_dir, tempfile.TemporaryDirectory() as right_dir:
            left_output = Path(left_dir) / "generated-module"
            right_output = Path(right_dir) / "generated-module"
            pipeline = SynthesisPipeline(
                project_root=ROOT.parent,
                backend_root=BACKEND_ROOT,
                output_root=left_output,
                specs_dir=SPECS_DIR,
            )
            pipeline.run(verify_compile=False)
            SynthesisPipeline(
                project_root=ROOT.parent,
                backend_root=BACKEND_ROOT,
                output_root=right_output,
                specs_dir=SPECS_DIR,
            ).run(verify_compile=False)

            left_report = load_yaml(left_output / "logs" / "synthesis-diff.yaml")
            right_report = load_yaml(right_output / "logs" / "synthesis-diff.yaml")
            self.assertEqual(left_report, right_report)


if __name__ == "__main__":
    unittest.main()
