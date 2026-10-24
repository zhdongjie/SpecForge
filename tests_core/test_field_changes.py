import copy
import json
from pathlib import Path
import tempfile
import unittest
import yaml
import test_core
from specforge.acceptance_packs import get_pack
from specforge.generate import generate
from specforge.spec import load
from specforge.workspace import inventory, read_json

ROOT = Path(__file__).resolve().parents[1]


class FieldChangeTests(unittest.TestCase):
    def test_fixed_scenarios_require_explicit_identity_and_matching_fields(self):
        pack = get_pack("book-lending-fields")
        for v in (1, 2):
            spec = load(ROOT / f"examples/book_fields_v{v}.yaml")
            pack.validate(spec)
            spec["project"]["id"] = "unrecognized"
            with self.assertRaises(ValueError):
                pack.validate(spec)
        spec = load(ROOT / "examples/book_fields_v1.yaml")
        spec["project"]["id"] = "book_fields_v2"
        with self.assertRaises(ValueError):
            pack.validate(spec)

    def test_same_inputs_deterministic_and_fields_synchronize_across_outputs(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            template = test_core.CoreTests().fixture(root)
            original_template = inventory(template)
            for v in (1, 2):
                workspace = root / f"workspace{v}"
                spec = ROOT / f"examples/book_fields_v{v}.yaml"
                first = generate(spec, template, workspace)
                second = generate(spec, template, workspace)
                self.assertNotEqual(first, second)
                self.assertTrue(first.exists())
                self.assertEqual(
                    inventory(first / "source"), inventory(second / "source")
                )
                self.assertEqual(
                    read_json(first / "manifest.json")["identity"]["spec_sha256"],
                    read_json(second / "manifest.json")["identity"]["spec_sha256"],
                )
                source = first / "source"
                sql = (
                    source
                    / "backend/src/main/resources/db/migration/SF001__business.sql"
                ).read_text()
                dto = (
                    source
                    / "backend/src/main/java/com/original/business/generated/BookInput.java"
                ).read_text()
                ts = (source / "frontend/src/api/business/generated.ts").read_text()
                view = (
                    source / "frontend/src/pages/business/sf_book/index.vue"
                ).read_text()
                field = "isbn" if v == 1 else "catalog_number"
                for content in (sql, dto, ts, view):
                    self.assertIn(field, content)
                obsolete = ["catalog_number"] if v == 1 else ["isbn", "shelf_number"]
                for content in (sql, dto, ts, view):
                    for old in obsolete:
                        self.assertNotIn(old, content)
                if v == 1:
                    self.assertIn("Long shelf_number", dto)
                    self.assertIn("shelf_number?:number", ts)
                    self.assertIn("DEFAULT 0", sql)
                    self.assertIn("CHECK", sql)
                else:
                    self.assertIn("馆藏名称", view)
            self.assertEqual(original_template, inventory(template))

    def test_original_book_browser_is_reused(self):
        self.assertEqual(
            get_pack("book-lending").browser_script,
            get_pack("book-lending-fields").browser_script,
        )
