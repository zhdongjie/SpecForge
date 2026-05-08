from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from runtime.codegen.common import read_text, write_text


class ImportResolver:
    def repair_permission_constant_symbol(self, file_path: Path, symbol: str | None) -> dict[str, Any] | None:
        if not file_path.exists():
            return None
        source = read_text(file_path)
        if symbol and "-" not in symbol and "-" not in source:
            return None
        normalized = re.sub(r"([A-Z0-9_]+(?:-[A-Z0-9_]+)+)", lambda m: m.group(1).replace("-", "_"), source)
        if normalized == source:
            return None
        write_text(file_path, normalized)
        return {
            "repair_type": "permission_constant_normalization",
            "file": str(file_path),
            "before_symbol": symbol,
            "after_symbol": symbol.replace("-", "_") if symbol else None,
        }
