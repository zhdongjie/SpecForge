import copy, json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
import yaml
from specforge.spec import load, validate, SpecError, JAVA, SQL
from specforge.generate import generate
from specforge.workspace import inventory, write_json, read_json
from specforge.release import package, repair

ROOT = Path(__file__).resolve().parents[1]


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.spec = load(ROOT / "examples/device_borrow.yaml")

    def invalid(self, mutate):
        s = copy.deepcopy(self.spec)
        mutate(s)
        with self.assertRaises(SpecError):
            validate(s)

    def test_spec_valid(self):
        self.assertEqual(validate(self.spec)["version"], 1)

    def test_unknown_type(self):
        self.invalid(lambda s: s["entities"][0]["fields"][0].update(type="decimal"))

    def test_unknown_keys(self):
        self.invalid(lambda s: s.update(unimplemented=True))

    def test_unknown_reference(self):
        self.invalid(
            lambda s: s["entities"][1]["fields"][0].update(reference="missing")
        )

    def test_duplicate_fields(self):
        self.invalid(
            lambda s: s["entities"][0]["fields"].append(s["entities"][0]["fields"][0])
        )

    def test_unsafe_identifier(self):
        self.invalid(lambda s: s["entities"][0].update(name="../bad"))

    def test_invalid_enum(self):
        self.invalid(
            lambda s: s["entities"][0]["fields"][0].update(type="enum", values=[])
        )

    def test_unsupported_operation(self):
        self.invalid(lambda s: s["entities"][0]["crud"].append("execute_shell"))

    def test_unsupported_owner_edit(self):
        self.invalid(lambda s: s["entities"][1]["crud"].append("update"))

    def test_page_unknown_field(self):
        self.invalid(lambda s: s["entities"][0]["page"]["form"].append("missing"))

    def test_bad_state(self):
        self.invalid(
            lambda s: s["entities"][1]["workflow"]["transitions"][0].update(
                to="UNKNOWN"
            )
        )

    def test_exclusive_guard_required(self):
        self.invalid(
            lambda s: s["entities"][1]["workflow"]["transitions"][0].update(
                exclusive=False
            )
        )

    def test_types_complete(self):
        self.assertEqual(set(JAVA), set(SQL))
        self.assertEqual(JAVA["foreign"], "Long")

    def fixture(self, root):
        t = root / "template"
        for n in [
            "backend/pom.xml",
            "backend/src/main/java/com/original/system/file/service/ImageValidationService.java",
            "frontend/pnpm-lock.yaml",
            "frontend/src/stores/user.ts",
            "deploy/compose.yaml",
            "backend/src/main/resources/sql/schema.sql",
        ]:
            p = t / n
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("fixture\n")
        for n in [
            ".env",
            "backend/.env.production",
            "private.key",
            "frontend/node_modules/a",
            "backend/target/a",
            ".jwk/key",
            "logs/a",
        ]:
            p = t / n
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("DO NOT COPY")
        (t / ".env.example").write_text("EXAMPLE=\n")
        return t

    def test_generation_determinism_isolation_exclusions_routes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            t = self.fixture(root)
            before = inventory(t)
            a = generate(ROOT / "examples/device_borrow.yaml", t, root / "workspace")
            b = generate(ROOT / "examples/device_borrow.yaml", t, root / "workspace")
            self.assertNotEqual(a, b)
            self.assertEqual(inventory(a / "source"), inventory(b / "source"))
            self.assertEqual(before, inventory(t))
            names = inventory(a / "source")
            self.assertFalse(
                any(
                    "DO NOT COPY" in p.read_text()
                    for p in (a / "source").rglob("*")
                    if p.is_file()
                )
            )
            self.assertIn(".env.example", names)
            self.assertIn("frontend/src/pages/business/sf_borrow/index.vue", names)
            permissions = read_json(a / "source/specforge/permissions.json")
            self.assertTrue(
                any(x["route"] == "/business/sf_borrow" for x in permissions)
            )

    def test_field_change_propagates(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            t = self.fixture(root)
            s = self.spec
            s["entities"][0]["fields"].append(
                {
                    "name": "location",
                    "label": "位置",
                    "type": "string",
                    "required": True,
                }
            )
            s["entities"][0]["page"]["form"].append("location")
            s["entities"][0]["page"]["list"].append("location")
            p = root / "spec.yaml"
            p.write_text(yaml.safe_dump(s, allow_unicode=True))
            run = generate(p, t, root / "w")
            for n in [
                "backend/src/main/java/com/original/business/generated/DeviceInput.java",
                "frontend/src/pages/business/sf_device/index.vue",
                "backend/src/main/resources/db/migration/SF001__business.sql",
            ]:
                self.assertIn("location", (run / "source" / n).read_text())

    def test_failed_release_preserves_published(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            run = generate(
                ROOT / "examples/device_borrow.yaml", self.fixture(root), root / "w"
            )
            write_json(root / "w/published.json", {"old": "keep"})
            write_json(run / "reports/verify.json", {"status": "FAIL"})
            with self.assertRaises(ValueError):
                package(run, root / "w")
            self.assertEqual(read_json(root / "w/published.json"), {"old": "keep"})

    def test_build_only_cannot_publish(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            run = generate(
                ROOT / "examples/device_borrow.yaml", self.fixture(root), root / "w"
            )
            write_json(run / "reports/verify.json", {"status": "BUILD_ONLY"})
            with self.assertRaises(ValueError):
                package(run, root / "w")

    def test_workspace_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            t = self.fixture(root)
            generate(ROOT / "examples/device_borrow.yaml", t, root / "w")
            p = root / "different.yaml"
            s = self.spec
            s["project"]["id"] = "other"
            p.write_text(yaml.safe_dump(s))
            with self.assertRaises(ValueError):
                generate(p, t, root / "w")

    def test_unknown_repair_stops(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            run = generate(
                ROOT / "examples/device_borrow.yaml", self.fixture(root), root / "w"
            )
            with self.assertRaises(RuntimeError):
                repair(run)
            self.assertEqual(
                read_json(run / "reports/repair.json")["status"], "STOPPED"
            )

    def test_known_repair(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            run = generate(
                ROOT / "examples/device_borrow.yaml", self.fixture(root), root / "w"
            )
            p = (
                run
                / "source/backend/src/main/java/com/original/business/generated/DeviceInput.java"
            )
            p.write_text(p.read_text().replace("import java.time.LocalDateTime;", ""))
            (run / "reports/backend.log").write_text("cannot find symbol LocalDateTime")
            write_json(
                run / "reports/verify.json",
                {
                    "status": "FAIL",
                    "failed_stage": "backend",
                    "source_sha256": inventory(run / "source"),
                    "acceptance_pack": "device-borrow",
                },
            )
            with patch("specforge.release.verify", return_value={"status": "PASS"}):
                self.assertEqual(repair(run)["status"], "PASS")
            self.assertIn("import java.time.LocalDateTime;", p.read_text())
            self.assertTrue((run / "reports/repair-1.patch").exists())


class ReleaseIntegrityTests(unittest.TestCase):
    def make_run(self, root):
        template = CoreTests().fixture(root)
        run = generate(ROOT / "examples/device_borrow.yaml", template, root / "w")
        source = run / "source"
        for name in [
            "backend/target/original-service-0.0.1-SNAPSHOT.jar",
            "frontend/dist/assets/app.js",
            "frontend/dist/index.html",
        ]:
            p = source / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("built fixture")
        from specforge.verification import artifact_hashes

        write_json(
            run / "reports/verify.json",
            {
                "status": "PASS",
                "checks": {
                    k: "PASS"
                    for k in ["backend", "frontend", "compose", "api", "browser"]
                },
                "source_sha256": inventory(source),
                "artifacts_sha256": artifact_hashes(source),
            },
        )
        return run

    def test_accepted_archive_has_artifacts_and_manifest(self):
        import zipfile

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            run = self.make_run(root)
            result = package(run, root / "w")
            with zipfile.ZipFile(result["archive"]) as z:
                names = z.namelist()
                self.assertIn("admin-platform/MANIFEST.json", names)
                self.assertIn(
                    "admin-platform/backend/target/original-service-0.0.1-SNAPSHOT.jar",
                    names,
                )
                self.assertFalse(
                    any(n.endswith("/.env") or "/node_modules/" in n for n in names)
                )

    def test_source_tamper_blocks_publication(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            run = self.make_run(root)
            (run / "source/backend/pom.xml").write_text("changed")
            with self.assertRaises(ValueError):
                package(run, root / "w")
            self.assertFalse((root / "w/published.json").exists())

    def test_artifact_tamper_blocks_publication(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            run = self.make_run(root)
            (run / "source/frontend/dist/assets/app.js").write_text("changed")
            with self.assertRaises(ValueError):
                package(run, root / "w")

    def test_generated_database_and_transaction_invariants(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            run = self.make_run(root)
            sql = (
                run
                / "source/backend/src/main/resources/db/migration/SF001__business.sql"
            ).read_text()
            self.assertIn("UNIQUE KEY sf_one_active", sql)
            java = (
                run
                / "source/backend/src/main/java/com/original/business/generated/BusinessResource.java"
            ).read_text()
            self.assertIn("new DataSourceTransactionManager", java)
            self.assertIn("FOR UPDATE", java)

    def test_cleanup_failure_cannot_leave_pass_report(self):
        from specforge.verification import verify

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            run = self.make_run(root)
            calls = []

            def fake(args, *a, **kw):
                calls.append(args)
                if "logs" in args:
                    raise RuntimeError("injected log collection failure")

            with (
                patch("specforge.verification.command", side_effect=fake),
                patch(
                    "specforge.acceptance_packs.device_borrow.accept", return_value={}
                ),
                patch(
                    "specforge.verification.BrowserRunner.from_environment",
                    return_value=SimpleNamespace(run=lambda *args: "PASS"),
                ),
            ):
                with self.assertRaises(RuntimeError):
                    verify(run, reuse_build=True, acceptance_pack="device-borrow")
            self.assertTrue(any("down" in args for args in calls))
            self.assertFalse((run / "acceptance.env").exists())
            self.assertEqual(read_json(run / "reports/verify.json")["status"], "FAIL")

    def test_startup_failure_still_cleans_up(self):
        from specforge.verification import verify

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            run = self.make_run(root)
            calls = []

            def fake(args, *a, **kw):
                calls.append(args)
                if "up" in args:
                    raise RuntimeError("injected startup failure")

            with (
                patch("specforge.verification.command", side_effect=fake),
                patch(
                    "specforge.verification.BrowserRunner.from_environment",
                    return_value=SimpleNamespace(run=lambda *args: "PASS"),
                ),
            ):
                with self.assertRaises(RuntimeError):
                    verify(run, reuse_build=True, acceptance_pack="device-borrow")
            self.assertTrue(any("down" in args for args in calls))
            self.assertFalse((run / "acceptance.env").exists())

    def test_literal_script_closing_tag_is_escaped(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            template = CoreTests().fixture(root)
            spec = load(ROOT / "examples/device_borrow.yaml")
            spec["entities"][0]["label"] = "</script><script>bad</script>"
            path = root / "spec.yaml"
            path.write_text(yaml.safe_dump(spec, allow_unicode=True))
            run = generate(path, template, root / "w")
            page = (
                run / "source/frontend/src/pages/business/sf_device/index.vue"
            ).read_text()
            self.assertEqual(page.count("</script>"), 1)
            self.assertIn(r"\u003c", page)


if __name__ == "__main__":
    unittest.main()
