import hashlib
import importlib.util
import json
from pathlib import Path
import stat
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.util.spec_from_file_location(
    "verify_release_tool", ROOT / "tools/verify-release.py"
)
release = importlib.util.module_from_spec(loader)
loader.loader.exec_module(release)


class ReleaseDeliveryTests(unittest.TestCase):
    def fixture(self, root, change=None, extra=None):
        files = {p: b"fixture" for p in release.REQUIRED}
        spec = (ROOT / "examples/device_borrow.yaml").read_bytes()
        identity = {"spec_sha256": hashlib.sha256(spec).hexdigest()}
        files["specforge/project.yaml"] = spec
        files["specforge/identity.json"] = json.dumps(identity).encode()
        files["frontend/dist/assets/app.js"] = b"javascript"
        manifest = {
            "identity": identity,
            "sha256": {n: hashlib.sha256(v).hexdigest() for n, v in files.items()},
            "verification": {
                "status": "PASS",
                "checks": dict.fromkeys(
                    ["backend", "frontend", "compose", "api", "browser"], "PASS"
                ),
            },
        }
        if change:
            change(files, manifest)
        archive = root / "release.zip"
        with zipfile.ZipFile(archive, "w") as z:
            for name, value in files.items():
                z.writestr("admin-platform/" + name, value)
            z.writestr("admin-platform/MANIFEST.json", json.dumps(manifest))
            if extra:
                z.writestr(*extra)
        archive.with_suffix(".zip.sha256").write_text(
            release.digest(archive) + "  release.zip"
        )
        return archive

    def test_valid_release_extracts_with_matching_identity(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            archive = self.fixture(root)
            source, manifest = release.validate_extract(archive, root / "extracted")
            self.assertTrue((source / "frontend/dist/assets/app.js").is_file())
            self.assertEqual(
                manifest["identity"],
                release.read_json(source / "specforge/identity.json"),
            )

    def test_corrupted_archive_rejected_before_extraction(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            archive = self.fixture(root)
            with archive.open("ab") as f:
                f.write(b"corrupt")
            with self.assertRaisesRegex(ValueError, "checksum"):
                release.validate_extract(archive, root / "extract")
            self.assertFalse((root / "extract").exists())

    def test_application_archive_without_coverage_proof_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)

            def change(files, manifest):
                spec = (ROOT / "examples/recipe_management.yaml").read_bytes()
                identity = {"spec_sha256": hashlib.sha256(spec).hexdigest()}
                manifest["identity"] = identity
                for name, value in {
                    "specforge/project.yaml": spec,
                    "specforge/identity.json": json.dumps(identity).encode(),
                }.items():
                    files[name] = value
                    manifest["sha256"][name] = hashlib.sha256(value).hexdigest()

            archive = self.fixture(root, change)
            with self.assertRaisesRegex(ValueError, "verified requirement coverage"):
                release.validate_extract(archive, root / "extract")

    def test_missing_required_file_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)

            def change(files, manifest):
                name = "frontend/dist/index.html"
                files.pop(name)
                manifest["sha256"].pop(name)

            archive = self.fixture(root, change)
            with self.assertRaisesRegex(ValueError, "required"):
                release.validate_extract(archive, root / "extract")

    def test_manifest_hash_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            archive = self.fixture(
                root,
                lambda files, manifest: files.update(
                    {"frontend/dist/index.html": b"tampered"}
                ),
            )
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                release.validate_extract(archive, root / "extract")

    def test_unsafe_archive_paths_and_symlink_rejected(self):
        link = zipfile.ZipInfo("admin-platform/link")
        link.create_system = 3
        link.external_attr = (stat.S_IFLNK | 0o777) << 16
        for entry in [
            "admin-platform/../../escape",
            "/absolute",
            "admin-platform/dir\\evil",
            "admin-platform/C:/evil",
            link,
        ]:
            with self.subTest(entry=str(entry)), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                archive = self.fixture(root, extra=(entry, "target"))
                with self.assertRaises(ValueError):
                    release.validate_extract(archive, root / "extract")
                self.assertFalse((root / "escape").exists())

    def test_unlisted_archive_file_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            archive = self.fixture(root, extra=("admin-platform/unlisted", "extra"))
            with self.assertRaisesRegex(ValueError, "inventory mismatch"):
                release.validate_extract(archive, root / "extract")

    def test_host_mount_outside_extraction_rejected(self):
        config = {"services": dict.fromkeys(["db", "redis", "backend", "frontend"], {})}
        config["services"]["db"] = {
            "volumes": [
                {
                    "type": "bind",
                    "source": "/home/zhang/projects/ai/SpecForge",
                    "target": "/work",
                }
            ]
        }
        with self.assertRaisesRegex(ValueError, "outside"):
            release.validate_compose(config, Path("/tmp/extracted"))

    def test_cleanup_failure_blocks_success(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            archive = self.fixture(root)
            pack = SimpleNamespace(
                validate=lambda spec: None,
                run_api=lambda *args: {},
                browser_script=Path("unused"),
            )
            browser = SimpleNamespace(run=lambda *args: "PASS")
            project = None

            def output(args, **kwargs):
                nonlocal project
                if "-p" in args:
                    project = args[args.index("-p") + 1]
                if "config" in args:
                    return json.dumps(
                        {
                            "services": dict.fromkeys(
                                ["db", "redis", "backend", "frontend"], {}
                            )
                        }
                    ).encode()
                if "ps" in args:
                    return "a b c d"
                if args[:2] == ["docker", "inspect"]:
                    return json.dumps(
                        [
                            {
                                "Config": {
                                    "Labels": {"com.docker.compose.project": project}
                                },
                                "Mounts": [],
                            }
                        ]
                        * 4
                    )
                raise AssertionError(args)

            def run(args, **kwargs):
                if "up" in args:
                    env_path = Path(args[args.index("--env-file") + 1])
                    fields = dict(
                        line.split("=", 1) for line in env_path.read_text().splitlines()
                    )
                    self.assertRegex(
                        fields["APP_BOOTSTRAP_PASSWORD"],
                        r"^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])[A-Za-z0-9]{8,16}$",
                    )
                return SimpleNamespace(returncode=1 if "down" in args else 0)

            with (
                patch.object(release, "get_pack", return_value=pack),
                patch.object(
                    release.BrowserRunner, "from_environment", return_value=browser
                ),
                patch.object(release.subprocess, "check_output", side_effect=output),
                patch.object(release.subprocess, "run", side_effect=run),
            ):
                result = release.verify_release(
                    archive, root / "reports", "device-borrow"
                )
            self.assertEqual(result["status"], "FAIL")
            self.assertEqual(result["failed_stage"], "cleanup")
            self.assertTrue(result["cleanup_errors"])
            self.assertTrue((root / "reports/release.json").is_file())
