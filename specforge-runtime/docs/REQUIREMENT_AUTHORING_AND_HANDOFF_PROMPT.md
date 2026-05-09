# Requirement Authoring And Resume Prompt

Use this file when you want one Codex session to work in two phases:

1. first write a detailed requirement document into a specified directory
2. then pause so you can manually edit that document
3. then let the same Codex continue from the edited document

This is useful when you want:

- one short idea as input
- one detailed requirement document as intermediate artifact
- one manual review or manual adjustment step
- one complete backend generation flow afterward

## Minimal Copy-Paste Version

If you want the shortest daily-use version, use these two prompts directly.

### Replace These Variables Only

In both prompts below, you usually only need to replace:

- `<project-name>`
- `<requirement-doc-path>`
- `<one-line idea>`

### Minimal Phase 1

```text
In this repository, write a detailed graduation-project-grade backend requirement document for this project.

Project name:
<project-name>

Project idea:
<one-line idea>

Rules:
1. Read README.md, WORKSPACE_LAYOUT.md, and specforge-runtime/docs/REQUIREMENT_TEMPLATE.md first.
2. Write the requirement document in Markdown.
3. Save it exactly to:
   <requirement-doc-path>
4. Make it detailed enough for SpecForge to generate a complete backend, not a thin CRUD skeleton.
5. Stop after writing the document.
6. Do not run generation.
7. Do not commit anything.
```

### Minimal Phase 2

```text
Use $specforge-full-project-compiler in this repository.
Read README.md, WORKSPACE_LAYOUT.md, specforge-runtime/docs/PROJECT_COMPILER_PROTOCOL.md, and specforge-runtime/docs/ENVIRONMENT_MIGRATION_RUNBOOK.md.
Continue in this same repository from this requirement document:

<requirement-doc-path>

Project name:
<project-name>

Rules:
1. Check workspace readiness.
2. Generate and update canonical specs from the requirement document.
3. Run the canonical auto-build pipeline.
4. Continue until compile and boot both pass, or return a reproducible failure bundle.
5. Treat specforge-runtime/outputs/ as the only final deliverable.
```

## Ready-To-Fill Daily Template

Use this section as your default working copy.

### Daily Template Values

```text
<project-name> = Laboratory Management Platform
<requirement-doc-path> = specforge-runtime/specs/input/laboratory-management-platform-requirement.md
<one-line idea> = Build a complete modular-monolith Spring Boot laboratory management backend covering laboratory resources, equipment management, consumable inventory, experiment projects, reservation approvals, access control, notifications, schedule calendar, and statistics reporting.
```

### Daily Template Phase 1

```text
In this repository, write a detailed graduation-project-grade backend requirement document for this project.

Project name:
Laboratory Management Platform

Project idea:
Build a complete modular-monolith Spring Boot laboratory management backend covering laboratory resources, equipment management, consumable inventory, experiment projects, reservation approvals, access control, notifications, schedule calendar, and statistics reporting.

Rules:
1. Read README.md, WORKSPACE_LAYOUT.md, and specforge-runtime/docs/REQUIREMENT_TEMPLATE.md first.
2. Write the requirement document in Markdown.
3. Save it exactly to:
   specforge-runtime/specs/input/laboratory-management-platform-requirement.md
4. Make it detailed enough for SpecForge to generate a complete backend, not a thin CRUD skeleton.
5. Stop after writing the document.
6. Do not run generation.
7. Do not commit anything.
```

### Daily Template Phase 2

```text
Use $specforge-full-project-compiler in this repository.
Read README.md, WORKSPACE_LAYOUT.md, specforge-runtime/docs/PROJECT_COMPILER_PROTOCOL.md, and specforge-runtime/docs/ENVIRONMENT_MIGRATION_RUNBOOK.md.
Continue in this same repository from this requirement document:

specforge-runtime/specs/input/laboratory-management-platform-requirement.md

Project name:
Laboratory Management Platform

Rules:
1. Check workspace readiness.
2. Generate and update canonical specs from the requirement document.
3. Run the canonical auto-build pipeline.
4. Continue until compile and boot both pass, or return a reproducible failure bundle.
5. Treat specforge-runtime/outputs/ as the only final deliverable.
```

## Phase 1 Prompt: Write The Detailed Requirement Document Only

Copy and paste this prompt into Codex for the first phase.

```text
In this repository, help me write a detailed graduation-project-grade backend requirement document for the project below.

Project name:
<project-name>

Project idea or short requirement:
<one-line idea or short requirement>

Execution rules:
1. Read README.md, WORKSPACE_LAYOUT.md, and specforge-runtime/docs/REQUIREMENT_TEMPLATE.md first.
2. Write a detailed requirement document in Markdown.
3. Save it to this exact path:
   <requirement-doc-path>
4. The document should be detailed enough for the SpecForge pipeline to generate a complete backend, not a thin CRUD skeleton.
5. Prefer business-center level coverage, roles, core flows, project-level rules, completeness expectations, and domain notes.
6. Do not run the generation pipeline yet.
7. Do not commit anything.
8. Stop after the requirement document is written.
```

After that, manually review and edit the requirement document if needed.

## Phase 2 Prompt: Resume From The Requirement Document

After the requirement document exists and you have finished manual edits, copy and paste this prompt into the same Codex session.

```text
Use $specforge-full-project-compiler in this repository.
Read README.md, WORKSPACE_LAYOUT.md, specforge-runtime/docs/PROJECT_COMPILER_PROTOCOL.md, and specforge-runtime/docs/ENVIRONMENT_MIGRATION_RUNBOOK.md.
Continue in this same repository and compile a complete Spring Boot backend for the project below from the requirement document at:

<requirement-doc-path>

Project name:
<project-name>

Execution contract:
1. Check workspace readiness.
2. Normalize the requirement document into project scope.
3. Scaffold or update canonical specs.
4. Run the canonical auto-build pipeline.
5. Continue until compile and boot both pass, or return a reproducible failure bundle.
6. Treat specforge-runtime/outputs/ as the only final deliverable.
7. Do not ask me for step-by-step confirmation unless there is a destructive risk or a major architecture ambiguity.
```

## Recommended Requirement Document Location

Prefer a stable repo-local path such as:

- `specforge-runtime/specs/input/<project-name>-requirement.md`
- `docs/requirements/<project-name>.md`
- `sandbox/<project-name>-requirement.md`

If the document is meant to become part of the canonical repository workflow, prefer:

- `specforge-runtime/specs/input/<project-name>-requirement.md`

If the document is only for temporary local experimentation, prefer:

- `sandbox/<project-name>-requirement.md`

## Recommended Operator Flow

1. Start from one short idea.
2. Run Phase 1 prompt.
3. Manually review and edit the generated requirement document.
4. Run Phase 2 prompt in the same Codex session.
5. Accept success only if compile and boot both pass.
6. Take the final backend only from `specforge-runtime/outputs/`.

## Recommended Default Path

For routine use, prefer:

- `specforge-runtime/specs/input/<project-name>-requirement.md`

This path is stable enough for manual editing and easy for the next phase to consume.
