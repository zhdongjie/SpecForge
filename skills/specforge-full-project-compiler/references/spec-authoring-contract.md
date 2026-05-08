# Spec Authoring Contract

## Project Planning Rules

- Treat the system as a modular-monolith.
- Derive modules from business capabilities, not package names.
- Prefer 3-8 bounded modules for a graduation-project backend.
- Separate platform concerns from business-domain modules.

## Required Generated Inputs

Create or update:

- `specforge-runtime/specs/project-spec.md`
- `specforge-runtime/specs/project-assembly-plan.yaml`
- `specforge-runtime/specs/build-plan.yaml`

For each enabled module create or update:

- `module-spec.yaml`
- `module-schema.resolved.yaml`

If multiple modules are needed, prefer template-style subdirectories under:

- `specforge-runtime/specs/templates/<module-name>/`

## Default Module Set For Business Platforms

When the requirement is broad and under-specified, infer a practical default split:

- domain resource management
- business transaction management
- approval or workflow management
- notification or messaging
- access or policy management

## Authoring Discipline

- Prefer deterministic names over creative naming.
- Keep semantic role explicit:
  - `business-domain`
  - `system-domain`
  - `platform-domain`
- Keep module dependencies acyclic.
- Enable only modules that have enough semantic detail to synthesize safely.
- Default to enabled modules that are covered by the validated domain blueprints; only disable a module when its synthesis inputs are truly missing or verification has failed.

## Regeneration Contract

- Always update the assembly plan when adding modules.
- Always keep `build-plan.yaml` pointed at the canonical `project-assembly-plan.yaml`.
- Never report project completion after generating only one module if the requirement clearly implies a multi-module system.
