# Handoff Checklist

Use this checklist before handing the repository to another machine, another Codex session, or your future self.

## Minimum Files To Read

- `README.md`
- `WORKSPACE_LAYOUT.md`
- `specforge-runtime/docs/PROJECT_COMPILER_PROTOCOL.md`
- `specforge-runtime/docs/ENVIRONMENT_MIGRATION_RUNBOOK.md`
- `specforge-runtime/docs/ONE_LINE_REQUIREMENT_PLAYBOOK.md`
- `specforge-runtime/docs/CODEX_STARTER_PROMPTS.md`
- `specforge-runtime/docs/REQUIREMENT_TEMPLATE.md`

## Minimum Files To Carry

- `backend/`
- `specforge-runtime/`
- `skills/specforge-full-project-compiler/`
- current canonical specs under `specforge-runtime/specs/`

## Toolchain Checks

- JDK 17+ available
- Maven 3.9+ available
- `java -version` works
- `mvn -version` works

## Readiness Check

Run:

```powershell
python skills/specforge-full-project-compiler/scripts/check_specforge_workspace.py --repo-root .
```

Expected:

- `"ready": true`

## Final Deliverable Rule

If someone asks "which directory is the real output?", the answer is:

- `specforge-runtime/outputs/<project-backend>/`

Everything else is either:

- template input
- execution trace
- or scratch space

## Fastest Single Command

```powershell
python skills/specforge-full-project-compiler/scripts/run_requirement_project.py --repo-root . --project-name "<project-name>" --requirement "<one-line requirement>" --run-id <run-id> --force
```

## Failure Preservation Rule

If the generation does not pass compile or boot, preserve:

- `auto-build-report.yaml`
- `project-health-report.yaml`
- `compile-diagnostics.yaml`
- `compile-repair-report.yaml`
- `boot-diagnostics.yaml`
- `boot-repair-report.yaml`
