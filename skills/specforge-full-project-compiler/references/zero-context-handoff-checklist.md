# Zero-Context Handoff Checklist

Use this reference when the user wants the workflow to be repeatable on:

- another machine
- another repository clone
- another Codex session

## Handoff Objective

A fresh agent should be able to:

1. orient itself from repository files
2. scaffold specs from a requirement
3. run canonical auto-build
4. return either:
   - a final backend under `specforge-runtime/outputs/`
   - or a reproducible failure bundle under `specforge-runtime/runs/<run-id>/logs/`

## Required Repository Orientation Files

- `README.md`
- `WORKSPACE_LAYOUT.md`
- `specforge-runtime/docs/PROJECT_COMPILER_PROTOCOL.md`
- `specforge-runtime/docs/ENVIRONMENT_MIGRATION_RUNBOOK.md`
- `specforge-runtime/docs/ONE_LINE_REQUIREMENT_PLAYBOOK.md`
- `specforge-runtime/docs/CODEX_STARTER_PROMPTS.md`

## Directory Meanings

- `backend/`
  - template input
- `specforge-runtime/specs/`
  - canonical compiler input
- `specforge-runtime/runs/<run-id>/`
  - one execution attempt with evidence
- `specforge-runtime/outputs/<target>/`
  - final deliverable
- `sandbox/`
  - scratch area

## Success Rule

Never call the task complete unless:

- compile passes
- boot passes
- final backend exists under `specforge-runtime/outputs/`

## Reporting Rule

On success, report the final backend path first.

On failure, report the failure bundle path first.
