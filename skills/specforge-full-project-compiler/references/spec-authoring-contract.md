# Spec Authoring Contract

## Project Planning Rules

- Treat the system as a modular-monolith.
- Derive modules from business capabilities, not package names.
- Prefer 3-8 bounded modules for a graduation-project backend.
- Separate platform concerns from business-domain modules.
- If the user asks for a "complete", "full", or "platform-level" system, raise the default target to 8-12 business-domain modules when the domain supports it.
- Treat user/role/menu linkage and database initialization SQL organization as required project-level deliverables for complete-platform requests.

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

When the requirement implies a fuller platform, expand beyond the minimal split and prefer business centers such as:

- product center
- customer center
- policy or order center
- approval center
- claim or after-sales center
- payment center
- renewal center
- channel or agent center
- notification center
- statistics or reporting center

## Authoring Discipline

- Prefer deterministic names over creative naming.
- Keep semantic role explicit:
  - `business-domain`
  - `system-domain`
  - `platform-domain`
- Keep module dependencies acyclic.
- Enable only modules that have enough semantic detail to synthesize safely.
- Default to enabled modules that are covered by the validated domain blueprints; only disable a module when its synthesis inputs are truly missing or verification has failed.
- Do not call a platform "complete" if it only contains a thin CRUD subset of the expected business centers.
- Record project-level supporting surfaces explicitly in `project-spec.md` when relevant:
  - user/role/menu linkage
  - initialization SQL organization
  - reporting surfaces
  - notification surfaces

## Regeneration Contract

- Always update the assembly plan when adding modules.
- Always keep `build-plan.yaml` pointed at the canonical `project-assembly-plan.yaml`.
- Never report project completion after generating only one module if the requirement clearly implies a multi-module system.
- Never report "complete platform" status unless the generated module set and project spec reflect the expected business-center coverage for that domain.
