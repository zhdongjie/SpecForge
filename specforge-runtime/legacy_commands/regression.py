"""Historical golden regression command."""

from __future__ import annotations

import argparse
from pathlib import Path


def run_regression_suite(args: argparse.Namespace, root: Path) -> None:
    from runtime.golden_validator import GoldenValidator

    summary = GoldenValidator(root).run_regression_suite()
    if summary["failed_count"] > 0:
        raise RuntimeError("Regression suite failed")
