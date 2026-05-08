This directory is the canonical home for SpecForge compiler inputs.

Primary inputs:
- `build-plan.yaml`
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
- Use `python main.py --auto-build --build-plan build-plan.yaml` for the canonical end-to-end backend compilation run.
