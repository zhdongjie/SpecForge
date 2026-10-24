"""Coverage is a separate completion gate, not a count of whatever tests exist."""

from pathlib import Path
import tempfile
import unittest
import yaml
from specforge.coverage import check_requirements, require_verified_plan
from specforge.workspace import write_json, read_json


class CoverageTests(unittest.TestCase):
    def fixture(self, root):
        source = root / "source"
        reports = root / "reports"
        (source / "specforge").mkdir(parents=True)
        (source / "specforge/project.yaml").write_text("application: recipe-management")
        (source / "implemented.txt").write_text("source evidence")
        item = {
            "id": "REQ-UPLOAD",
            "need": "real uploaded cover",
            "mode": "adapt",
            "rationale": "reuse platform upload",
            "sources": ["implemented.txt"],
            "template_evidence": ["implemented.txt"],
            "api": ["real upload works"],
            "browser": ["image displayed"],
            "stages": [],
        }
        plan = source / "specforge/requirements.yaml"
        plan.write_text(yaml.safe_dump({"version": 1, "requirements": [item]}))
        write_json(
            reports / "api.json", [{"name": "real upload works", "passed": True}]
        )
        write_json(
            reports / "browser.json", {"status": "PASS", "checks": ["image displayed"]}
        )
        return source, reports, item

    def test_pass_records_requirement_and_hash(self):
        with tempfile.TemporaryDirectory() as td:
            source, reports, item = self.fixture(Path(td))
            result = check_requirements(source, reports)
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["items"][0]["id"], "REQ-UPLOAD")
            require_verified_plan(source, {"requirements": result})

    def test_missing_expected_api_blocks_even_with_other_passing_tests(self):
        with tempfile.TemporaryDirectory() as td:
            source, reports, _ = self.fixture(Path(td))
            write_json(
                reports / "api.json", [{"name": "unrelated test", "passed": True}]
            )
            with self.assertRaisesRegex(ValueError, "REQ-UPLOAD"):
                check_requirements(source, reports)
            self.assertEqual(read_json(reports / "requirements.json")["status"], "FAIL")

    def test_failed_duplicate_test_label_is_not_masked_by_pass(self):
        with tempfile.TemporaryDirectory() as td:
            source, reports, _ = self.fixture(Path(td))
            write_json(
                reports / "api.json",
                [
                    {"name": "real upload works", "passed": True},
                    {"name": "real upload works", "passed": False},
                ],
            )
            with self.assertRaises(ValueError):
                check_requirements(source, reports)

    def test_missing_browser_case_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            source, reports, _ = self.fixture(Path(td))
            write_json(reports / "browser.json", {"status": "PASS", "checks": []})
            with self.assertRaises(ValueError):
                check_requirements(source, reports)

    def test_missing_application_plan_cannot_publish(self):
        with tempfile.TemporaryDirectory() as td:
            source, reports, _ = self.fixture(Path(td))
            (source / "specforge/requirements.yaml").unlink()
            with self.assertRaises(ValueError):
                check_requirements(source, reports)
            with self.assertRaises(ValueError):
                require_verified_plan(source, {"status": "PASS"})

    def test_plan_change_invalidates_previous_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            source, reports, _ = self.fixture(Path(td))
            proof = check_requirements(source, reports)
            with (source / "specforge/requirements.yaml").open("a") as f:
                f.write("\n# changed requirements\n")
            with self.assertRaises(ValueError):
                require_verified_plan(source, {"requirements": proof})

    def test_stage_only_requirement_needs_actual_stage_pass(self):
        with tempfile.TemporaryDirectory() as td:
            source, reports, item = self.fixture(Path(td))
            item.update(api=[], browser=[], stages=["compose"])
            (source / "specforge/requirements.yaml").write_text(
                yaml.safe_dump({"version": 1, "requirements": [item]})
            )
            with self.assertRaises(ValueError):
                check_requirements(source, reports, {"compose": "FAIL"})
            self.assertEqual(
                check_requirements(source, reports, {"compose": "PASS"})["status"],
                "PASS",
            )

    def test_evidence_cannot_escape_project(self):
        with tempfile.TemporaryDirectory() as td:
            source, reports, item = self.fixture(Path(td))
            (Path(td) / "outside").write_text("exists")
            item["sources"] = ["../outside"]
            (source / "specforge/requirements.yaml").write_text(
                yaml.safe_dump({"version": 1, "requirements": [item]})
            )
            with self.assertRaises(ValueError):
                check_requirements(source, reports)

    def test_historical_sample_without_application_keeps_compatibility(self):
        with tempfile.TemporaryDirectory() as td:
            source, reports, _ = self.fixture(Path(td))
            (source / "specforge/project.yaml").write_text(
                "version: 1\nproject: {id: device_borrow}"
            )
            (source / "specforge/requirements.yaml").unlink()
            self.assertIsNone(check_requirements(source, reports))

    def test_new_plain_project_cannot_omit_coverage_plan(self):
        with tempfile.TemporaryDirectory() as td:
            source, reports, _ = self.fixture(Path(td))
            (source / "specforge/project.yaml").write_text(
                "version: 1\nproject: {id: new_real_project}"
            )
            (source / "specforge/requirements.yaml").unlink()
            with self.assertRaises(ValueError):
                check_requirements(source, reports)
            with self.assertRaises(ValueError):
                require_verified_plan(source, {"status": "PASS"})

    def test_package_blocks_uncovered_project_and_preserves_previous_publication(self):
        from specforge.release import package
        from specforge.verification import artifact_hashes
        from specforge.workspace import inventory

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source, reports, _ = self.fixture(root)
            for name in [
                "backend/target/original-service-0.0.1-SNAPSHOT.jar",
                "frontend/dist/index.html",
                "frontend/dist/assets/app.js",
            ]:
                path = source / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("fixture artifact")
            write_json(
                reports / "verify.json",
                {
                    "status": "PASS",
                    "checks": dict.fromkeys(
                        ["backend", "frontend", "compose", "api", "browser"], "PASS"
                    ),
                    "source_sha256": inventory(source),
                    "artifacts_sha256": artifact_hashes(source),
                },
            )
            write_json(root / "published.json", {"previous": "keep"})
            with self.assertRaisesRegex(ValueError, "verified requirement coverage"):
                package(root, root)
            self.assertEqual(read_json(root / "published.json"), {"previous": "keep"})
            self.assertFalse((root / "releases").exists())
