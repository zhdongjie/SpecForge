from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.mutation import MutationEngine
from runtime.replay import load_yaml


SPECS_DIR = ROOT / "specs"
BACKEND_ROOT = ROOT.parent / "backend"


class MutationEngineTests(unittest.TestCase):
    def test_mutation_engine_emits_inventory_module(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_root = Path(temp_dir) / "mutated-module"
            summary = MutationEngine(
                project_root=ROOT.parent,
                backend_root=BACKEND_ROOT,
                output_root=output_root,
                specs_dir=SPECS_DIR,
            ).run(verify_compile=False)

            report = load_yaml(output_root / "logs" / "mutation-report.yaml")
            diff = load_yaml(output_root / "logs" / "mutation-diff.yaml")
            resource_file = output_root / "src" / "main" / "java" / "org" / "eu" / "originalkeen" / "system" / "inventory" / "category" / "resource" / "InventoryCategoryResource.java"
            sql_file = output_root / "src" / "main" / "resources" / "sql" / "inventory-management.sql"

            self.assertEqual(summary["status"], "PASS")
            self.assertEqual(report["validation_status"], "PASS")
            self.assertEqual(diff["renamed_entities"]["DictionaryType"], "InventoryCategory")
            self.assertTrue(resource_file.exists())
            self.assertTrue(sql_file.exists())
            self.assertIn('/v1/system/inventory-category', resource_file.read_text(encoding="utf-8"))

    def test_mutation_engine_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            first = root / "first"
            second = root / "second"
            MutationEngine(
                project_root=ROOT.parent,
                backend_root=BACKEND_ROOT,
                output_root=first,
                specs_dir=SPECS_DIR,
            ).run(verify_compile=False)
            MutationEngine(
                project_root=ROOT.parent,
                backend_root=BACKEND_ROOT,
                output_root=second,
                specs_dir=SPECS_DIR,
            ).run(verify_compile=False)

            first_diff = load_yaml(first / "logs" / "mutation-diff.yaml")
            second_diff = load_yaml(second / "logs" / "mutation-diff.yaml")

            self.assertEqual(first_diff, second_diff)


if __name__ == "__main__":
    unittest.main()
