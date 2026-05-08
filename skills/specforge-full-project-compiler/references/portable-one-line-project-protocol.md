# Portable One-Line Project Protocol

Use this protocol when the user wants:

- a skill that works in a fresh environment
- a single sentence or a requirement document as input
- full autonomous generation without step-by-step chat guidance

## Goal

Make another Codex session succeed with only:

- the repository
- the skill
- the toolchain
- a requirement

and no dependence on earlier conversation context.

## Required Execution Shape

1. Read repository orientation files first.
2. Verify workspace readiness.
3. Normalize the requirement into a project-level scope.
4. Scaffold canonical specs into `specforge-runtime/specs/`.
5. Run canonical auto-build.
6. Return only:
   - final exported backend path on success
   - or reproducible failure bundle path on failure

## Required Orientation Files

- `README.md`
- `WORKSPACE_LAYOUT.md`
- `specforge-runtime/docs/PROJECT_COMPILER_PROTOCOL.md`
- `specforge-runtime/docs/ENVIRONMENT_MIGRATION_RUNBOOK.md`

## Directory Contract

- `backend/`
  - assembly input template
- `specforge-runtime/specs/`
  - canonical compiler inputs
- `specforge-runtime/runs/<run-id>/`
  - per-attempt trace and diagnostics
- `specforge-runtime/outputs/<target>/`
  - final generated backend
- `sandbox/`
  - local-only scratch area

## Prompt Contract

The portable operator prompt should be short and explicit.

Recommended shape:

```text
Use $specforge-full-project-compiler in this repository.
Read the repository orientation docs.
Compile a complete Spring Boot backend from this requirement.
Run until compile and boot pass, or return a reproducible failure bundle.
Treat specforge-runtime/outputs/ as the only final deliverable.
```

## Completion Contract

Success requires:

- `compile_status: PASS`
- `boot_status: PASS`
- final backend under `specforge-runtime/outputs/`

Failure requires preserving:

- `compile-diagnostics.yaml`
- `compile-repair-report.yaml`
- `boot-diagnostics.yaml`
- `boot-repair-report.yaml`
- `project-health-report.yaml`
- `auto-build-report.yaml`
