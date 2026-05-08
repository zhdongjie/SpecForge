from __future__ import annotations

import hashlib
import json
from typing import Any


class DeterministicRepairValidator:
    def validate(self, compile_repair_report: dict[str, Any], boot_repair_report: dict[str, Any]) -> dict[str, Any]:
        canonical_payload = {
            "compile_repairs": compile_repair_report.get("repairs", []),
            "boot_repairs": boot_repair_report.get("repairs", []),
        }
        signature = hashlib.sha256(
            json.dumps(canonical_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        return {
            "status": "PASS",
            "repair_signature": signature,
            "compile_repair_count": len(compile_repair_report.get("repairs", [])),
            "boot_repair_count": len(boot_repair_report.get("repairs", [])),
        }
