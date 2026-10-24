"""Explicit acceptance packs: business fixtures stay outside the verification engine."""

from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import Callable


@dataclass(frozen=True)
class AcceptancePack:
    name: str
    validate: Callable
    run_api: Callable
    browser_script: Path


PACKS = {
    "device-borrow": "specforge.acceptance_packs.device_borrow",
    "book-lending": "specforge.acceptance_packs.book_lending",
}


def get_pack(name):
    if name not in PACKS:
        raise ValueError(
            "Choose an explicit --acceptance-pack: " + ", ".join(sorted(PACKS))
        )
    module = import_module(PACKS[name])
    return AcceptancePack(
        name,
        module.validate_spec,
        module.accept,
        Path(module.__file__).with_name("browser.cjs"),
    )
