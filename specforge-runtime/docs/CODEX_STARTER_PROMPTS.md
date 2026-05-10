# Codex Starter Prompts

This file provides copy-paste prompts for a fresh Codex session.

Use these prompts when you want the next agent to succeed without relying on prior chat history.

## Prompt A: One-Line Requirement

```text
Use $specforge-full-project-compiler in this repository.
Read README.md, WORKSPACE_LAYOUT.md, specforge-runtime/docs/PROJECT_COMPILER_PROTOCOL.md, and specforge-runtime/docs/ENVIRONMENT_MIGRATION_RUNBOOK.md.
Then compile a complete Spring Boot backend from this requirement:

<one-line requirement>

Execution contract:
1. Check workspace readiness.
2. Scaffold canonical specs from the requirement.
3. Run the canonical auto-build pipeline.
4. Continue until compile, boot, business contract validation, delivery validation, SQL asset validation, and auth surface validation all pass, or return a reproducible failure bundle.
5. Treat specforge-runtime/outputs/ as the only final deliverable.
6. Do not ask me for step-by-step confirmation unless there is a destructive risk or a major architecture ambiguity.
```

## Prompt B: Requirement Document

```text
Use $specforge-full-project-compiler in this repository.
Read README.md, WORKSPACE_LAYOUT.md, specforge-runtime/docs/PROJECT_COMPILER_PROTOCOL.md, and specforge-runtime/docs/ENVIRONMENT_MIGRATION_RUNBOOK.md.
Then compile a complete Spring Boot backend from the requirement document at:

<absolute-or-repo-relative-requirement-file>

Execution contract:
1. Check workspace readiness.
2. Normalize the requirement document into project scope.
3. Scaffold or update canonical specs.
4. Run the canonical auto-build pipeline.
5. Continue until compile, boot, business contract validation, delivery validation, SQL asset validation, and auth surface validation all pass, or return a reproducible failure bundle.
6. Treat specforge-runtime/outputs/ as the only final deliverable.
```

If you need a structured document instead of free writing, start from:

- `specforge-runtime/docs/REQUIREMENT_TEMPLATE.md`

## Prompt C: Domain + Completeness Bias

Use this when you want to strongly signal "not a thin CRUD demo".

```text
Use $specforge-full-project-compiler in this repository.
Read the repository orientation docs first.
Generate a complete graduation-project-grade Spring Boot backend, not a thin CRUD skeleton.
The domain is:

<domain or project title>

Requirements:
- prefer business-center level module coverage when the domain supports it
- include user/role/menu linkage as a project-level concern
- include database initialization SQL organization as a project-level concern
- keep business modules under org.eu.originalkeen.business.*
- keep business routes under /v1/business/*
- keep business authorities under business:*
- continue until compile, boot, business contract validation, delivery validation, SQL asset validation, and auth surface validation all pass, or return a reproducible failure bundle
- treat specforge-runtime/outputs/ as the only final deliverable
```

## Prompt D: Resume Existing Specs

Use this when canonical specs already exist and you want the new Codex session to continue from them.

```text
Use $specforge-full-project-compiler in this repository.
Read README.md, WORKSPACE_LAYOUT.md, specforge-runtime/docs/PROJECT_COMPILER_PROTOCOL.md, specforge-runtime/docs/ENVIRONMENT_MIGRATION_RUNBOOK.md, and specforge-runtime/specs/build-plan.yaml.
Continue from the existing canonical specs instead of starting over.
Run the canonical auto-build pipeline and keep iterating until compile, boot, business contract validation, delivery validation, SQL asset validation, and auth surface validation all pass, or return a reproducible failure bundle.
Treat specforge-runtime/outputs/ as the only final deliverable.
```

## Expected Success Return

On success, the agent should report at least:

- final backend path under `specforge-runtime/outputs/`
- run id
- compile status
- boot status
- business contract validation status
- delivery validation status
- SQL asset validation status
- auth surface validation status
- module coverage summary

## Expected Failure Return

On failure, the agent should report at least:

- run id
- failure bundle path under `specforge-runtime/runs/<run-id>/logs/`
- blocking stage
- next reproducible rerun command

## Operator Shortcut

If the environment already has Python, JDK, and Maven ready, the fastest single command is:

```powershell
python skills/specforge-full-project-compiler/scripts/run_requirement_project.py --repo-root . --project-name "<project-name>" --requirement "<one-line requirement>" --run-id <run-id> --force
```

## Frontend Continuation Shortcut

If a frontend repository or another Codex session needs to continue from an already generated backend, first emit a handoff prompt with:

```powershell
python skills/specforge-full-project-compiler/scripts/emit_frontend_handoff_prompt.py --backend-output specforge-runtime/outputs/<project-backend> --project-name "<project-name>"
```
