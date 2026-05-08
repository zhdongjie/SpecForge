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
- Treat `specforge-runtime/outputs/` as the stable home for final exported backend code after a successful auto-build.

Business module rule:
- Modules with `semantic_role: business-domain` must use `org.eu.originalkeen.business.*` as `package_root`.
- Business-domain routes should use `/v1/business/*`.
- Business-domain authorities should use `business:*`.
- `system/*` is reserved for platform and administrative modules, not new business modules.
