This directory is the canonical home for SpecForge compiler inputs.

Primary inputs:
- `build-plan.yaml`
- `project-assembly-plan.yaml`
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
- Use `project-assembly-plan.yaml` to describe the project-level module sequence and platform contracts for multi-module growth.

Portability rule:
- Do not hardcode local JDK or Maven paths in runtime components.
- Prefer `SPECFORGE_JAVA_HOME` and `SPECFORGE_MAVEN_CMD` when moving to a new machine.
- See `docs/ENVIRONMENT_MIGRATION_RUNBOOK.md` for the migration contract.

Business module rule:
- Modules with `semantic_role: business-domain` must use `org.eu.originalkeen.business.*` as `package_root`.
- Business-domain routes should use `/v1/business/*`.
- Business-domain authorities should use `business:*`.
- `system/*` is reserved for platform and administrative modules, not new business modules.
