# New Machine Quickstart

Use this when you want the shortest reliable path on a fresh machine.

## Goal

Start from:

- repository checkout
- Codex
- one-line or one-file requirement

End at:

- `specforge-runtime/outputs/<project-backend>/`
- `delivery-validation.yaml status: PASS`
- `business-contract-validation.yaml validation.status: PASS`
- `sql-asset-validation.yaml status: PASS`
- `auth-surface-validation.yaml status: PASS`

## Minimum Environment

- JDK 17+
- Maven 3.9+

Recommended environment variables:

- `SPECFORGE_JAVA_HOME`
- `SPECFORGE_MAVEN_CMD`

Optional Codex auto-discovery install:

- copy `skills/specforge-full-project-compiler/`
- into `C:\Users\<username>\.codex\skills\specforge-full-project-compiler\`

## Fastest Commands

### 1. Readiness

```powershell
python skills/specforge-full-project-compiler/scripts/check_specforge_workspace.py --repo-root .
```

Accept only:

- `"ready": true`

Run one generation job at a time in the same repository workspace.

The wrapper now enforces a workspace lock under:

- `specforge-runtime/.workspace.lock`

### 2. One-command generation

```powershell
python skills/specforge-full-project-compiler/scripts/run_requirement_project.py --repo-root . --project-name "<project-name>" --requirement "<one-line requirement>" --run-id <run-id> --force
```

Or with a requirement file:

```powershell
python skills/specforge-full-project-compiler/scripts/run_requirement_project.py --repo-root . --project-name "<project-name>" --requirement-file "<requirement-file>" --run-id <run-id> --force
```

### 3. Outcome summary

```powershell
python skills/specforge-full-project-compiler/scripts/summarize_specforge_outcome.py --repo-root . --run-id <run-id>
```

## Success Rule

Accept success only if the summary says:

- `compile_status: PASS`
- `boot_status: PASS`
- `delivery_validation_status: PASS`
- `business_contract_status: PASS`
- `sql_asset_status: PASS`
- `auth_surface_status: PASS`

Final deliverable:

- `specforge-runtime/outputs/<project-backend>/`

Operational note:

- do not start two `run_requirement_project.py` or `run_specforge_autobuild.py` jobs in parallel against the same repository checkout
- if a previous run crashes, confirm `specforge-runtime/.workspace.lock` is gone before retrying

## Failure Rule

If the run fails, use the printed failure bundle from the summary output.

The most important files are:

- `specforge-runtime/runs/<run-id>/logs/auto-build-report.yaml`
- `specforge-runtime/runs/<run-id>/generated-project/logs/project-health-report.yaml`
- `specforge-runtime/runs/<run-id>/generated-project/logs/compile-diagnostics.yaml`
- `specforge-runtime/runs/<run-id>/generated-project/logs/boot-diagnostics.yaml`

## One-Line Codex Prompt

```text
Use $specforge-full-project-compiler in this repository. Read README.md, WORKSPACE_LAYOUT.md, and specforge-runtime/docs/ENVIRONMENT_MIGRATION_RUNBOOK.md. Then generate a complete Spring Boot backend from my requirement, run until compile, boot, business contract validation, delivery validation, SQL asset validation, and auth surface validation all pass, and treat specforge-runtime/outputs/ as the only final deliverable.
```
