from __future__ import annotations

from pathlib import Path
from typing import Any

from .naming_transformer import NamingTransformer


class ArtifactGraphMutator:
    def __init__(self, naming_transformer: NamingTransformer) -> None:
        self.naming_transformer = naming_transformer

    def rewrite_path(self, source_root: Path, source_file: Path, destination_root: Path) -> tuple[Path, dict[str, Any]]:
        relative_path = source_file.relative_to(source_root)
        rewritten_relative = self.naming_transformer.rename_relative_path(relative_path)
        destination = destination_root / rewritten_relative
        return destination, {
            "source_relative_path": relative_path.as_posix(),
            "destination_relative_path": rewritten_relative.as_posix(),
        }
