from __future__ import annotations

from enum import Enum


class TaskState(str, Enum):
    WAITING = "WAITING"
    READY = "READY"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    INVALIDATED = "INVALIDATED"


TERMINAL_STATES = {TaskState.SUCCESS, TaskState.FAILED, TaskState.SKIPPED, TaskState.INVALIDATED}
