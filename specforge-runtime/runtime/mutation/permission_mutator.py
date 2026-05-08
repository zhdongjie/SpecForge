from __future__ import annotations

from typing import Any

from .semantic_rewriter import SemanticRewriter


class PermissionMutator:
    def __init__(self, rewriter: SemanticRewriter) -> None:
        self.rewriter = rewriter

    def mutate(self, content: str) -> tuple[str, dict[str, Any]]:
        rewritten = self.rewriter.rewrite_text(content)
        return rewritten, {"permission_rewrite_applied": rewritten != content}
