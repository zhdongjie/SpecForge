from __future__ import annotations

from typing import Any


class RedisVerifier:
    def verify(self, output: str) -> dict[str, Any]:
        return {
            "status": "FAIL" if "RedisConnectionFailureException" in output else "PASS",
        }
