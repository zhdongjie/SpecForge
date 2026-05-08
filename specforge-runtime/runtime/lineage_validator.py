from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from .replay import load_task_records, load_yaml


class LineageValidator:
    def validate(self, run_dir: Path) -> dict[str, Any]:
        findings: list[dict[str, str]] = []
        task_records = load_task_records(run_dir)
        invalidation_report = load_yaml(run_dir / "logs" / "invalidation-report.yaml")

        artifact_owners: dict[str, list[str]] = {}
        for task_id, record in sorted(task_records.items()):
            produced_artifacts = record.get("generated_artifact_lineage", {}).get("produced_artifacts", [])
            current_state = record.get("lifecycle_state", {}).get("current_state")
            for artifact in produced_artifacts:
                artifact_name = artifact.get("artifact_file_name", "")
                if not artifact_name:
                    continue
                artifact_owners.setdefault(artifact_name, []).append(task_id)
                artifact_path = self._resolve_artifact_path(run_dir, artifact)
                if current_state == "SUCCESS":
                    if artifact_path is None or not artifact_path.exists():
                        findings.append(
                            self._finding(
                                "ERROR",
                                "missing-produced-artifact",
                                f"Successful task {task_id} is missing artifact {artifact_name}",
                            )
                        )
                        continue
                    expected_digest = artifact.get("artifact_digest", "")
                    if expected_digest:
                        actual_digest = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
                        if actual_digest != expected_digest:
                            findings.append(
                                self._finding(
                                    "ERROR",
                                    "artifact-digest-mismatch",
                                    f"Artifact digest mismatch for {artifact_name} produced by {task_id}",
                                )
                            )
                elif artifact_path is not None and artifact_path.exists():
                    findings.append(
                        self._finding(
                            "ERROR",
                            "stale-nonterminal-artifact",
                            f"Non-success task {task_id} left artifact {artifact_name} in the artifact set",
                        )
                    )

        for artifact_name, owners in sorted(artifact_owners.items()):
            if len(owners) > 1:
                findings.append(
                    self._finding(
                        "ERROR",
                        "artifact-ownership-duplication",
                        f"Artifact {artifact_name} is owned by multiple tasks: {', '.join(sorted(owners))}",
                    )
                )

        for event in invalidation_report.get("events", []):
            for invalidated_path in event.get("invalidated_artifacts", []):
                if Path(invalidated_path).exists():
                    findings.append(
                        self._finding(
                            "ERROR",
                            "rollback-artifact-still-present",
                            f"Invalidated artifact still exists on disk: {invalidated_path}",
                        )
                    )

        return {
            "validator": "lineage-validator",
            "passed": not any(finding["severity"] == "ERROR" for finding in findings),
            "finding_count": len(findings),
            "findings": findings,
        }

    def _resolve_artifact_path(self, run_dir: Path, artifact: dict[str, Any]) -> Path | None:
        planned_path = artifact.get("planned_path")
        if planned_path:
            candidate = Path(planned_path)
            if candidate.exists():
                return candidate
        artifact_name = artifact.get("artifact_file_name", "")
        if not artifact_name:
            return None
        return run_dir / "artifacts" / artifact_name

    def _finding(self, severity: str, code: str, message: str) -> dict[str, str]:
        return {
            "severity": severity,
            "code": code,
            "message": message,
        }
