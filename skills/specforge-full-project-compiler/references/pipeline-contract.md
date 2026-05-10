# SpecForge Pipeline Contract

## Goal

Turn a short project requirement or requirements document into a bootable Spring Boot backend by driving the SpecForge compiler pipeline end to end.

## Preconditions

- Work inside a repository that contains:
  - `specforge-runtime/`
  - optional baseline backend template at `backend/`
- Prefer a baseline backend template when available.
- Require a resolvable JDK 17+ and Maven 3.6.3+ toolchain.

## Canonical Runtime Chain

```text
requirement
  -> project-spec
  -> project-assembly-plan
  -> module-spec(s)
  -> module-schema.resolved(s)
  -> IR lowering
  -> module synthesis
  -> project assembly
  -> compile
  -> boot verify
  -> repair loop
  -> final exported backend
```

## Stable Output Locations

- Canonical specs:
  - `specforge-runtime/specs/`
- Execution traces:
  - `specforge-runtime/runs/<run-id>/`
- Final backend export:
  - `specforge-runtime/outputs/<target-name>/`

## Non-Negotiable Invariants

- Business modules must generate only under `org.eu.originalkeen.business.*`.
- Business routes must stay under `/v1/business/*`.
- Business authorities must stay under `business:*`.
- Final success means both:
  - compile passes
  - Spring Boot context boots
- Final success also requires:
  - business contract validation passes
  - SQL asset validation passes
  - auth surface validation passes
  - expected enabled business modules are present in the exported backend
- If the request asks for a full platform rather than an MVP, the project spec and assembly plan must reflect business-center level module coverage instead of a thin skeleton.

## Completion Criteria

Return success only if:

- `auto-build-report.yaml` says `compile_status: PASS`
- `auto-build-report.yaml` says `boot_status: PASS`
- `business-contract-validation.yaml` says `validation.status: PASS`
- `delivery-validation.yaml` says `status: PASS`
- `sql-asset-validation.yaml` says `status: PASS`
- `auth-surface-validation.yaml` says `status: PASS`
- final backend exists under `specforge-runtime/outputs/`

For complete-platform requests, also require the authored spec set to cover:

- the expected business-center modules for the domain
- user/role/menu linkage as a project-level concern
- database initialization SQL organization as a project-level concern

Otherwise, preserve the failure bundle:

- `compile-diagnostics.yaml`
- `compile-repair-report.yaml`
- `boot-diagnostics.yaml`
- `boot-repair-report.yaml`
- `project-health-report.yaml`
- `auto-build-report.yaml`
