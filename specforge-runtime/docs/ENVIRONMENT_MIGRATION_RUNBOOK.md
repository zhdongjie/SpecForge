# SpecForge Environment Migration Runbook

This runbook defines the portable execution contract for moving SpecForge to a new machine or handing it to another Codex session.

Repository-level directory roles are summarized in:

- `WORKSPACE_LAYOUT.md`

## Goals

- Reproduce backend generation on a clean machine
- Avoid local hardcoded JDK or Maven assumptions
- Preserve deterministic build, compile, and boot verification
- Let another Codex session succeed from a short requirement without inheriting chat history

## Required Layout

Clone or copy the repository so that this directory exists:

- `specforge-runtime/`

Recommended repository companion path:

- `skills/specforge-full-project-compiler/`

Canonical runtime entrypoint:

- `specforge-runtime/main.py`

Canonical final backend export location:

- `specforge-runtime/outputs/<plan-id-or-custom-output>/`

Local-only verification area:

- `sandbox/`

Do not treat `sandbox/` as canonical source or final deliverable output.

## Codex Skill Installation Modes

There are two supported migration modes.

### Mode A: Repository-local execution only

Use this when you will run commands directly inside the repository.

In this mode, keeping the skill under:

- `skills/specforge-full-project-compiler/`

is enough, because all documented commands already reference the repository-local script paths.

### Mode B: Fresh Codex auto-discovery

Use this when you want a fresh Codex environment to discover the skill automatically without being told the repository path first.

Copy this directory:

- `skills/specforge-full-project-compiler/`

into the new machine's Codex home, for example:

- `C:\Users\<username>\.codex\skills\specforge-full-project-compiler\`

Recommended practice:

- keep one copy in the repository for version control
- keep one copy in `.codex/skills/` for automatic Codex discovery

If only one copy is maintained, the repository copy remains the canonical source of truth.

## Toolchain Discovery Contract

SpecForge now resolves Java and Maven in this order.

### Java

1. `SPECFORGE_JAVA_HOME`
2. `JAVA_HOME`
3. `java` available on `PATH`
4. common local install directories scanned on Windows

### Maven

1. `SPECFORGE_MAVEN_CMD`
2. `SPECFORGE_MAVEN_HOME`
3. `MAVEN_HOME`
4. `M2_HOME`
5. `mvn.cmd` or `mvn` on `PATH`
6. common local install directories scanned on Windows

## Recommended New-Machine Bootstrap

1. Install JDK 17.
2. Install Maven 3.9+.
3. Copy the repository to the new machine.
4. If you want automatic Codex skill discovery, copy `skills/specforge-full-project-compiler/` into `.codex/skills/`.
5. Set environment variables:
   - `SPECFORGE_JAVA_HOME`
   - `SPECFORGE_MAVEN_CMD`
6. Verify commands:
   - `java -version`
   - `mvn -version`
7. Open the repo root.
8. Read:
   - `README.md`
   - `WORKSPACE_LAYOUT.md`
   - `specforge-runtime/docs/PROJECT_COMPILER_PROTOCOL.md`
   - `specforge-runtime/docs/ONE_LINE_REQUIREMENT_PLAYBOOK.md`
   - `specforge-runtime/docs/CODEX_STARTER_PROMPTS.md`
   - `specforge-runtime/docs/REQUIREMENT_TEMPLATE.md`

## Canonical Commands

### Zero-context full-project path

This is the preferred path when a new machine or a new Codex session starts from almost no prior context.

1. Check workspace readiness.
2. Scaffold project specs from one sentence or one requirements file.
3. Run the canonical auto-build command.
4. Accept only `compile_status: PASS`, `boot_status: PASS`, `business-contract-validation.yaml validation.status: PASS`, `delivery-validation.yaml status: PASS`, `sql-asset-validation.yaml status: PASS`, and `auth-surface-validation.yaml status: PASS`.
5. Take the final backend only from `specforge-runtime/outputs/`.

Workspace safety rule:

- do not run two generation jobs concurrently in the same repository checkout
- the wrappers now create `specforge-runtime/.workspace.lock` to prevent shared `specs/` and `outputs/` mutation races
- if a process is interrupted unexpectedly, clear the stale lock only after confirming no SpecForge job is still running

Preferred wrapper commands from the repo root:

```powershell
python skills/specforge-full-project-compiler/scripts/check_specforge_workspace.py --repo-root .
python skills/specforge-full-project-compiler/scripts/scaffold_requirement_project.py --repo-root . --project-name "<project-name>" --requirement "<one-line requirement>" --force
python skills/specforge-full-project-compiler/scripts/run_specforge_autobuild.py --repo-root . --run-id <run-id>
```

One-command shortcut:

```powershell
python skills/specforge-full-project-compiler/scripts/run_requirement_project.py --repo-root . --project-name "<project-name>" --requirement "<one-line requirement>" --run-id <run-id> --force
```

Outcome summary command:

```powershell
python skills/specforge-full-project-compiler/scripts/summarize_specforge_outcome.py --repo-root . --run-id <run-id>
```

### Runtime component commands

IR lowering:

```powershell
python main.py --lower-ir --run-id lowering-smoke
```

Module synthesis:

```powershell
python main.py --synthesize-module --verify-compile --run-id synth-smoke
```

Backend compile and boot:

```powershell
python main.py --compile-backend --verify-boot --run-id backend-smoke
```

Deterministic hardening pipeline:

```powershell
python main.py --harden-backend --auto-repair --verify-boot --run-id hardening-smoke
```

Canonical end-to-end export:

```powershell
python main.py --auto-build --build-plan build-plan.yaml --run-id laboratory-reservation-final
```

## Output Contract

Successful end-to-end runs must produce:

- `runs/<run-id>/logs/auto-build-report.yaml`
- `outputs/<target>/`
- `outputs/<target>/logs/delivery-validation.yaml`
- `outputs/<target>/logs/api-smoke/business-contract-validation.yaml`
- `outputs/<target>/logs/sql-asset-validation.yaml`
- `outputs/<target>/logs/auth-surface-validation.yaml`
- `outputs/<target>/logs/demo-access.yaml`
- `outputs/<target>/logs/api-smoke/postman-environment.json`
- `outputs/<target>/src/main/resources/sql/demo-password-reset.sql`

The final backend for handoff or deployment review is always the exported backend under:

- `specforge-runtime/outputs/...`

Do not treat temporary generated directories inside `runs/` as final deliverables.

## Reproducibility Rules

- Use canonical specs from `specforge-runtime/specs/`.
- Keep runtime version and specs in the same commit when migrating.
- Always prefer `build-plan.yaml` driven runs over ad hoc command combinations.
- Treat any compile or boot failure as a reproducible artifact only if the matching logs in `runs/<run-id>/logs/` are preserved.
- Treat one repository checkout as one active mutable workspace for generation purposes.
- Prefer separate repository copies if you need to run multiple domains in parallel on the same machine.

## Another Codex Handoff Contract

When another Codex session resumes this repository, it should:

1. Read `README.md`.
2. Read `WORKSPACE_LAYOUT.md`.
3. Read `specforge-runtime/docs/PROJECT_COMPILER_PROTOCOL.md`.
4. Read `specforge-runtime/docs/ENVIRONMENT_MIGRATION_RUNBOOK.md`.
5. Read `specforge-runtime/docs/ONE_LINE_REQUIREMENT_PLAYBOOK.md`.
6. Read `specforge-runtime/docs/CODEX_STARTER_PROMPTS.md`.
7. If the task begins from a new requirement, run the scaffold command before auto-build.
8. Use `specforge-runtime/specs/build-plan.yaml` as the canonical execution entry spec.
9. Export final deliverables only into `specforge-runtime/outputs/`.
10. If a frontend repository will consume the backend, also read `specforge-runtime/docs/FRONTEND_HANDOFF_BACKEND_CONTRACT.md`.
11. If another Codex session will continue from the generated backend, also read `specforge-runtime/docs/FRONTEND_ZERO_CONTEXT_PROMPTS.md`.

The resumed agent must not rely on prior conversational context as part of the execution contract.

## Failure Report Contract

If generation cannot succeed on the new machine, preserve:

- `compile-diagnostics.yaml`
- `compile-repair-report.yaml`
- `boot-diagnostics.yaml`
- `boot-repair-report.yaml`
- `project-health-report.yaml`
- `auto-build-report.yaml`

Use this helper to print the canonical success or failure paths:

```powershell
python skills/specforge-full-project-compiler/scripts/summarize_specforge_outcome.py --repo-root . --run-id <run-id>
```

These files together are the minimum reproducible failure bundle.
