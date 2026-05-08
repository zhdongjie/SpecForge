from __future__ import annotations

from typing import Any


class MapperScanVerifier:
    def verify(self, output: str) -> dict[str, Any]:
        return {
            "status": "FAIL" if "Mapper" in output and "not found" in output else "PASS",
        }
