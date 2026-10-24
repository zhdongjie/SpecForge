"""Explicit application extensions; no inference from requirement keywords."""

from importlib import import_module

REGISTRY = {"recipe-management": "specforge.applications.recipe_management"}


def get_application(name):
    if not isinstance(name, str) or name not in REGISTRY:
        raise ValueError("unsupported application extension: " + str(name))
    return import_module(REGISTRY[name])
