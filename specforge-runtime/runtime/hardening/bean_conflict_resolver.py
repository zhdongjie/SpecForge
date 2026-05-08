from __future__ import annotations

from typing import Any


class BeanConflictResolver:
    def repair(self, diagnostics: list[dict[str, Any]]) -> list[dict[str, Any]]:
        repairs: list[dict[str, Any]] = []
        for finding in diagnostics:
            if finding.get("category") == "bean_conflict":
                repairs.append(
                    {
                        "repair_type": "bean_conflict_deferred",
                        "status": "NO_OP",
                        "reason": "No deterministic bean rename strategy matched the failure",
                    }
                )
        return repairs
