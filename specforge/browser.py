"""Browser execution infrastructure. Business steps live only in acceptance packs."""

from dataclasses import dataclass
from importlib.util import find_spec
from pathlib import Path
import json
import os
import shutil
import subprocess
from .workspace import read_json, write_json


@dataclass(frozen=True)
class BrowserRunner:
    node: str
    module: str
    executable: str | None = None
    windows: bool = False

    @classmethod
    def from_environment(cls):
        node = os.environ.get("SPECFORGE_BROWSER_NODE")
        module = os.environ.get("SPECFORGE_PLAYWRIGHT_MODULE")
        if not node or not module:
            installed = find_spec("playwright")
            if installed and installed.origin:
                driver = Path(installed.origin).parent / "driver"
                node = node or str(driver / ("node.exe" if os.name == "nt" else "node"))
                module = module or str(driver / "package")
        if not node or not module:
            raise ValueError(
                "Browser runtime missing: install .[acceptance] and Chromium, or configure SPECFORGE_BROWSER_NODE and SPECFORGE_PLAYWRIGHT_MODULE"
            )
        if not (Path(node).is_file() or shutil.which(node)):
            raise ValueError("Browser Node executable not found: " + node)
        windows = (
            os.name != "nt"
            and node.startswith("/mnt/")
            and node.lower().endswith(".exe")
        )
        if not windows and not Path(module).is_dir():
            raise ValueError("Playwright module directory not found: " + module)
        return cls(
            node, module, os.environ.get("SPECFORGE_CHROMIUM_EXECUTABLE"), windows
        )

    def run(self, script, origin, password, reports, payload):
        reports = Path(reports)
        write_json(reports / "browser.json", {"status": "RUNNING"})
        settings = {
            **payload,
            "origin": origin,
            "password": password,
            "reports": str(reports),
            "module": self.module,
            "support": str(Path(__file__).parent / "assets/browser-support.cjs"),
            "executable": self.executable,
        }
        if self.windows:
            from .windows_browser import execute

            execute(self, Path(script), settings, reports)
        else:
            result = subprocess.run(
                [self.node, str(script)],
                input=json.dumps(settings),
                text=True,
                errors="replace",
                capture_output=True,
                timeout=240,
            )
            (reports / "browser-runner.log").write_text(
                result.stdout + result.stderr, encoding="utf-8"
            )
            if result.returncode:
                raise RuntimeError(
                    "Browser acceptance failed; see browser.json and browser-runner.log"
                )
        if read_json(reports / "browser.json").get("status") != "PASS":
            raise RuntimeError("Browser runner did not produce an acceptance PASS")
        return "PASS"
