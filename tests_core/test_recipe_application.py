"""Recipe application boundaries are explicit and cannot grant raw table bypasses."""

import copy
from pathlib import Path
import tempfile
import unittest
import yaml
import test_core
from specforge.spec import load, validate, SpecError
from specforge.generate import generate, permissions
from specforge.applications import get_application
from specforge.acceptance_packs import get_pack
from specforge.workspace import inventory, read_json

ROOT = Path(__file__).resolve().parents[1]


class RecipeApplicationTests(unittest.TestCase):
    def setUp(self):
        self.spec = load(ROOT / "examples/recipe_management.yaml")

    def test_explicit_contract_and_acceptance_agree(self):
        get_application("recipe-management").validate_spec(self.spec)
        get_pack("recipe-management").validate(self.spec)
        other = load(ROOT / "examples/book_lending.yaml")
        with self.assertRaises(ValueError):
            get_pack("recipe-management").validate(other)

    def test_unknown_application_and_nonstring_are_rejected(self):
        for name in ["unknown-application", {"name": "recipe-management"}]:
            spec = copy.deepcopy(self.spec)
            spec["application"] = name
            with self.assertRaises(SpecError):
                validate(spec)

    def test_recipe_storage_cannot_silently_change_business_contract(self):
        spec = copy.deepcopy(self.spec)
        spec["entities"][1]["crud"].append("update")
        with self.assertRaises(SpecError):
            validate(spec)
        spec = copy.deepcopy(self.spec)
        spec["entities"][1]["fields"][0]["name"] = "caption"
        spec["entities"][1]["page"]["list"][0] = "caption"
        spec["entities"][1]["page"]["form"][0] = "caption"
        with self.assertRaises(SpecError):
            validate(spec)

    def test_no_role_has_generic_recipe_table_permissions(self):
        app = get_application("recipe-management")
        actual = app.permissions(self.spec, permissions(self.spec))
        authorities = {p["authority"] for p in actual}
        for entity in ["recipe", "recipe_ingredient", "recipe_step", "recipe_favorite"]:
            self.assertNotIn("business:sf_" + entity, authorities)
            self.assertFalse(
                any(a.startswith("business:sf_" + entity + ":") for a in authorities)
            )
        for action in ["browse", "publish", "favorite"]:
            row = next(
                p for p in actual if p["authority"] == "business:recipes:" + action
            )
            self.assertEqual(set(row["roles"]), {"admin", "normal"})
        for action in ["review", "statistics"]:
            row = next(
                p for p in actual if p["authority"] == "business:recipes:" + action
            )
            self.assertEqual(row["roles"], ["admin"])

    def test_application_generation_is_deterministic_and_template_stays_unchanged(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            template = test_core.CoreTests().fixture(root)
            (template / "frontend/src/appConfig.ts").write_text(
                "export default {name: 'template'}"
            )
            from specforge.applications.recipe_management.adaptations import (
                ENUM,
                CLEANER,
                ENUM_MARKER,
                CLEANER_MARKER,
            )

            for name, content in [
                (ENUM, ENUM_MARKER),
                (CLEANER, CLEANER_MARKER + " READ_COMMITTED"),
            ]:
                path = template / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
            before = inventory(template)
            first = generate(
                ROOT / "examples/recipe_management.yaml", template, root / "project"
            )
            second = generate(
                ROOT / "examples/recipe_management.yaml", template, root / "project"
            )
            self.assertEqual(inventory(first / "source"), inventory(second / "source"))
            self.assertEqual(before, inventory(template))
            source = first / "source"
            self.assertIn(
                "食谱管理系统", (source / "frontend/src/appConfig.ts").read_text()
            )
            self.assertTrue(
                (
                    source
                    / "backend/src/main/java/com/original/business/recipes/RecipeResource.java"
                ).is_file()
            )
            self.assertTrue(
                (source / "frontend/src/pages/business/recipes/index.vue").is_file()
            )
            sql = (source / "backend/src/main/resources/sql/schema.sql").read_text()
            self.assertIn("UNIQUE KEY recipe_user_favorite(recipe_id,user_id)", sql)
            self.assertTrue((source / "RECIPE_SYSTEM.md").is_file())
            perms = read_json(source / "specforge/permissions.json")
            self.assertTrue(
                any(p["authority"] == "business:recipes:review" for p in perms)
            )
