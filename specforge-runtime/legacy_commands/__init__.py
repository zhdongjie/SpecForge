"""Lazy dispatch for compatibility commands; importing loads no runtime modules."""

from __future__ import annotations

import argparse
from pathlib import Path

# Preserve the original precedence when more than one historical flag is set.
MODULE_COMMANDS = (
    "emit_code",
    "mutate_module",
    "synthesize_module",
    "lower_ir",
    "compile_backend",
    "harden_backend",
)


def dispatch(args: argparse.Namespace, root: Path) -> bool:
    for name in MODULE_COMMANDS:
        if getattr(args, name):
            from . import modules

            getattr(modules, "run_" + name)(args, root)
            return True
    if args.run_regression_suite:
        from .regression import run_regression_suite

        run_regression_suite(args, root)
        return True
    return False
