from __future__ import annotations

from typing import Any


class PermissionLowering:
    def lower(self, module_schema: dict[str, Any], expanded: dict[str, Any]) -> dict[str, Any]:
        permissions = sorted({capability["authority"] for capability in module_schema.get("capabilities", [])})
        by_aggregate = {
            aggregate: value["authorities"]
            for aggregate, value in sorted(expanded["aggregates"].items(), key=lambda item: item[0])
        }
        return {
            "permissions": permissions,
            "permission_families": by_aggregate,
        }
