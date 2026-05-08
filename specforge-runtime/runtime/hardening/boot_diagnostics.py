from __future__ import annotations

import subprocess
import time
from pathlib import Path
from typing import Any

from runtime.codegen.common import dump_yaml

from .boot_failure_classifier import BootFailureClassifier
from .compile_diagnostics import CompileDiagnostics
from .controller_registration_verifier import ControllerRegistrationVerifier
from .datasource_verifier import DatasourceVerifier
from .mapper_scan_verifier import MapperScanVerifier
from .redis_verifier import RedisVerifier
from .security_boot_verifier import SecurityBootVerifier
from .spring_context_verifier import SpringContextVerifier


class BootDiagnostics:
    START_MARKERS = (
        "Started ",
        "Tomcat started on port",
        "Netty started on port",
    )

    def __init__(self, project_root: Path, logs_root: Path) -> None:
        self.project_root = project_root
        self.logs_root = logs_root
        self.compile_diagnostics = CompileDiagnostics(project_root, logs_root)
        self.failure_classifier = BootFailureClassifier()
        self.spring_context_verifier = SpringContextVerifier()
        self.mapper_scan_verifier = MapperScanVerifier()
        self.controller_registration_verifier = ControllerRegistrationVerifier()
        self.datasource_verifier = DatasourceVerifier()
        self.redis_verifier = RedisVerifier()
        self.security_boot_verifier = SecurityBootVerifier()

    def run(self, timeout_seconds: int = 120) -> dict[str, Any]:
        environment = self.compile_diagnostics._resolve_environment()
        command = [
            environment["maven_command"],
            "-Dmaven.repo.local=.m2/repository",
            "-DskipTests",
            "spring-boot:run",
            "-Dspring-boot.run.arguments=--server.port=0",
        ]
        process = subprocess.Popen(
            command,
            cwd=self.project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=environment["env"],
        )
        output_lines: list[str] = []
        deadline = time.time() + timeout_seconds
        started = False
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
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
        output = "\n".join(output_lines[-300:])
        diagnostics = {
            "status": "PASS" if started else "FAIL",
            "command": command,
            "environment_binding": environment["binding"],
            "boot_failures": [] if started else self.failure_classifier.classify(output),
            "spring_context": self.spring_context_verifier.summarize(output),
            "mapper_scan": self.mapper_scan_verifier.verify(output),
            "controller_registration": self.controller_registration_verifier.verify(output),
            "datasource": self.datasource_verifier.verify(output),
            "redis": self.redis_verifier.verify(output),
            "security": self.security_boot_verifier.verify(output),
            "output_tail": output,
        }
        dump_yaml(self.logs_root / "boot-diagnostics.yaml", diagnostics)
        return diagnostics
