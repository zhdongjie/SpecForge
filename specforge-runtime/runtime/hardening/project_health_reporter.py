from __future__ import annotations

from pathlib import Path
from typing import Any

from runtime.codegen.common import dump_yaml


class ProjectHealthReporter:
    def __init__(self, logs_root: Path) -> None:
        self.logs_root = logs_root

    def write(
        self,
        compile_diagnostics: dict[str, Any],
        compile_repair_report: dict[str, Any],
        boot_diagnostics: dict[str, Any],
        boot_repair_report: dict[str, Any],
        compile_repair_validation: dict[str, Any],
        boot_repair_validation: dict[str, Any],
        deterministic_validation: dict[str, Any],
    ) -> dict[str, Any]:
        compile_status = compile_diagnostics.get("status", "UNKNOWN")
        compile_post_repair = compile_repair_report.get("post_repair_status", compile_status)
        boot_status = boot_diagnostics.get("status", "SKIPPED")
        boot_post_repair = boot_repair_report.get("post_repair_status", boot_status)
        overall = "PASS" if compile_post_repair == "PASS" and boot_post_repair in {"PASS", "SKIPPED"} else "FAIL"
        report = {
            "status": overall,
            "compile_status": compile_status,
            "compile_post_repair_status": compile_post_repair,
            "boot_status": boot_status,
            "boot_post_repair_status": boot_post_repair,
            "compile_error_count": len(compile_diagnostics.get("compile_errors", [])),
            "boot_failure_count": len(boot_diagnostics.get("boot_failures", [])),
            "compile_repair_validation": compile_repair_validation,
            "boot_repair_validation": boot_repair_validation,
            "deterministic_repair_validation": deterministic_validation,
        }
        dump_yaml(self.logs_root / "project-health-report.yaml", report)
        return report
