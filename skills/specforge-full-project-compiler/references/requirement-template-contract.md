# Requirement Template Contract

Use this reference when the user wants:

- a reusable requirement document format
- a handoff-friendly input contract
- less dependence on free-form prompting

## Goal

Normalize project input so another Codex session can regenerate a backend with less ambiguity.

## Required Sections

- project name
- project goal
- domain
- core business centers
- primary roles
- core flows
- required platform rules
- completeness expectations
- optional domain notes

## Completeness Rule

If the requirement says the project is complete or platform-level, the template should bias the compiler toward:

- business-center level modules
- user/role/menu linkage
- initialization SQL organization
- compile verification
- boot verification

## Output Rule

The template is only an input aid.

Final success still requires:

- canonical specs under `specforge-runtime/specs/`
- final backend under `specforge-runtime/outputs/`
