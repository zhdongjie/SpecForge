This directory is the canonical home for SpecForge compiler inputs.

Primary inputs:
- `project-spec.md`
- `module-spec.yaml`
- `module-schema.resolved.yaml`
- `generation-task-graph.yaml`
- `field-schema.resolved.yaml`
- `mutation-spec.yaml`

Examples:
- `examples/task-run-record.example.yaml`

Working rule:
- Put runtime-facing specs here instead of the repository root.
- Keep generated run outputs under `specforge-runtime/runs/`, which is ignored.
