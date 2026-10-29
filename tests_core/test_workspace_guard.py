"""Hard workspace isolation must hold before dispatch, writes or installed-package use."""
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from specforge.cli import main
from specforge.generate import generate
from specforge.release import package
from specforge.workspace import validate_workspace, new_run, resolve_run

ROOT = Path(__file__).resolve().parents[1]


def source_tree(root):
    module = root / "specforge/workspace.py"
    module.parent.mkdir(parents=True)
    module.write_text("# source marker")
    (root / "pyproject.toml").write_text('[project]\nname = "specforge-core"\n')
    return module


def installed_tree(root):
    module = root / "env/lib/python3.10/site-packages/specforge/workspace.py"
    module.parent.mkdir(parents=True)
    module.write_text("# installed marker")
    # An unrelated project's metadata must not turn site-packages into our source root.
    (module.parent.parent / "pyproject.toml").write_text('[project]\nname = "another-project"\n')
    return module


class WorkspaceGuardTests(unittest.TestCase):
    def test_source_root_children_and_ancestors_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            module = source_tree(root / "checkout")
            with patch("specforge.workspace.__file__", str(module)):
                for workspace in [module.parent.parent, module.parent.parent / "work/new", root]:
                    with self.subTest(workspace=workspace), self.assertRaisesRegex(ValueError, "outside SpecForge"):
                        validate_workspace(workspace)
                self.assertFalse((root / "checkout/work").exists())

    def test_sibling_with_similar_prefix_is_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            module = source_tree(root / "checkout")
            with patch("specforge.workspace.__file__", str(module)):
                workspace = root / "checkout-projects/new"
                self.assertEqual(validate_workspace(workspace), workspace)
                self.assertFalse(workspace.exists())

    def test_workspace_alias_and_nonexistent_child_resolve_before_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            module = source_tree(root / "checkout")
            alias = root / "alias"
            alias.symlink_to(module.parent.parent, target_is_directory=True)
            with patch("specforge.workspace.__file__", str(module)):
                with self.assertRaisesRegex(ValueError, "outside SpecForge"):
                    new_run(alias / "does-not-exist")
            self.assertFalse((root / "checkout/does-not-exist").exists())

    def test_relative_repository_path_is_rejected(self):
        with patch("specforge.workspace.Path.cwd", return_value=ROOT):
            with self.assertRaisesRegex(ValueError, "outside SpecForge"):
                validate_workspace(ROOT / "examples/../new-workspace")
        # The CLI resolves '.' from the actual repository before loading a spec.
        with contextlib.redirect_stderr(io.StringIO()) as error:
            self.assertEqual(main(["validate", "--workspace", ".", "--spec", "/missing"]), 1)
        self.assertIn("outside SpecForge", error.getvalue())

    def test_installed_wheel_protects_package_not_entire_environment(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            module = installed_tree(root)
            with patch("specforge.workspace.__file__", str(module)):
                for workspace in [module.parent, module.parent / "new", root / "env"]:
                    with self.subTest(workspace=workspace), self.assertRaisesRegex(ValueError, "outside SpecForge"):
                        validate_workspace(workspace)
                for workspace in [root / "env/projects/new", module.parent.parent / "other-project"]:
                    with self.subTest(workspace=workspace):
                        self.assertEqual(validate_workspace(workspace), workspace)

    def test_installed_wheel_recognizes_source_checkout_from_cwd(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            module = installed_tree(root)
            source = source_tree(root / "checkout").parent.parent
            with patch("specforge.workspace.__file__", str(module)), patch("specforge.workspace.Path.cwd", return_value=source):
                with self.assertRaisesRegex(ValueError, "outside SpecForge"):
                    validate_workspace(source / "sandbox")

    def test_installed_wheel_rejects_workspace_inside_another_source_checkout(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            module = installed_tree(root)
            source = source_tree(root / "another-checkout").parent.parent
            with patch("specforge.workspace.__file__", str(module)):
                with self.assertRaisesRegex(ValueError, "outside SpecForge"):
                    validate_workspace(source / "new")

    def test_managed_directory_aliases_cannot_redirect_writes(self):
        for name in ["runs", "releases"]:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                module = source_tree(root / "checkout")
                workspace = root / "work"
                workspace.mkdir()
                (workspace / name).symlink_to(module.parent.parent, target_is_directory=True)
                before = sorted(str(p.relative_to(root)) for p in root.rglob("*"))
                with patch("specforge.workspace.__file__", str(module)):
                    with self.assertRaisesRegex(ValueError, "symlink or junction"):
                        new_run(workspace)
                    with self.assertRaisesRegex(ValueError, "symlink or junction"):
                        package(root / "missing-run", workspace)
                self.assertEqual(before, sorted(str(p.relative_to(root)) for p in root.rglob("*")))

    def test_template_overlap_still_rejected_after_alias_resolution(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            template = root / "template"
            template.mkdir()
            alias = root / "template-alias"
            alias.symlink_to(template, target_is_directory=True)
            for workspace in [alias, alias / "new", root]:
                with self.subTest(workspace=workspace), self.assertRaisesRegex(ValueError, "workspace and template"):
                    validate_workspace(workspace, template=template)

    def test_all_cli_commands_reject_before_stage_dispatch(self):
        stages = ["load", "get_pack", "generate", "resolve_run", "verify", "repair", "package"]
        for command in ["validate", "generate", "verify", "repair", "package", "run"]:
            with self.subTest(command=command), contextlib.ExitStack() as stack:
                calls = [stack.enter_context(patch("specforge.cli." + name)) for name in stages]
                error = stack.enter_context(contextlib.redirect_stderr(io.StringIO()))
                stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
                args = [command, "--workspace", str(ROOT / "never-create-workspace")]
                if command in ["validate", "generate", "run"]:
                    args += ["--spec", "/missing"]
                if command in ["generate", "run"]:
                    args += ["--template", "/missing-template"]
                self.assertEqual(main(args), 1)
                self.assertIn("outside SpecForge", json.loads(error.getvalue())["error"])
                for call in calls:
                    call.assert_not_called()
                self.assertFalse((ROOT / "never-create-workspace").exists())

    def test_direct_workspace_apis_reject_before_reading_or_creating(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            module = source_tree(root / "checkout")
            workspace = module.parent.parent / "new"
            with patch("specforge.workspace.__file__", str(module)):
                calls = [lambda: new_run(workspace), lambda: resolve_run(workspace),
                         lambda: generate(root / "missing-spec", root / "missing-template", workspace),
                         lambda: package(root / "missing-run", workspace)]
                for call in calls:
                    with self.subTest(call=call), self.assertRaisesRegex(ValueError, "outside SpecForge"):
                        call()
            self.assertFalse(workspace.exists())

    def test_valid_outside_validate_remains_read_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "not-created"
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(["validate", "--workspace", str(workspace), "--spec", str(ROOT / "examples/device_borrow.yaml")]), 0)
            self.assertFalse(workspace.exists())


if __name__ == "__main__":
    unittest.main()
