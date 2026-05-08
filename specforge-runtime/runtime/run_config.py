from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FailureInjection:
    task_id: str
    failure_type: str = "validation"
    attempt: int = 1
    message: str = "Injected runtime failure"


@dataclass(frozen=True)
class RunConfig:
    run_id: str
    replay_source_run_id: str | None = None
    partial_replay_tasks: tuple[str, ...] = ()
    halt_on_validation_failure: bool = True
    compare_trace: bool = False
    failure_injections: tuple[FailureInjection, ...] = ()
    max_workers: int = 4

    @property
    def mode(self) -> str:
        if self.partial_replay_tasks:
            return "partial-replay"
        if self.replay_source_run_id:
            return "deterministic-replay"
        return "fresh"

    def injections_for(self, task_id: str, attempt: int) -> list[FailureInjection]:
        return [
            injection
            for injection in self.failure_injections
            if injection.task_id == task_id and injection.attempt == attempt
        ]
