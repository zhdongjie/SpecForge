from __future__ import annotations

from typing import Any


class SpringContextVerifier:
    def summarize(self, output: str) -> dict[str, Any]:
        return {
            "started": "Started " in output,
            "bean_creation_failure": "Error creating bean" in output,
            "controller_mapping_conflict": "Ambiguous mapping" in output,
        }
