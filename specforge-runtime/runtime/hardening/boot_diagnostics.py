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
    DEFAULT_MAX_TIMEOUT_SECONDS = 900
    DEFAULT_IDLE_TIMEOUT_SECONDS = 180

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

    def run(
        self,
        timeout_seconds: int = DEFAULT_MAX_TIMEOUT_SECONDS,
        idle_timeout_seconds: int = DEFAULT_IDLE_TIMEOUT_SECONDS,
    ) -> dict[str, Any]:
        environment = self.compile_diagnostics._resolve_environment()
        command = [
            environment["maven_command"],
            "-ntp",
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
        started = False
        start_time = time.time()
        deadline = start_time + timeout_seconds
        last_output_at = start_time
        failure_reason = ""
        try:
            while time.time() < deadline:
                line = process.stdout.readline() if process.stdout is not None else ""
                if line:
                    output_lines.append(line.rstrip())
                    last_output_at = time.time()
                    if any(marker in line for marker in self.START_MARKERS):
                        started = True
                        break
                elif process.poll() is None and time.time() - last_output_at >= idle_timeout_seconds:
                    failure_reason = "startup-idle-timeout"
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
        elapsed_seconds = round(time.time() - start_time, 3)
        if not started and not failure_reason and process.poll() is None:
            failure_reason = "startup-timeout"
        elif not started and not failure_reason and process.poll() is not None:
            failure_reason = "process-exited-before-start"
        diagnostics = {
            "status": "PASS" if started else "FAIL",
            "command": command,
            "environment_binding": environment["binding"],
            "timeout_seconds": timeout_seconds,
            "idle_timeout_seconds": idle_timeout_seconds,
            "elapsed_seconds": elapsed_seconds,
            "failure_reason": None if started else failure_reason,
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
