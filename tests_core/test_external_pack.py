import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from specforge.acceptance_packs import get_pack

class ExternalPackTests(unittest.TestCase):
    def test_explicit_external_module_contract(self):
        with tempfile.TemporaryDirectory() as temp:
            script = Path(temp) / "browser.cjs"
            script.write_text("fixture")
            module = SimpleNamespace(__file__=str(Path(temp) / "__init__.py"), validate_spec=lambda s: None, accept=lambda *a: None)
            with patch("specforge.acceptance_packs.import_module", return_value=module) as load:
                pack = get_pack("python:project.acceptance")
            load.assert_called_once_with("project.acceptance")
            self.assertEqual(pack.browser_script, script)
    def test_invalid_or_implicit_modules_never_imported(self):
        for name in ["project.acceptance", "python:../outside", "python:", "python:a-b", None]:
            with patch("specforge.acceptance_packs.import_module") as load:
                with self.assertRaises(ValueError): get_pack(name)
                load.assert_not_called()
    def test_missing_entry_points_and_script_fail(self):
        with tempfile.TemporaryDirectory() as temp:
            module = SimpleNamespace(__file__=str(Path(temp) / "__init__.py"))
            with patch("specforge.acceptance_packs.import_module", return_value=module):
                with self.assertRaisesRegex(ValueError,"callable"): get_pack("python:project")
                module.validate_spec=lambda s: None
                module.accept=lambda *a: None
                with self.assertRaisesRegex(ValueError,"script missing"): get_pack("python:project")
