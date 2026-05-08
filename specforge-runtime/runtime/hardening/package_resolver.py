from __future__ import annotations

from typing import Any


class PackageResolver:
    def normalize(self, diagnostics: list[dict[str, Any]]) -> list[dict[str, Any]]:
        repairs: list[dict[str, Any]] = []
        for finding in diagnostics:
            if finding.get("category") == "package_mismatch":
                repairs.append(
                    {
                        "repair_type": "package_normalization_deferred",
                        "status": "NO_OP",
                        "reason": "No deterministic package relocation rule was applicable",
                    }
                )
        return repairs
