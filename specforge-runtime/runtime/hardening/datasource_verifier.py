from __future__ import annotations

from typing import Any


class DatasourceVerifier:
    def verify(self, output: str) -> dict[str, Any]:
        return {
            "status": "FAIL" if "Failed to configure a DataSource" in output else "PASS",
        }
