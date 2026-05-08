from __future__ import annotations

from pathlib import Path
from typing import Any

from .replay import compare_traces, load_run_trace, load_yaml


class ReplayValidator:
    def validate(
        self,
        run_dir: Path,
        replay_source_run_id: str | None = None,
        affected_tasks: set[str] | None = None,
    ) -> dict[str, Any]:
        findings: list[dict[str, str]] = []
        comparison_path = run_dir / "logs" / "replay-comparison.yaml"
        if replay_source_run_id is None:
            return {
                "validator": "replay-validator",
                "passed": True,
                "finding_count": 0,
                "findings": findings,
                "comparison_checked": False,
            }

        comparison = load_yaml(comparison_path)
        runs_root = run_dir.parent
        baseline_run_dir = runs_root / replay_source_run_id
        baseline_trace = load_run_trace(baseline_run_dir)
        current_trace = load_run_trace(run_dir)
        subset = affected_tasks if affected_tasks else None
        recomputed = compare_traces(baseline_trace, current_trace, task_subset=subset)
        if not comparison:
            comparison = recomputed
            findings.append(
                self._finding(
                    "WARNING",
                    "missing-replay-comparison",
                    "Replay comparison file is missing; validation fell back to recomputed traces",
                )
            )
        if comparison.get("match") is not True:
            findings.append(
                self._finding(
                    "ERROR",
                    "replay-match-failed",
                    f"Replay comparison reported mismatch: {comparison.get('differences', [])}",
                )
            )
        if comparison.get("baseline_signature") != recomputed.get("baseline_signature"):
            findings.append(
                self._finding(
                    "ERROR",
                    "baseline-signature-drift",
                    "Stored baseline replay signature does not match recomputed signature",
                )
            )
        if comparison.get("current_signature") != recomputed.get("current_signature"):
            findings.append(
                self._finding(
                    "ERROR",
                    "current-signature-drift",
                    "Stored current replay signature does not match recomputed signature",
                )
            )

        return {
            "validator": "replay-validator",
            "passed": not any(finding["severity"] == "ERROR" for finding in findings),
            "finding_count": len(findings),
            "findings": findings,
            "comparison_checked": True,
        }

    def _finding(self, severity: str, code: str, message: str) -> dict[str, str]:
        return {
            "severity": severity,
            "code": code,
            "message": message,
        }
