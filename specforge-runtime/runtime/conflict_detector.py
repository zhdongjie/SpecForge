from __future__ import annotations

from collections import defaultdict
from typing import Any


class ConflictDetector:
    def detect_batch_conflicts(
        self,
        batch_id: str,
        task_artifacts: dict[str, list[dict[str, Any]]],
    ) -> list[dict[str, Any]]:
        artifact_owners: dict[str, list[str]] = defaultdict(list)
        for task_id, artifacts in task_artifacts.items():
            for artifact in artifacts:
                artifact_owners[artifact["artifact_file_name"]].append(task_id)

        conflicts: list[dict[str, Any]] = []
        for artifact_name, owners in sorted(artifact_owners.items()):
            if len(owners) < 2:
                continue
            conflicts.append(
                {
                    "conflict_type": "artifact-ownership-conflict",
                    "batch_id": batch_id,
                    "artifact_file_name": artifact_name,
                    "owners": sorted(owners),
                    "details": f"Multiple tasks plan artifact {artifact_name}",
                }
            )
        return conflicts
