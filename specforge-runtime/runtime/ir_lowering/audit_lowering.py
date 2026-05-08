from __future__ import annotations

from typing import Any


class AuditLowering:
    def lower(self, module_schema: dict[str, Any], entities: dict[str, dict[str, Any]]) -> dict[str, Any]:
        operate_log = module_schema.get("audit_behavior", {}).get("operate_log", {})
        return {
            "audit_contract": {
                "enabled": True,
                "soft_delete": True,
                "fields": ["createdTime", "createdBy", "lastModifiedTime", "lastModifiedBy", "deleted"],
                "operate_log_enabled": bool(operate_log.get("enabled")),
                "operate_log_capabilities": sorted(operate_log.get("target_capabilities", [])),
            }
        }
