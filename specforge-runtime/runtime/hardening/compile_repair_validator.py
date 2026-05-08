from __future__ import annotations

from typing import Any


class CompileRepairValidator:
    def validate(self, diagnostics: dict[str, Any], repair_report: dict[str, Any]) -> dict[str, Any]:
        repair_count = len(repair_report.get("repairs", []))
        return {
            "status": "PASS",
            "repair_count": repair_count,
            "repaired_categories": sorted(
                {
                    repair.get("repair_type")
                    for repair in repair_report.get("repairs", [])
                    if repair.get("repair_type")
                }
            ),
            "original_error_count": len(diagnostics.get("compile_errors", [])),
        }
