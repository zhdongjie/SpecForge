# SpecForge

SpecForge is a deterministic Spring Boot backend compiler workflow.

Its goal is:

- input a short project requirement or a requirement document
- compile project specs and module specs
- generate a full backend
- verify compile and boot
- export the final backend into a stable output directory

## Directory Map

- `backend/`
  - baseline backend template
  - compiler assembly input
  - not the final generated deliverable

- `specforge-runtime/`
  - compiler runtime
  - canonical specs live in `specforge-runtime/specs/`
  - per-run execution traces live in `specforge-runtime/runs/`
  - final generated projects export into `specforge-runtime/outputs/`

- `skills/`
  - Codex skills, including the full-project compiler skill
  - repository-local source of truth for portable skill logic

- `sandbox/`
  - local-only validation area
  - ignored by git

See [WORKSPACE_LAYOUT.md](WORKSPACE_LAYOUT.md) for the full workspace contract.

## Fastest Path

If you want:

- one project name
- or one short requirement
- and one complete generated backend

use this flow.

Shortest doc:

- [SUPER_QUICKSTART.md](E:/Project/Generate/SpecForge/specforge-runtime/docs/SUPER_QUICKSTART.md)

### 1. Prepare toolchain

Install:

- JDK 17+
- Maven 3.9+

Recommended environment variables:

- `SPECFORGE_JAVA_HOME`
- `SPECFORGE_MAVEN_CMD`

If you want a fresh Codex environment to auto-discover the project compiler skill, also copy:

- `skills/specforge-full-project-compiler/`

to:

- `C:\Users\<username>\.codex\skills\specforge-full-project-compiler\`

If you only plan to run the repository-local commands in this README, the repository copy under `skills/` is enough.

See [ENVIRONMENT_MIGRATION_RUNBOOK.md](E:/Project/Generate/SpecForge/specforge-runtime/docs/ENVIRONMENT_MIGRATION_RUNBOOK.md) for the portability contract.

### 2. Check workspace

```powershell
python skills/specforge-full-project-compiler/scripts/check_specforge_workspace.py --repo-root .
```

Expected result:

- `"ready": true`

### 3. Scaffold from a short requirement

Example:

```powershell
python skills/specforge-full-project-compiler/scripts/scaffold_requirement_project.py --repo-root . --project-name "Laboratory Reservation Platform" --requirement "Build a complete laboratory reservation management backend with reservation approval, notification, and laboratory access control under a modular-monolith Spring Boot architecture." --force
```

This writes canonical specs into:

- `specforge-runtime/specs/project-spec.md`
- `specforge-runtime/specs/project-assembly-plan.yaml`
- `specforge-runtime/specs/build-plan.yaml`
- `specforge-runtime/specs/templates/...`

### 4. Run the canonical auto-build

```powershell
python skills/specforge-full-project-compiler/scripts/run_specforge_autobuild.py --repo-root . --run-id lab-platform-001
```

Or use the one-command wrapper:

```powershell
python skills/specforge-full-project-compiler/scripts/run_requirement_project.py --repo-root . --project-name "Laboratory Reservation Platform" --requirement "Build a complete laboratory reservation management backend with reservation approval, notification, and laboratory access control under a modular-monolith Spring Boot architecture." --run-id lab-platform-001 --force
```

The wrapper can auto-select a supported scaffold domain from the project name and requirement text.

Use `--domain <domain-key>` only when you want to override automatic selection explicitly.

Currently validated automatic scaffold domains include:

- `laboratory-reservation`
- `laboratory-management`
- `insurance-management`
- `library-management`
- `course-management`
- `dormitory-management`

### 5. Check results

Success report:

- `specforge-runtime/runs/lab-platform-001/logs/auto-build-report.yaml`

Health report:

- `specforge-runtime/runs/lab-platform-001/generated-project/logs/project-health-report.yaml`

Final exported backend:

- `specforge-runtime/outputs/<project-backend>/`

## Final Output Rule

Treat only this as the final generated project:

- `specforge-runtime/outputs/<project-backend>/`

Meaning of each frequently-seen directory:

- `backend/`
  - reusable template input
- `specforge-runtime/runs/<run-id>/`
  - one build attempt
  - contains logs, diagnostics, intermediate IR, and a transient assembled project for validation
- `specforge-runtime/outputs/<project-backend>/`
  - latest handoff-ready generated backend
- `sandbox/`
  - local-only experimentation or migration rehearsal area

Do not treat these as final deliverables:

- `sandbox/...`
- `specforge-runtime/runs/<run-id>/generated-project/`

Those are validation and intermediate directories.

If you feel "the output directories are too many", the practical rule is simple:

- look at `specforge-runtime/outputs/` for the product
- look at `specforge-runtime/runs/` only when you need logs or failure diagnosis

## Canonical End-to-End Commands

Workspace readiness:

```powershell
python skills/specforge-full-project-compiler/scripts/check_specforge_workspace.py --repo-root .
```

Scaffold project specs:

```powershell
python skills/specforge-full-project-compiler/scripts/scaffold_requirement_project.py --repo-root . --project-name "<project-name>" --requirement "<requirement>" --force
```

Compile full backend:

```powershell
python skills/specforge-full-project-compiler/scripts/run_specforge_autobuild.py --repo-root . --run-id <run-id>
```

One-command full generation:

```powershell
python skills/specforge-full-project-compiler/scripts/run_requirement_project.py --repo-root . --project-name "<project-name>" --requirement "<one-line requirement>" --run-id <run-id> --force
```

Requirement-file generation:

```powershell
python skills/specforge-full-project-compiler/scripts/run_requirement_project.py --repo-root . --project-name "<project-name>" --requirement-file "<requirement-file>" --run-id <run-id> --force
```

Run the portable validation suite:

```powershell
python skills/specforge-full-project-compiler/scripts/run_tool_validation_suite.py --repo-root . --force
```

Clean runtime artifacts:

```powershell
python skills/specforge-full-project-compiler/scripts/clean_runtime_artifacts.py --repo-root .
```

Preview cleanup only:

```powershell
python skills/specforge-full-project-compiler/scripts/clean_runtime_artifacts.py --repo-root . --dry-run
```

Export backend API smoke assets:

```powershell
python skills/specforge-full-project-compiler/scripts/export_backend_api_smoke.py --backend-root specforge-runtime/outputs/<project-backend>
```

Export demo-access and frontend handoff assets:

```powershell
python skills/specforge-full-project-compiler/scripts/export_backend_delivery_assets.py --backend-root specforge-runtime/outputs/<project-backend>
```

## Frontend Handoff Assets

Every successful generated backend should also expose:

- `logs/demo-access.yaml`
- `logs/api-smoke/postman-collection.json`
- `logs/api-smoke/postman-environment.json`
- `logs/api-smoke/curl-login-example.sh`
- `logs/api-smoke/invoke-login.ps1`
- `src/main/resources/sql/demo-password-reset.sql`

Use these as the stable handoff surface when you connect a separate frontend repository.

See [FRONTEND_HANDOFF_BACKEND_CONTRACT.md](E:/Project/Generate/SpecForge/specforge-runtime/docs/FRONTEND_HANDOFF_BACKEND_CONTRACT.md) for the exact frontend integration contract.

If another Codex session or frontend repository needs a zero-context backend docking prompt, use:

```powershell
python skills/specforge-full-project-compiler/scripts/emit_frontend_handoff_prompt.py --backend-output specforge-runtime/outputs/<project-backend> --project-name "<project-name>"
```

Prompt reference:

- [FRONTEND_ZERO_CONTEXT_PROMPTS.md](E:/Project/Generate/SpecForge/specforge-runtime/docs/FRONTEND_ZERO_CONTEXT_PROMPTS.md)

Validate business module route and permission contracts:

```powershell
python skills/specforge-full-project-compiler/scripts/export_backend_api_smoke.py --backend-root specforge-runtime/outputs/<project-backend> --validate-business-contract
```

Validate final backend delivery contract:

```powershell
python skills/specforge-full-project-compiler/scripts/validate_backend_delivery.py --repo-root . --run-id <run-id>
```

Direct runtime equivalent:

```powershell
cd specforge-runtime
python main.py --auto-build --build-plan build-plan.yaml --run-id <run-id>
```

Emit a portable Codex handoff prompt:

```powershell
python skills/specforge-full-project-compiler/scripts/emit_codex_handoff_prompt.py --project-name "<project-name>" --requirement "<one-line requirement>" --mode inline
```

Emit a requirement-file handoff prompt:

```powershell
python skills/specforge-full-project-compiler/scripts/emit_codex_handoff_prompt.py --project-name "<project-name>" --requirement-file "<requirement-file>" --mode file
```

## Recommended Running Scheme

### A. Generate a backend in the current machine

1. Run the readiness check.
2. Use the one-command wrapper with either `--requirement` or `--requirement-file`.
3. Check:
   - `specforge-runtime/runs/<run-id>/logs/auto-build-report.yaml`
   - `specforge-runtime/runs/<run-id>/generated-project/logs/project-health-report.yaml`
   - `specforge-runtime/outputs/<project-backend>/logs/api-smoke/business-contract-validation.yaml`
   - `specforge-runtime/outputs/<project-backend>/logs/delivery-validation.yaml`
4. Accept success only if:
   - `compile_status: PASS`
   - `boot_status: PASS`
   - business contract validation status is `PASS`
   - delivery validation status is `PASS`
5. Take the final backend only from:
   - `specforge-runtime/outputs/<project-backend>/`

### B. Handoff to a fresh Codex session

1. Run `emit_codex_handoff_prompt.py`.
2. Paste the emitted prompt into the new Codex session.
3. Let the new session run until compile and boot pass, or it returns a reproducible failure bundle.

### C. Validate the tool itself

1. Run:
   - `python skills/specforge-full-project-compiler/scripts/run_tool_validation_suite.py --repo-root . --force`
2. Current built-in validated scenarios:
   - `lab-inline-auto`
   - `lab-platform-file-auto`
   - `insurance-inline-auto`
   - `insurance-file-auto`
   - `library-inline-auto`
3. Use this when you want to prove the generator still works after refactors, migration, or environment changes.

## Success And Failure Contract

Successful generation means:

- final backend exists under `specforge-runtime/outputs/`
- compile passes
- boot passes

If a run fails, inspect first:

- `specforge-runtime/runs/<run-id>/logs/auto-build-report.yaml`
- `specforge-runtime/runs/<run-id>/generated-project/logs/project-health-report.yaml`
- `specforge-runtime/runs/<run-id>/generated-project/logs/compile-diagnostics.yaml`
- `specforge-runtime/runs/<run-id>/generated-project/logs/boot-diagnostics.yaml`

## One-Line Requirement Mode

For a new domain, the most portable workflow is:

1. Put the repository on the new machine.
2. Ensure JDK and Maven resolve.
3. Give Codex one project sentence or one requirements document.
4. Let the skill scaffold specs into `specforge-runtime/specs/`.
5. Run the canonical auto-build.
6. Accept success only if `compile` and `boot` both pass.
7. Take the final backend only from `specforge-runtime/outputs/`.

See [ONE_LINE_REQUIREMENT_PLAYBOOK.md](E:/Project/Generate/SpecForge/specforge-runtime/docs/ONE_LINE_REQUIREMENT_PLAYBOOK.md).
See [CODEX_STARTER_PROMPTS.md](E:/Project/Generate/SpecForge/specforge-runtime/docs/CODEX_STARTER_PROMPTS.md) for copy-paste prompts for a fresh Codex session.
See [REQUIREMENT_TEMPLATE.md](E:/Project/Generate/SpecForge/specforge-runtime/docs/REQUIREMENT_TEMPLATE.md) for a structured requirement document template.
See [REQUIREMENT_AUTHORING_AND_HANDOFF_PROMPT.md](E:/Project/Generate/SpecForge/specforge-runtime/docs/REQUIREMENT_AUTHORING_AND_HANDOFF_PROMPT.md) for the two-phase prompt, including a minimal daily-use copy-paste version that first writes a detailed requirement document, then lets you manually edit it, and finally lets the same Codex continue from that file.
See [DAILY_REQUIREMENT_PROMPT_TEMPLATE.md](E:/Project/Generate/SpecForge/specforge-runtime/docs/DAILY_REQUIREMENT_PROMPT_TEMPLATE.md) for the fastest replace-only prompt template.
See [FINAL_ONE_SHOT_PROTOCOL.md](E:/Project/Generate/SpecForge/specforge-runtime/docs/FINAL_ONE_SHOT_PROTOCOL.md) for the shortest new-machine or fresh-Codex operating path.
See [CODEX_CHROME_TEST_LOOP.md](E:/Project/Generate/SpecForge/specforge-runtime/docs/CODEX_CHROME_TEST_LOOP.md) for the browser verification loop with Codex for Chrome.

## Handoff Rule

When moving to another machine or another Codex session:

1. Read [README.md](README.md)
2. Read [WORKSPACE_LAYOUT.md](WORKSPACE_LAYOUT.md)
3. Read [PROJECT_COMPILER_PROTOCOL.md](E:/Project/Generate/SpecForge/specforge-runtime/docs/PROJECT_COMPILER_PROTOCOL.md)
4. Read [ENVIRONMENT_MIGRATION_RUNBOOK.md](E:/Project/Generate/SpecForge/specforge-runtime/docs/ENVIRONMENT_MIGRATION_RUNBOOK.md)
5. Read [CODEX_STARTER_PROMPTS.md](E:/Project/Generate/SpecForge/specforge-runtime/docs/CODEX_STARTER_PROMPTS.md)
6. Use `specforge-runtime/specs/build-plan.yaml` as the canonical execution entry

## Current Proven Flow

The validated local flow now supports:

- scaffold from a one-line requirement
- assemble multiple business modules
- compile pass
- boot pass
- final export under `specforge-runtime/outputs/`
