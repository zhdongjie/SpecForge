import tempfile
import unittest
from pathlib import Path
from specforge.applications.recipe_management.adaptations import (
    adapt,
    ENUM,
    CLEANER,
    ENUM_MARKER,
    LIFECYCLE_GUARD,
    CLEANER_MARKER,
)
from specforge.workspace import read_json, digest


class TemplateReuseTests(unittest.TestCase):
    def fixture(self, root):
        for name, text in [
            (ENUM, ENUM_MARKER + "\r\n"),
            (CLEANER, CLEANER_MARKER + " READ_COMMITTED"),
            (LIFECYCLE_GUARD, "template-owned guard"),
        ]:
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(text.encode())

    def test_adaptations_record_actual_input_hash_and_narrow_changes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.fixture(root)
            original = digest(root / ENUM)
            cleaner_before = digest(root / CLEANER)
            adapt(root)
            proof = read_json(root / "specforge/adaptations/template-reuse.json")
            self.assertEqual(proof["files"][0]["before_sha256"], original)
            self.assertIn("RECIPE_COVER", (root / ENUM).read_text())
            cleaner = (root / CLEANER).read_text()
            self.assertEqual(digest(root / CLEANER), cleaner_before)
            self.assertEqual([x["path"] for x in proof["files"]], [ENUM])
            self.assertEqual(proof["template_capabilities"][CLEANER], cleaner_before)
            for item in proof["files"]:
                self.assertEqual(item["after_sha256"], digest(root / item["path"]))

    def test_changed_template_contract_stops_instead_of_guessing(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.fixture(root)
            (root / ENUM).write_text("unrecognized template")
            with self.assertRaisesRegex(ValueError, "template reuse contract changed"):
                adapt(root)

    def test_missing_shared_guard_stops_before_any_patch(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); self.fixture(root); before=digest(root/ENUM)
            (root/LIFECYCLE_GUARD).unlink()
            with self.assertRaisesRegex(ValueError,"shared file lifecycle"):
                adapt(root)
            self.assertEqual(digest(root/ENUM), before)

    def test_old_cleaner_is_not_silently_patched(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); self.fixture(root); before=digest(root/ENUM)
            (root/CLEANER).write_text("old cleanup implementation")
            with self.assertRaisesRegex(ValueError,"shared file lifecycle"):
                adapt(root)
            self.assertEqual(digest(root/ENUM), before)
