from __future__ import annotations

import subprocess
import time
from pathlib import Path
from typing import Any

from runtime.codegen.common import dump_yaml
from runtime.toolchain import resolve_toolchain


class BootVerifier:
    START_MARKERS = (
        "Started ",
        "Tomcat started on port",
        "Netty started on port",
    )

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
        toolchain = resolve_toolchain()
        mvn_command = toolchain["maven_command"]
        if mvn_command is None:
            return {
                "status": "SKIPPED",
                "reason": "maven-not-found",
                "environment_binding": toolchain["binding"],
            }
        completed = subprocess.run(
            [mvn_command, "-q", "-DskipTests", "clean", "compile"],
            cwd=self.project_root,
            capture_output=True,
            text=True,
            check=False,
            env=toolchain["env"],
        )
        result = {
            "status": "PASS" if completed.returncode == 0 else "FAIL",
            "return_code": completed.returncode,
            "command": mvn_command,
            "environment_binding": toolchain["binding"],
            "stdout": completed.stdout[-4000:],
            "stderr": completed.stderr[-4000:],
        }
        combined_output = f"{result['stdout']}\n{result['stderr']}"
        if completed.returncode != 0 and ("_remote.repositories" in combined_output or "拒绝访问" in combined_output or "Access is denied" in combined_output):
            result["status"] = "BLOCKED"
            result["reason"] = "maven-local-repository-permission"
        return result

    def boot_check(self, timeout_seconds: int = 120) -> dict[str, Any]:
        toolchain = resolve_toolchain()
        mvn_command = toolchain["maven_command"]
        if mvn_command is None:
            return {
                "status": "SKIPPED",
                "reason": "maven-not-found",
                "environment_binding": toolchain["binding"],
            }

        process = subprocess.Popen(
            [mvn_command, "-q", "-DskipTests", "spring-boot:run", "-Dspring-boot.run.arguments=--server.port=0"],
            cwd=self.project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=toolchain["env"],
        )
        started = False
        output_lines: list[str] = []
        deadline = time.time() + timeout_seconds
        try:
            while time.time() < deadline:
                line = process.stdout.readline() if process.stdout is not None else ""
                if line:
                    output_lines.append(line.rstrip())
                    if any(marker in line for marker in self.START_MARKERS):
                        started = True
                        break
                if process.poll() is not None and not line:
                    break
            if started:
                return {
                    "status": "PASS",
                    "command": mvn_command,
                    "environment_binding": toolchain["binding"],
                    "output": "\n".join(output_lines[-200:]),
                }
            if process.poll() is None:
                return {
                    "status": "FAIL",
                    "command": mvn_command,
                    "environment_binding": toolchain["binding"],
                    "reason": "startup-timeout",
                    "output": "\n".join(output_lines[-200:]),
                }
            return {
                "status": "FAIL",
                "command": mvn_command,
                "environment_binding": toolchain["binding"],
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
