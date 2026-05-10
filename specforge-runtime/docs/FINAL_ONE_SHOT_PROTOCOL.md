# Final One-Shot Protocol

Use this protocol when the target is:

- a fresh Codex session
- a new machine
- a one-line or one-file requirement
- a complete backend outcome with no step-by-step chat dependency

## Minimal Goal

Provide only:

- the repository
- the skill
- the requirement

and let Codex run until:

- compile passes
- boot passes
- delivery validation passes
- business contract validation passes
- SQL asset validation passes
- auth surface validation passes

or produce a reproducible failure bundle.

## Fastest Human Workflow

1. Open the repository root.
2. Ensure JDK 17+ and Maven 3.9+ are available.
3. If you want a fresh Codex environment to auto-discover the skill, copy:
   - `skills/specforge-full-project-compiler/`
   into:
   - `C:\Users\<username>\.codex\skills\specforge-full-project-compiler\`
4. Run:

```powershell
python skills/specforge-full-project-compiler/scripts/check_specforge_workspace.py --repo-root .
```

5. Use one of these:

Inline requirement:

```powershell
python skills/specforge-full-project-compiler/scripts/run_requirement_project.py --repo-root . --project-name "<project-name>" --requirement "<one-line requirement>" --run-id <run-id> --force
```

Requirement document:

```powershell
python skills/specforge-full-project-compiler/scripts/run_requirement_project.py --repo-root . --project-name "<project-name>" --requirement-file "<requirement-file>" --run-id <run-id> --force
```

Currently validated automatic scaffold domains include:

- `laboratory-reservation`
- `laboratory-management`
- `insurance-management`
- `library-management`
- `course-management`
- `dormitory-management`

## Fastest Codex Handoff Workflow

Generate a copy-paste prompt with:

Inline requirement:

```powershell
python skills/specforge-full-project-compiler/scripts/emit_codex_handoff_prompt.py --project-name "<project-name>" --requirement "<one-line requirement>" --mode inline
```

Requirement document:

```powershell
python skills/specforge-full-project-compiler/scripts/emit_codex_handoff_prompt.py --project-name "<project-name>" --requirement-file "<requirement-file>" --mode file
```

Then paste the emitted prompt into the fresh Codex session.

## Success Rule

Accept success only if:

- `specforge-runtime/outputs/<project-backend>/` exists
- `compile_status: PASS`
- `boot_status: PASS`
- `specforge-runtime/outputs/<project-backend>/logs/delivery-validation.yaml` says `status: PASS`
- `specforge-runtime/outputs/<project-backend>/logs/api-smoke/business-contract-validation.yaml` says `validation.status: PASS`
- `specforge-runtime/outputs/<project-backend>/logs/sql-asset-validation.yaml` says `status: PASS`
- `specforge-runtime/outputs/<project-backend>/logs/auth-surface-validation.yaml` says `status: PASS`
- `specforge-runtime/outputs/<project-backend>/logs/demo-access.yaml` exists
- `specforge-runtime/outputs/<project-backend>/logs/api-smoke/postman-environment.json` exists
- `specforge-runtime/outputs/<project-backend>/src/main/resources/sql/demo-password-reset.sql` exists

## Failure Rule

If the run does not converge, return:

- `specforge-runtime/runs/<run-id>/logs/auto-build-report.yaml`
- `specforge-runtime/runs/<run-id>/generated-project/logs/project-health-report.yaml`
- `specforge-runtime/runs/<run-id>/generated-project/logs/compile-diagnostics.yaml`
- `specforge-runtime/runs/<run-id>/generated-project/logs/boot-diagnostics.yaml`

## Stable Interpretation

- `backend/` is template input
- `specforge-runtime/runs/` is execution evidence
- `specforge-runtime/outputs/` is the product
- `sandbox/` is scratch space
