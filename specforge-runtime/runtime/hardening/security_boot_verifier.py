from __future__ import annotations

from typing import Any


class SecurityBootVerifier:
    def verify(self, output: str) -> dict[str, Any]:
        return {
            "status": "FAIL" if "SecurityFilterChain" in output and "BeanCreationException" in output else "PASS",
        }
