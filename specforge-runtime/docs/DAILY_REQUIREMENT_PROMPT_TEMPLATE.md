# Daily Requirement Prompt Template

Use this file as the fastest day-to-day prompt source.

Only replace:

- `<project-name>`
- `<requirement-doc-path>`
- `<one-line idea>`

## Phase 1

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

## Phase 2

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

## Recommended Default Path

```text
specforge-runtime/specs/input/<project-name>-requirement.md
```
