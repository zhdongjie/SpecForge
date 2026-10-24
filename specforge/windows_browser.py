"""Optional native Windows transport; contains no business scenario or generator behavior."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
from .workspace import read_json, write_json


def winpath(path):
    return subprocess.check_output(
        ["wslpath", "-w", str(Path(path).resolve())], text=True
    ).strip()


def execute(runner, script, settings, reports):
    staging = os.environ.get("SPECFORGE_BROWSER_STAGING")
    if not staging:
        win_temp = subprocess.check_output(
            ["/mnt/c/Windows/System32/cmd.exe", "/d", "/c", "echo", "%TEMP%"],
            text=True,
            errors="replace",
        ).strip()
        staging = subprocess.check_output(
            ["wslpath", "-u", win_temp], text=True
        ).strip()
    Path(staging).mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="specforge-browser-", dir=staging) as temp:
        local = Path(temp)
        local_script = local / script.name
        shutil.copyfile(script, local_script)
        support = Path(settings["support"])
        shutil.copyfile(support, local / support.name)
        settings = {
            **settings,
            "reports": winpath(local),
            "support": winpath(local / support.name),
        }
        if os.environ.get("SPECFORGE_BROWSER_QUEUE"):
            # Atomic publication prevents a worker from reading a partially written request.
            write_json(
                local / "request.json",
                {"script": winpath(local_script), "settings": settings},
            )
            (local / "request.json").chmod(0o600)
            deadline = time.monotonic() + 240
            while not (local / "completed.json").exists():
                if time.monotonic() > deadline:
                    raise RuntimeError("Windows browser worker timed out")
                time.sleep(0.5)
            result = read_json(local / "completed.json")
        else:
            process = subprocess.run(
                [runner.node, winpath(local_script)],
                input=json.dumps(settings),
                text=True,
                errors="replace",
                capture_output=True,
                timeout=240,
            )
            result = {
                "returncode": process.returncode,
                "stdout": process.stdout,
                "stderr": process.stderr,
            }
        (reports / "browser-runner.log").write_text(
            result.get("stdout", "") + result.get("stderr", ""), encoding="utf-8"
        )
        for file in local.iterdir():
            if file.name == "browser.json" or file.suffix == ".png":
                shutil.copyfile(file, reports / file.name)
        if result["returncode"]:
            raise RuntimeError(
                "Browser acceptance failed; see browser.json and browser-runner.log"
            )
