from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ClockStamp:
    execution_tick: int
    logical_order_id: str


class LogicalClock:
    def __init__(self) -> None:
        self._tick = 0

    def next(self, category: str, task_id: str, sequence: int) -> ClockStamp:
        self._tick += 1
        logical_order_id = f"{self._tick:05d}:{sequence:03d}:{category}:{task_id}"
        return ClockStamp(execution_tick=self._tick, logical_order_id=logical_order_id)

    @property
    def current_tick(self) -> int:
        return self._tick
