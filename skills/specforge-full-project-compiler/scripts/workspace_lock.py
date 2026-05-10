from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


LOCK_ENV_KEY = "SPECFORGE_WORKSPACE_LOCK_HELD"


@contextmanager
def acquire_workspace_lock(repo_root: Path, owner: str) -> Iterator[None]:
    resolved_root = str(repo_root.resolve())
    if os.environ.get(LOCK_ENV_KEY) == resolved_root:
        yield
        return

    lock_path = repo_root / "specforge-runtime" / ".workspace.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with lock_path.open("x", encoding="utf-8") as handle:
            handle.write(f"{owner}\n")
            handle.write(f"{resolved_root}\n")
    except FileExistsError as exc:
        raise RuntimeError(
            f"SpecForge workspace is busy. Existing lock: {lock_path}. Wait for the current run to finish before starting another."
        ) from exc

    previous = os.environ.get(LOCK_ENV_KEY)
    os.environ[LOCK_ENV_KEY] = resolved_root
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop(LOCK_ENV_KEY, None)
        else:
            os.environ[LOCK_ENV_KEY] = previous
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass
