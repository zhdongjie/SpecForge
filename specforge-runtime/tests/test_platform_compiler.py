from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.platform_compiler import ProjectCompiler
from runtime.replay import load_yaml

SPECS_DIR = ROOT / "specs"
BACKEND_ROOT = ROOT.parent / "backend"


class PlatformCompilerTests(unittest.TestCase):
    def test_project_compiler_assembles_bootable_backend_layout(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_root = Path(temp_dir) / "backend-compile"
            summary = ProjectCompiler(
                project_root=ROOT.parent,
                backend_root=BACKEND_ROOT,
                run_root=run_root,
                specs_dir=SPECS_DIR,
            ).run(run_compile=False, run_boot=False)

            self.assertEqual(summary["status"], "PASS")
            platform_schema = load_yaml(run_root / "generated-ir" / "platform-schema.generated.yaml")
            assembly_report = load_yaml(run_root / "generated-project" / "logs" / "assembly-report.yaml")
            self.assertEqual(platform_schema["security"]["auth_type"], "jwt")
            self.assertEqual(assembly_report["infrastructure_status"], "PASS")
            self.assertTrue((run_root / "generated-project" / "pom.xml").exists())
            self.assertTrue((run_root / "generated-project" / "src" / "main" / "resources" / "application.yml").exists())
            self.assertTrue(
                (
                    run_root
                    / "generated-project"
                    / "src"
                    / "main"
                    / "java"
                    / "org"
                    / "eu"
                    / "originalkeen"
                    / "BackendApplication.java"
                ).exists()
            )


if __name__ == "__main__":
    unittest.main()
