from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from main import export_final_backend


class ExportFinalBackendTests(unittest.TestCase):
    def test_export_tolerates_locked_transient_log_and_replaces_other_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_root = root / "source"
            destination_root = root / "destination"

            (source_root / "src" / "main" / "java" / "demo").mkdir(parents=True, exist_ok=True)
            (source_root / "logs").mkdir(parents=True, exist_ok=True)
            (source_root / "src" / "main" / "java" / "demo" / "NewFile.java").write_text(
                "class NewFile {}",
                encoding="utf-8",
            )
            (source_root / "logs" / "delivery-validation.yaml").write_text(
                "status: PASS\n",
                encoding="utf-8",
            )
            (source_root / "logs" / "business.log").write_text(
                "fresh runtime log\n",
                encoding="utf-8",
            )

            (destination_root / "src" / "main" / "java" / "demo").mkdir(parents=True, exist_ok=True)
            (destination_root / "logs").mkdir(parents=True, exist_ok=True)
            stale_java = destination_root / "src" / "main" / "java" / "demo" / "Obsolete.java"
            locked_log = destination_root / "logs" / "business.log"
            stale_java.write_text("class Obsolete {}", encoding="utf-8")
            locked_log.write_text("old runtime log\n", encoding="utf-8")

            original_unlink = Path.unlink

            def unlink_with_locked_log(path: Path, *args, **kwargs):  # type: ignore[no-untyped-def]
                if path == locked_log:
                    raise PermissionError("locked log file")
                return original_unlink(path, *args, **kwargs)

            with patch("pathlib.Path.unlink", new=unlink_with_locked_log):
                export_final_backend(source_root, destination_root)

            self.assertFalse(stale_java.exists())
            self.assertTrue((destination_root / "src" / "main" / "java" / "demo" / "NewFile.java").exists())
            self.assertTrue((destination_root / "logs" / "delivery-validation.yaml").exists())
            self.assertTrue(locked_log.exists())
            export_report = destination_root / "logs" / "output-export-report.yaml"
            self.assertTrue(export_report.exists())
            self.assertIn("preserved_transient_paths", export_report.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
