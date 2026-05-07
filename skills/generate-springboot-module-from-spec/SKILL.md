---
name: generate-springboot-module-from-spec
description: Generate one Spring Boot business module from a structured project specification while preserving existing architecture conventions, modular-monolith boundaries, CRUD standardization, and regeneration contracts. Use when Codex must add or regenerate a bounded backend module inside an existing Spring Boot codebase with deterministic, production-oriented behavior instead of creative reinterpretation.
---

# Generate Spring Boot Module From Spec

Generate exactly one bounded Spring Boot business module from a structured specification and the current repository conventions. Optimize for deterministic regeneration, convention matching, and contract preservation.

## Core Objective

- Generate exactly one business module per run.
- Reuse the repository's established architecture instead of introducing a new one.
- Preserve modular-monolith boundaries and generation contracts from the input specification.
- Standardize CRUD-style capabilities into repeatable artifact patterns.
- Keep the output compatible with future DAG-style generation by treating cross-module relationships as explicit dependencies rather than implicit rewrites.

## Phase Ordering

Complete the phases in order. Do not skip ahead to code generation before discovery, planning, and validation gates are satisfied.

1. Discover architecture conventions.
2. Interpret the requested capability scope.
3. Build an internal module generation plan.
4. Generate code for one bounded module only.
5. Validate consistency before finishing.

## Phase 1: Discover Architecture Conventions

- Inspect the current codebase before generating anything.
- Use `references/architecture-discovery.md` to identify package layout, naming, layering, security, logging, validation, persistence, and response conventions.
- Prefer explicit repository evidence over generic Spring Boot defaults.
- If the repository is sparse, infer the minimum viable convention set from the strongest local signals.
- Do not create a new architectural style when a convention already exists.

## Phase 2: Interpret Capability Scope

- Read the structured project specification and isolate the single target module to generate.
- Translate business capabilities into standardized capability patterns using `references/capability-taxonomy.yaml`.
- Separate in-module responsibilities from cross-module dependencies.
- Preserve bounded-context language from the specification.
- Reject scope creep: if the request would require multiple modules, generate only the target one and treat the others as dependencies or contracts.

## Phase 3: Build the Internal Module Plan

- Build an internal plan that conforms to `references/output-schema.yaml`.
- Include the module name, package root, bounded context, artifact list, capabilities, authorities, routes, persistence needs, and dependency edges.
- Preserve generation contracts from the project specification.
- Use deterministic artifact mapping:
  - business capability -> resource endpoint group
  - state mutation -> manager/service transaction boundary
  - query capability -> page/details/list/tree/read pattern
  - persistence concept -> entity/mapper/service artifact set
- Do not expose the internal plan unless the user explicitly asks for it.

## Phase 4: Generate One Bounded Module

- Generate exactly one Spring Boot module and only the directly required supporting artifacts.
- Match existing package names, suffixes, annotations, and layering conventions.
- Prefer established repository patterns for:
  - `resource`
  - `manager`
  - `service`
  - `service.impl`
  - `mapper`
  - `domain.entity`
  - `domain.dto`
  - `domain.vo`
  - `domain.bo` when the repository already uses it
- Standardize CRUD capabilities using the capability taxonomy rather than inventing bespoke controller or service shapes.
- Preserve existing response wrappers, exception patterns, validation style, and security annotations.
- Keep cross-module integration explicit and minimal.

## Phase 5: Validate Before Final Output

- Apply `references/validation-checklist.md` before finishing.
- If a check fails, continue editing or tightening the implementation instead of declaring completion.
- Validate that the module is architecturally consistent even if the user did not ask for an explicit review.

## Determinism Rules

- Optimize for reproducibility, not novelty.
- Prefer repository conventions over abstract best practices when they conflict.
- Use one naming scheme consistently within the module.
- Do not introduce extra abstractions, frameworks, or layers unless the repository already requires them.
- Do not generate optional features that are not justified by the input capability set.
- Do not merge multiple business modules into one implementation.

## Bounded Module Rules

- The generated module must have a single bounded responsibility.
- External modules may be referenced only through existing contracts, services, authorities, or foreign-key style relationships already implied by the specification or repository.
- Avoid editing unrelated modules unless a small compatibility update is required for compilation or wiring.
- If a compatibility update is required outside the target module, keep it minimal and directly traceable to the new module.

## CRUD Standardization Rules

- Use taxonomy-backed capability patterns for create, update, delete, batch-delete, details, page, list, tree, uniqueness-check, and custom domain actions.
- Reuse the repository's existing route style, request style, and response style.
- Keep validation aligned with the same DTO boundary used by adjacent modules.
- Keep mutation logging and authorization checks consistent with sibling modules.

## Modular-Monolith and DAG Compatibility

- Treat module generation as a node in a larger dependency graph.
- Make inbound and outbound dependencies explicit in the internal plan.
- Avoid hidden coupling through utility shortcuts or cross-module state reach-through.
- Preserve module boundaries so future generators can build other modules independently in topological order.

## Generation Contract Preservation

- Preserve explicit generation contracts from the source specification.
- Preserve architectural contracts discovered from the repository even when they are undocumented.
- If the project-spec says a boundary, authority model, CRUD policy, or translation model must remain stable, treat that as a hard constraint.

## Forbidden Behavior

- Do not generate more than one business module.
- Do not ignore repository conventions and replace them with generic scaffolding.
- Do not invent unsupported capabilities.
- Do not rewrite unrelated modules for style consistency alone.
- Do not collapse separate bounded contexts into a convenience implementation.
- Do not finalize the task before running the validation checklist.

## Resources

- Use `references/architecture-discovery.md` to discover existing implementation conventions.
- Use `references/capability-taxonomy.yaml` to map business capabilities to deterministic CRUD and non-CRUD patterns.
- Use `references/output-schema.yaml` to structure the internal generation plan.
- Use `references/validation-checklist.md` as the required gate before completion.
