from __future__ import annotations

from typing import Any


class ControllerRegistrationVerifier:
    def verify(self, output: str) -> dict[str, Any]:
        return {
            "status": "FAIL" if "Ambiguous mapping" in output else "PASS",
        }
