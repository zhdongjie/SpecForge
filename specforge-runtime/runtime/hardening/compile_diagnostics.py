from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from runtime.codegen.common import dump_yaml
from runtime.toolchain import resolve_toolchain

from .compile_error_classifier import CompileErrorClassifier


class CompileDiagnostics:
    def __init__(self, project_root: Path, logs_root: Path) -> None:
        self.project_root = project_root
        self.logs_root = logs_root
        self.classifier = CompileErrorClassifier()

    def run(self) -> dict[str, Any]:
        environment = self._resolve_environment()
        if environment["maven_command"] is None:
            diagnostics = {
                "status": "BLOCKED",
                "return_code": None,
                "command": None,
                "environment_binding": environment["binding"],
                "compile_errors": [
                    {
                        "category": "toolchain_unavailable",
                        "message": "Unable to resolve Maven command for deterministic compilation",
                    }
                ],
                "stdout_tail": "",
                "stderr_tail": "",
            }
            dump_yaml(self.logs_root / "compile-diagnostics.yaml", diagnostics)
            return diagnostics
        command = [
            environment["maven_command"],
            "-Dmaven.repo.local=.m2/repository",
            "-DskipTests",
            "clean",
            "compile",
        ]
        completed = subprocess.run(
            command,
            cwd=self.project_root,
            capture_output=True,
            text=True,
            check=False,
            env=environment["env"],
        )
        combined_output = self._combine_output(completed.stdout, completed.stderr)
        diagnostics = {
            "status": "PASS" if completed.returncode == 0 else "FAIL",
            "return_code": completed.returncode,
            "command": command,
            "environment_binding": environment["binding"],
            "compile_errors": self.classifier.classify(combined_output),
            "stdout_tail": completed.stdout[-4000:],
            "stderr_tail": completed.stderr[-4000:],
        }
        if diagnostics["status"] == "FAIL" and not diagnostics["compile_errors"]:
            diagnostics["compile_errors"] = [
                {
                    "category": "unknown_compile_failure",
                    "message": "Compilation failed without normalized classifier coverage",
                }
            ]
        dump_yaml(self.logs_root / "compile-diagnostics.yaml", diagnostics)
        return diagnostics

    def _resolve_environment(self) -> dict[str, Any]:
        return resolve_toolchain(local_repo=".m2/repository")

    def _combine_output(self, stdout: str, stderr: str) -> str:
        return "\n".join(part for part in [stdout, stderr] if part)
