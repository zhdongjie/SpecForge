"""Regression tests for ownership boundaries, failure routing and filesystem isolation."""

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import yaml
import test_core
from specforge.acceptance_packs import get_pack
from specforge.browser import BrowserRunner
from specforge.cli import verify_with_repair
from specforge.errors import VerificationError, RepairNotApplicable
from specforge.generate import generate
from specforge.release import repair
from specforge.spec import load
from specforge.verification import verify
from specforge.workspace import inventory, write_json, read_json, resolve_run

ROOT = Path(__file__).resolve().parents[1]


class FailureRoutingTests(unittest.TestCase):
    def test_browser_failure_never_attempts_code_repair(self):
        original = VerificationError("browser", "missing browser binary")
        with (
            patch("specforge.cli.verify", side_effect=original),
            patch("specforge.cli.repair") as fix,
        ):
            with self.assertRaises(VerificationError) as caught:
                verify_with_repair(Path("/unused"), "device-borrow")
        self.assertIs(caught.exception, original)
        fix.assert_not_called()

    def test_unknown_compile_failure_preserves_original_error(self):
        original = VerificationError("backend", "actual javac diagnostic")
        with (
            patch("specforge.cli.verify", side_effect=original),
            patch(
                "specforge.cli.repair",
                side_effect=RepairNotApplicable("no matching rule"),
            ),
        ):
            with self.assertRaises(VerificationError) as caught:
                verify_with_repair(Path("/unused"), "device-borrow")
        self.assertIs(caught.exception, original)

    def test_pack_required_before_build_or_deploy(self):
        with tempfile.TemporaryDirectory() as temp:
            run = test_core.ReleaseIntegrityTests().make_run(Path(temp))
            with patch("specforge.verification.command") as cmd:
                with self.assertRaises(VerificationError) as caught:
                    verify(run, reuse_build=True)
            cmd.assert_not_called()
            self.assertEqual(caught.exception.stage, "preflight")

    def test_build_only_does_not_load_business_pack_or_browser(self):
        with tempfile.TemporaryDirectory() as temp:
            run = test_core.ReleaseIntegrityTests().make_run(Path(temp))
            with (
                patch(
                    "specforge.verification.get_pack",
                    side_effect=AssertionError("must not load pack"),
                ),
                patch(
                    "specforge.verification.BrowserRunner.from_environment",
                    side_effect=AssertionError("must not load browser"),
                ),
            ):
                self.assertEqual(
                    verify(run, build_only=True, reuse_build=True)["status"],
                    "BUILD_ONLY",
                )

    def test_api_error_is_not_masked_by_cleanup_error(self):
        with tempfile.TemporaryDirectory() as temp:
            run = test_core.ReleaseIntegrityTests().make_run(Path(temp))
            calls = []

            def cmd(args, *unused, **kw):
                calls.append(args)
                if "logs" in args:
                    raise RuntimeError("logs unavailable")

            with (
                patch("specforge.verification.command", side_effect=cmd),
                patch(
                    "specforge.verification.BrowserRunner.from_environment",
                    return_value=SimpleNamespace(),
                ),
                patch(
                    "specforge.acceptance_packs.device_borrow.accept",
                    side_effect=AssertionError("real business assertion failed"),
                ),
            ):
                with self.assertRaises(VerificationError) as caught:
                    verify(run, reuse_build=True, acceptance_pack="device-borrow")
            self.assertEqual(caught.exception.stage, "api")
            self.assertIn("real business assertion failed", str(caught.exception))
            report = read_json(run / "reports/verify.json")
            self.assertEqual(report["failed_stage"], "api")
            self.assertIn("logs unavailable", report["cleanup_errors"][0])
            self.assertTrue(any("down" in args for args in calls))

    def test_stale_compile_log_does_not_modify_source(self):
        with tempfile.TemporaryDirectory() as temp:
            run = test_core.ReleaseIntegrityTests().make_run(Path(temp))
            source = run / "source"
            path = (
                source
                / "backend/src/main/java/com/original/business/generated/DeviceInput.java"
            )
            path.write_text(
                path.read_text().replace("import java.time.LocalDateTime;", "")
            )
            (run / "reports/backend.log").write_text("cannot find symbol LocalDateTime")
            write_json(
                run / "reports/verify.json",
                {
                    "status": "FAIL",
                    "failed_stage": "browser",
                    "source_sha256": inventory(source),
                },
            )
            before = inventory(source)
            with self.assertRaises(RepairNotApplicable):
                repair(run)
            self.assertEqual(before, inventory(source))

    def test_source_change_requires_reverification_before_repair(self):
        with tempfile.TemporaryDirectory() as temp:
            run = test_core.ReleaseIntegrityTests().make_run(Path(temp))
            source = run / "source"
            write_json(
                run / "reports/verify.json",
                {
                    "status": "FAIL",
                    "failed_stage": "backend",
                    "source_sha256": inventory(source),
                },
            )
            (source / "backend/pom.xml").write_text("edited after failure")
            with self.assertRaises(RepairNotApplicable):
                repair(run)

    def test_preflight_failure_preserves_valid_build_for_retry(self):
        with tempfile.TemporaryDirectory() as temp:
            run = test_core.ReleaseIntegrityTests().make_run(Path(temp))
            with self.assertRaises(VerificationError):
                verify(run, reuse_build=True)
            report = read_json(run / "reports/verify.json")
            self.assertEqual(report["checks"]["backend"], "PASS")
            self.assertIn("artifacts_sha256", report)
            with patch(
                "specforge.verification.get_pack",
                side_effect=AssertionError("not needed for build-only"),
            ):
                self.assertEqual(
                    verify(run, build_only=True, reuse_build=True)["status"],
                    "BUILD_ONLY",
                )

    def test_build_only_repair_does_not_require_business_or_browser_runtime(self):
        with tempfile.TemporaryDirectory() as temp:
            run = test_core.ReleaseIntegrityTests().make_run(Path(temp))
            source = run / "source"
            p = (
                source
                / "backend/src/main/java/com/original/business/generated/DeviceInput.java"
            )
            p.write_text(p.read_text().replace("import java.time.LocalDateTime;", ""))
            (run / "reports/backend.log").write_text("cannot find symbol LocalDateTime")
            write_json(
                run / "reports/verify.json",
                {
                    "status": "FAIL",
                    "failed_stage": "backend",
                    "build_only": True,
                    "source_sha256": inventory(source),
                },
            )
            with patch(
                "specforge.release.verify", return_value={"status": "BUILD_ONLY"}
            ) as recheck:
                self.assertEqual(repair(run)["status"], "BUILD_ONLY")
            recheck.assert_called_once_with(run, build_only=True, acceptance_pack=None)


class PackBoundaryTests(unittest.TestCase):
    def test_pack_rejects_unrelated_domain(self):
        spec = load(ROOT / "examples/device_borrow.yaml")
        spec["entities"][0]["name"] = "book"
        with self.assertRaisesRegex(ValueError, "device and borrow"):
            get_pack("device-borrow").validate(spec)

    def test_pack_rejects_unsupported_semantics_before_runtime(self):
        spec = load(ROOT / "examples/device_borrow.yaml")
        spec["entities"][1]["workflow"]["transitions"][0]["forbid_self"] = False
        with self.assertRaisesRegex(ValueError, "workflow actions"):
            get_pack("device-borrow").validate(spec)

    def test_another_domain_generates_without_acceptance_pack(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            spec = load(ROOT / "examples/device_borrow.yaml")
            spec["project"]["id"] = "catalog_loans"
            spec["entities"][0]["name"] = "catalog"
            spec["entities"][1]["name"] = "loan"
            spec["entities"][1]["fields"][0]["reference"] = "catalog"
            path = root / "spec.yaml"
            path.write_text(yaml.safe_dump(spec, allow_unicode=True))
            run = generate(path, test_core.CoreTests().fixture(root), root / "w")
            self.assertTrue(
                (
                    run / "source/frontend/src/pages/business/sf_catalog/index.vue"
                ).exists()
            )
            self.assertTrue(
                (run / "source/frontend/src/pages/business/sf_loan/index.vue").exists()
            )

    def test_pack_rejects_missing_browser_fields_at_preflight(self):
        spec = load(ROOT / "examples/device_borrow.yaml")
        spec["entities"][0]["page"]["list"].remove("code")
        with self.assertRaisesRegex(ValueError, "page fields"):
            get_pack("device-borrow").validate(spec)

    def test_changed_ui_labels_can_use_same_pack(self):
        spec = load(ROOT / "examples/device_borrow.yaml")
        spec["entities"][0]["label"] = "仪器"
        spec["entities"][1]["workflow"]["state_labels"] = {"APPROVED": "借出中"}
        get_pack("device-borrow").validate(spec)


class BrowserTransportTests(unittest.TestCase):
    def test_native_runner_does_not_accept_missing_or_stale_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_json(root / "browser.json", {"status": "PASS"})
            runner = BrowserRunner("fake-node", "fake-module")
            with patch(
                "specforge.browser.subprocess.run",
                return_value=SimpleNamespace(returncode=0, stdout="", stderr=""),
            ):
                with self.assertRaisesRegex(RuntimeError, "did not produce"):
                    runner.run(
                        root / "scenario.cjs", "http://local", "secret", root, {}
                    )

    def test_native_payload_cannot_override_runtime_target(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            runner = BrowserRunner("fake-node", "fake-module")
            seen = {}

            def execute(args, **kwargs):
                seen.update(json.loads(kwargs["input"]))
                write_json(root / "browser.json", {"status": "PASS"})
                return SimpleNamespace(returncode=0, stdout="", stderr="")

            with patch("specforge.browser.subprocess.run", side_effect=execute):
                runner.run(
                    root / "scenario.cjs",
                    "http://trusted",
                    "secret",
                    root,
                    {"origin": "http://wrong"},
                )
            self.assertEqual(seen["origin"], "http://trusted")


class WorkspaceBoundaryTests(unittest.TestCase):
    def test_inventory_does_not_descend_into_dependency_cache(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "node_modules").mkdir()
            (root / "source.txt").write_text("source")
            scan = os.scandir

            def guarded(path):
                if Path(path).name == "node_modules":
                    raise AssertionError("dependency traversal")
                return scan(path)

            with patch("specforge.workspace.os.scandir", side_effect=guarded):
                self.assertEqual(list(inventory(root)), ["source.txt"])

    def test_source_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "real.txt").write_text("source")
            (root / "alias.txt").symlink_to(root / "real.txt")
            with self.assertRaisesRegex(ValueError, "symlink"):
                inventory(root)

    def test_latest_pointer_cannot_escape_runs(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_json(root / "latest.json", {"run_id": "../outside"})
            with self.assertRaises(ValueError):
                resolve_run(root)


if __name__ == "__main__":
    unittest.main()
