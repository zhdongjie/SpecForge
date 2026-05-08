from __future__ import annotations

import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

from runtime.codegen.common import dump_yaml


class BootVerifier:
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root

    def verify(self, run_compile: bool = True, run_boot: bool = True) -> dict[str, Any]:
        compile_check = self.compile_check() if run_compile else {"status": "SKIPPED"}
        if compile_check["status"] in {"FAIL", "BLOCKED"}:
            boot_check = {"status": "BLOCKED", "reason": "compile-failed"}
        else:
            boot_check = self.boot_check() if run_boot else {"status": "SKIPPED"}
        dump_yaml(self.project_root / "logs" / "compile-check.yaml", compile_check)
        dump_yaml(self.project_root / "logs" / "boot-check.yaml", boot_check)
        return {"compile_check": compile_check, "boot_check": boot_check}

    def compile_check(self) -> dict[str, Any]:
        mvn_command = self._find_maven()
        if mvn_command is None:
            return {"status": "SKIPPED", "reason": "maven-not-found"}
        completed = subprocess.run(
            [mvn_command, "-q", "-DskipTests", "clean", "compile"],
            cwd=self.project_root,
            capture_output=True,
            text=True,
            check=False,
        )
        result = {
            "status": "PASS" if completed.returncode == 0 else "FAIL",
            "return_code": completed.returncode,
            "command": mvn_command,
            "stdout": completed.stdout[-4000:],
            "stderr": completed.stderr[-4000:],
        }
        combined_output = f"{result['stdout']}\n{result['stderr']}"
        if completed.returncode != 0 and ("_remote.repositories" in combined_output or "拒绝访问" in combined_output or "Access is denied" in combined_output):
            result["status"] = "BLOCKED"
            result["reason"] = "maven-local-repository-permission"
        return result

    def boot_check(self, timeout_seconds: int = 45) -> dict[str, Any]:
        mvn_command = self._find_maven()
        if mvn_command is None:
            return {"status": "SKIPPED", "reason": "maven-not-found"}

        process = subprocess.Popen(
            [mvn_command, "-q", "-DskipTests", "spring-boot:run", "-Dspring-boot.run.arguments=--server.port=0"],
            cwd=self.project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        started = False
        output_lines: list[str] = []
        deadline = time.time() + timeout_seconds
        try:
            while time.time() < deadline:
                line = process.stdout.readline() if process.stdout is not None else ""
                if line:
                    output_lines.append(line.rstrip())
                    if "Started " in line:
                        started = True
                        break
                if process.poll() is not None and not line:
                    break
            if started:
                return {
                    "status": "PASS",
                    "command": mvn_command,
                    "output": "\n".join(output_lines[-200:]),
                }
            if process.poll() is None:
                return {
                    "status": "FAIL",
                    "command": mvn_command,
                    "reason": "startup-timeout",
                    "output": "\n".join(output_lines[-200:]),
                }
            return {
                "status": "FAIL",
                "command": mvn_command,
                "return_code": process.returncode,
                "output": "\n".join(output_lines[-200:]),
            }
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()

    def _find_maven(self) -> str | None:
        preferred_commands = [Path(r"E:\Dev\Maven\apache-maven-3.9.6\bin\mvn.cmd")]
        for candidate in preferred_commands:
            if candidate.exists():
                return str(candidate)
        return shutil.which("mvn.cmd") or shutil.which("mvn")
