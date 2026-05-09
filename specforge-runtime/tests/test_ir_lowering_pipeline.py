from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.ir_lowering import IRLoweringPipeline
from runtime.replay import load_yaml

SPECS_DIR = ROOT / "specs"


class IRLoweringPipelineTests(unittest.TestCase):
    def test_lowering_pipeline_emits_generated_ir(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_root = Path(temp_dir) / "run-001"
            summary = IRLoweringPipeline(
                output_root=output_root,
                specs_dir=SPECS_DIR,
            ).run()

            generated = load_yaml(output_root / "generated-ir" / "field-schema.generated.yaml")
            report = load_yaml(output_root / "generated-ir" / "logs" / "lowering-report.yaml")
            validation = load_yaml(output_root / "generated-ir" / "logs" / "lowering-validation.yaml")

            self.assertEqual(summary["status"], "PASS")
            self.assertEqual(report["status"], "PASS")
            self.assertEqual(validation["status"], "PASS")
            self.assertEqual(generated["module"]["route_base"], "/v1/business")
            self.assertEqual(
                sorted(generated["entities"].keys()),
                [
                    "LaboratoryBuilding",
                    "LaboratoryRoom",
                ],
            )
            self.assertIn("business:laboratory-building:create", generated["permissions"])
            laboratory_room_fields = [field["name"] for field in generated["entities"]["LaboratoryRoom"]["fields"]]
            self.assertIn("laboratoryBuildingId", laboratory_room_fields)

    def test_lowering_pipeline_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as left_dir, tempfile.TemporaryDirectory() as right_dir:
            left_output = Path(left_dir) / "run-left"
            right_output = Path(right_dir) / "run-right"

            IRLoweringPipeline(output_root=left_output, specs_dir=SPECS_DIR).run()
            IRLoweringPipeline(output_root=right_output, specs_dir=SPECS_DIR).run()

            left_generated = load_yaml(left_output / "generated-ir" / "field-schema.generated.yaml")
            right_generated = load_yaml(right_output / "generated-ir" / "field-schema.generated.yaml")
            left_diff = load_yaml(left_output / "generated-ir" / "logs" / "lowering-diff.yaml")
            right_diff = load_yaml(right_output / "generated-ir" / "logs" / "lowering-diff.yaml")

            self.assertEqual(left_generated, right_generated)
            self.assertEqual(left_diff, right_diff)

    def test_business_template_backfills_empty_capabilities_from_module_spec(self) -> None:
        template_specs_dir = SPECS_DIR / "templates" / "underwriting-approval-management"
        with tempfile.TemporaryDirectory() as temp_dir:
            output_root = Path(temp_dir) / "run-business"
            summary = IRLoweringPipeline(
                output_root=output_root,
                specs_dir=template_specs_dir,
            ).run()

            generated = load_yaml(output_root / "generated-ir" / "field-schema.generated.yaml")
            validation = load_yaml(output_root / "generated-ir" / "logs" / "lowering-validation.yaml")

            self.assertEqual(summary["status"], "PASS")
            self.assertEqual(validation["status"], "PASS")
            self.assertEqual(generated["module"]["route_base"], "/v1/business/underwriting-approval")
            self.assertEqual(
                sorted(generated["permissions"]),
                [
                    "business:underwriting-approval:create",
                    "business:underwriting-approval:delete",
                    "business:underwriting-approval:details",
                    "business:underwriting-approval:list",
                    "business:underwriting-approval:page",
                    "business:underwriting-approval:update",
                ],
            )
            self.assertEqual(
                generated["entities"]["UnderwritingApproval"]["permission_namespace"],
                "business:underwriting-approval",
            )
            self.assertEqual(
                generated["entities"]["UnderwritingApproval"]["route_segment"],
                "underwriting-approval",
            )


if __name__ == "__main__":
    unittest.main()
