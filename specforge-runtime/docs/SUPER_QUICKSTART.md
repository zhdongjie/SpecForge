# Super Quickstart

This is the shortest reliable path for a new machine, a fresh Codex session, or a zero-context handoff.

## What You Need

- JDK 17+
- Maven 3.9+
- this repository

Optional but recommended:

- set `SPECFORGE_JAVA_HOME`
- set `SPECFORGE_MAVEN_CMD`

If you want Codex to auto-discover the skill on a fresh machine, also copy:

- `skills/specforge-full-project-compiler/`

to:

- `C:\Users\<username>\.codex\skills\specforge-full-project-compiler\`

## Only Three Commands

### 1. Check the workspace

```powershell
python skills/specforge-full-project-compiler/scripts/check_specforge_workspace.py --repo-root .
```

Accept only:

- `"ready": true`

### 2. Run one full generation job

Inline requirement:

```powershell
python skills/specforge-full-project-compiler/scripts/run_requirement_project.py --repo-root . --project-name "<project-name>" --requirement "<one-line requirement>" --run-id <run-id> --force
```

Requirement file:

```powershell
python skills/specforge-full-project-compiler/scripts/run_requirement_project.py --repo-root . --project-name "<project-name>" --requirement-file "<requirement-file>" --run-id <run-id> --force
```

Examples:

```powershell
python skills/specforge-full-project-compiler/scripts/run_requirement_project.py --repo-root . --project-name "Insurance Operations Platform" --requirement "Build a complete modular-monolith Spring Boot insurance operations backend covering product center, customer center, policy center, claim center, premium payment center, renewal center, underwriting center, channel agent center, notification center, and statistics reporting center." --run-id insurance-demo-001 --force
```

```powershell
python skills/specforge-full-project-compiler/scripts/run_requirement_project.py --repo-root . --project-name "Library Management Platform" --requirement "Build a complete modular-monolith Spring Boot library management backend covering book catalog center, reader membership center, circulation borrowing center, return inspection center, reservation queue center, acquisition supplier center, shelf inventory center, notification center, and statistics reporting center." --run-id library-demo-001 --force
```

### 3. Read the final summary

```powershell
python skills/specforge-full-project-compiler/scripts/summarize_specforge_outcome.py --repo-root . --run-id <run-id>
```

## Success Means All PASS

- `compile_status`
- `boot_status`
- `business_contract_status`
- `delivery_validation_status`
- `sql_asset_status`
- `auth_surface_status`

## Where To Look

Final product:

- `specforge-runtime/outputs/<project-backend>/`

Run evidence:

- `specforge-runtime/runs/<run-id>/`

If something fails, inspect:

- `specforge-runtime/runs/<run-id>/logs/auto-build-report.yaml`
- `specforge-runtime/runs/<run-id>/generated-project/logs/project-health-report.yaml`
- `specforge-runtime/runs/<run-id>/generated-project/logs/compile-diagnostics.yaml`
- `specforge-runtime/runs/<run-id>/generated-project/logs/boot-diagnostics.yaml`

## Supported Auto-Detected Domains

- `laboratory-reservation`
- `laboratory-management`
- `insurance-management`
- `library-management`

## One-Line Prompt For Codex

```text
Use $specforge-full-project-compiler in this repository. Read README.md, WORKSPACE_LAYOUT.md, and specforge-runtime/docs/SUPER_QUICKSTART.md. Then generate a complete Spring Boot backend from my requirement, keep going until compile, boot, business contract validation, delivery validation, SQL asset validation, and auth surface validation all pass, and treat specforge-runtime/outputs/ as the only final deliverable.
```

## Two Rules

- Run only one generation job at a time in the same repository checkout.
- Treat `specforge-runtime/outputs/` as the product and `specforge-runtime/runs/` as logs.
