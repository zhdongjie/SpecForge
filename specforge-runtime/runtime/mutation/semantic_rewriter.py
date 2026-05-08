from __future__ import annotations

from .naming_transformer import NamingTransformer


class SemanticRewriter:
    def __init__(self, naming_transformer: NamingTransformer) -> None:
        self.naming_transformer = naming_transformer

    def rewrite_text(self, content: str) -> str:
        return self.naming_transformer.rename_text(content)
