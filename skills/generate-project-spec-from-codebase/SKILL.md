---
name: generate-project-spec-from-codebase
description: Analyze an existing Spring Boot and Vue3 repository and extract an implementation-agnostic YAML project specification that another Codex agent can use to regenerate the system from scratch. Use when reverse-engineering full-stack business modules, features, auth, database tables, frontend pages, and project-level regeneration constraints from code without outputting code.
---

# Generate Project Spec From Codebase

Extract a business-oriented project specification from a Spring Boot plus Vue3 codebase. Return only valid YAML that captures the system shape well enough for another agent to rebuild the project from scratch without copying implementation details.

## Workflow

Complete each phase in order. Do not skip ahead to YAML generation before the evidence and grouping phases are complete.

1. Confirm the repository shape.
   Inspect backend, frontend, configuration, SQL, and docs to determine whether the project is a monolith or modular monolith and whether Vue3 is present.

2. Gather evidence before summarizing.
   Prefer configuration, route definitions, entities, schema files, menu/page definitions, and README-level business descriptions over file naming guesses.

3. Group code into business modules.
   Merge controllers, services, entities, mappers, and frontend pages into conceptual domain modules. Group by business responsibility, not by package or technical layer.

4. Extract business-facing capabilities.
   Summarize what the system lets users do. Collapse repetitive CRUD endpoints into concise feature language.

5. Identify cross-cutting concerns.
   Infer auth type, roles, database type, page families, and major business rules from the strongest repository evidence available.

6. Emit strict YAML only.
   Follow the schema in `references/output-schema.yaml`. Do not add prose before or after the YAML document.

## Phase Rules

### Phase 1: Inventory

- Identify the available backend, frontend, database, and documentation evidence.
- Do not infer modules, roles, tables, or pages in this phase.
- If the repository shape is still unclear, continue gathering evidence instead of summarizing.

### Phase 2: Evidence Mapping

- Build an internal evidence map that links likely modules, auth signals, tables, pages, and business rules to repository evidence.
- Require evidence coverage before promoting any item into the final YAML.
- If evidence is missing or contradictory, keep the item unresolved and continue investigating.

### Phase 3: Module Grouping

- Convert technical artifacts into business modules only after evidence mapping is complete.
- Group by business workflow or bounded context, not by package layout.
- Exclude infrastructure-only concerns from module lists.

### Phase 4: YAML Construction

- Construct the final YAML only after the prior phases are internally consistent.
- Include only items that survived evidence review and grouping.
- Fall back to `unknown` or empty arrays where evidence remains insufficient.

## Extraction Rules

- Focus on business meaning rather than code structure.
- Prefer stable abstractions over file-level detail.
- Treat backend and frontend artifacts as evidence for the same business domain.
- Merge similar resources into one module when they belong to the same workflow or bounded context.
- Infer CRUD patterns from repeated create/read/update/delete flows, but describe them in business terms.
- Exclude framework wiring, generated code, boilerplate configuration, DTO-only noise, and infrastructure-only packages from `modules` and `features`.
- Preserve terminology that appears consistently across the repository.

## Evidence Priority

- Prefer explicit configuration over naming conventions.
- Prefer entity relationships and schema definitions over endpoint names.
- Prefer router, menu, and page titles over component file names.
- Prefer repeated evidence across backend and frontend over isolated hints from one file.
- If evidence conflicts, choose the interpretation supported by the most independent signals and keep wording conservative.

## Conservative Inference Rules

- Never invent modules, roles, tables, or pages without repository evidence.
- Never generate final YAML directly from naming intuition alone.
- If auth exists but the mechanism is unclear, set `auth.type: none` only when the repository strongly suggests no auth; otherwise use the closest supported type only when evidence is clear.
- If the database engine cannot be confirmed, set `database.type: unknown`.
- If a frontend is absent or not discoverable, return `frontend.pages: []`.
- If tables or pages exist but exact purpose is unclear, describe the most defensible business purpose in neutral language.
- When a section has weak evidence, prefer `unknown`, empty arrays, or shorter summaries over confident guesses.

## Section Guidance

### architecture

- Set `style` to `monolith` unless there is meaningful module separation with preserved domain boundaries inside one deployable unit.
- Describe architecture in terms of domain organization, not package layout.

### modules

- Each module should represent a business domain or workflow.
- `responsibility` should explain the business job of the module.
- `boundaries` should explain what belongs inside the module and what should stay outside it.
- `apis` should list business-facing API groups or capabilities, not low-level routes.
- `entities` should list core domain nouns, not DTOs or utility classes.

### features

- Write concise business capabilities.
- Merge obvious CRUD variants into one feature when appropriate.

### auth

- Use `jwt`, `session`, or `none` only.
- List only roles that have direct repository evidence from annotations, menus, seed data, docs, or permission mappings.

### database

- Capture the likely engine and the core tables needed to understand the domain.
- Table `purpose` should explain why the table exists in the business model.

### frontend

- List meaningful pages or page groups that correspond to user tasks.
- Avoid atomic UI pieces, dialogs, and shared components.

### business_rules

- Include only domain rules with behavioral impact, such as status transitions, uniqueness constraints, approval conditions, ownership limits, or cross-module dependencies.
- Exclude generic pagination, logging, framework validation, and other technical mechanics unless they encode business policy.

### dependencies

- List major frameworks, libraries, or platform integrations by product name only.
- Do not include versions.

### generation_contract

- Keep the required baseline constraints from the schema reference.
- Add project-specific regeneration rules inferred from the repository.
- Ensure the final contract preserves module boundaries, auth centralization, CRUD consistency, vocabulary consistency, and important business workflows.

## Output Constraints

- Return only one valid YAML document.
- Do not output code.
- Do not mention file paths.
- Do not explain Spring Boot, Vue3, or framework syntax.
- Do not include implementation trivia, class inventories, or dependency versions.
- Do not wrap the YAML in Markdown fences.

## Resources

- Use `references/output-schema.yaml` as the exact output skeleton and allowed fields.
- Use `references/extraction-checklist.md` as a required gate before writing the final YAML.
- Use `references/execution-guard.md` as the hard execution discipline for phase ordering and anti-hallucination behavior.