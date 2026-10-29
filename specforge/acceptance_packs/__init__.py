"""Explicit acceptance packs: business fixtures stay outside the verification engine."""

from dataclasses import dataclass
from importlib import import_module
import re
from pathlib import Path
from typing import Callable


@dataclass(frozen=True)
class AcceptancePack:
    name: str
    validate: Callable
    run_api: Callable
    browser_script: Path


PACKS = {
    "recipe-management": "specforge.acceptance_packs.recipe_management",
    "device-borrow": "specforge.acceptance_packs.device_borrow",
    "book-lending": "specforge.acceptance_packs.book_lending",
    "book-lending-fields": "specforge.acceptance_packs.book_lending_fields",
}


def get_pack(name):
    # Explicit code plugin, imported only at the user's CLI request. Specs cannot load code.
    if isinstance(name, str) and name.startswith("python:"):
        module_name = name[len("python:"):]
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*", module_name):
            raise ValueError("invalid external acceptance module name")
    elif name in PACKS:
        module_name = PACKS[name]
    else:
        raise ValueError("Choose an explicit --acceptance-pack: " + ", ".join(sorted(PACKS)) + "; or python:your_module")
    module = import_module(module_name)
    validate = getattr(module, "validate_spec", None)
    accept = getattr(module, "accept", None)
    if not callable(validate) or not callable(accept):
        raise ValueError("acceptance module requires callable validate_spec and accept")
    script = Path(getattr(module, "BROWSER_SCRIPT", Path(module.__file__).with_name("browser.cjs"))).resolve()
    if not script.is_file():
        raise ValueError("acceptance browser script missing: " + str(script))
    return AcceptancePack(name, validate, accept, script)
