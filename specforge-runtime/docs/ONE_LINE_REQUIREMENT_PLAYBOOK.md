# One-Line Requirement Playbook

This document defines the portable operator protocol for:

- one project name
- or one paragraph requirement
- to one bootable Spring Boot backend

without depending on prior conversation history.

## Contract

Input:

- a project name
- or a short business requirement
- or a requirements document

Output:

- a bootable backend under `specforge-runtime/outputs/<project-backend>/`
- or a reproducible failure bundle under `specforge-runtime/runs/<run-id>/logs/`

## Hard Rules

- Treat `specforge-runtime/specs/build-plan.yaml` as the canonical execution entry.
- Treat `specforge-runtime/outputs/` as the only final deliverable location.
- Treat `specforge-runtime/runs/` as execution evidence, not the product.
- Treat `backend/` as template input, not output.
- Accept success only if compile and boot both pass.

## Operator Steps

### 1. Open the repository root

```powershell
cd E:\Project\Generate\SpecForge
```

### 2. Verify workspace readiness

```powershell
python skills/specforge-full-project-compiler/scripts/check_specforge_workspace.py --repo-root .
```

Required result:

- `"ready": true`

### 3. Scaffold from a one-line requirement

```powershell
python skills/specforge-full-project-compiler/scripts/scaffold_requirement_project.py --repo-root . --project-name "<project-name>" --requirement "<requirement>" --force
```

Example:

```powershell
python skills/specforge-full-project-compiler/scripts/scaffold_requirement_project.py --repo-root . --project-name "Laboratory Management Platform" --requirement "Build a complete modular-monolith Spring Boot laboratory management backend covering laboratory resources, experiment projects, equipment, consumables, reservations, approvals, access control, notifications, schedule calendar, and statistics reporting." --force
```

### 4. Run the canonical auto-build

```powershell
python skills/specforge-full-project-compiler/scripts/run_specforge_autobuild.py --repo-root . --run-id <run-id>
```

### 5. Inspect success or failure

Required success files:

- `specforge-runtime/runs/<run-id>/logs/auto-build-report.yaml`
- `specforge-runtime/runs/<run-id>/generated-project/logs/project-health-report.yaml`

Required success conditions:

- `compile_status: PASS`
- `boot_status: PASS`

Final product:

- `specforge-runtime/outputs/<project-backend>/`

### 6. If failure occurs

Do not treat the generated code as final.

Read:

- `compile-diagnostics.yaml`
- `compile-repair-report.yaml`
- `boot-diagnostics.yaml`
- `boot-repair-report.yaml`
- `project-health-report.yaml`
- `auto-build-report.yaml`

Repair specs or compiler inputs first, then rerun with a new `run-id`.

## Codex Prompt Contract

For a new Codex session, the minimal portable prompt can be:

```text
Use $specforge-full-project-compiler in this repository.
Read README.md, WORKSPACE_LAYOUT.md, and specforge-runtime/docs/ENVIRONMENT_MIGRATION_RUNBOOK.md.
Then compile a complete Spring Boot backend from this requirement:
<requirement>
Run until compile and boot both pass, or return a reproducible failure bundle.
Treat specforge-runtime/outputs/ as the only final deliverable.
```

Additional ready-to-use prompt variants are collected in:

- `specforge-runtime/docs/CODEX_STARTER_PROMPTS.md`

## Directory Interpretation

- `backend/`
  - stable assembly baseline
- `specforge-runtime/specs/`
  - canonical input specs
- `specforge-runtime/runs/<run-id>/`
  - one build attempt with full evidence
- `specforge-runtime/outputs/<project-backend>/`
  - final backend to hand off or continue development on
- `sandbox/`
  - local scratch area

## Graduation-Project Scope Rule

When the requirement asks for a complete platform, do not stop at a small CRUD skeleton.

Prefer a business-center level split, such as:

- domain resource center
- business transaction center
- approval center
- notification center
- reporting center

and include:

- user/role/menu linkage as a project-level concern
- database initialization SQL organization as a project-level concern
