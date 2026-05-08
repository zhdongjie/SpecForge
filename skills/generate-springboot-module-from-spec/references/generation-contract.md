Generation contract for deterministic bounded-module regeneration:

- Generate exactly one bounded business module per run.
- Preserve the repository's discovered architecture instead of introducing a parallel style.
- Preserve package layout, naming suffixes, annotation style, response wrappers, validation style, and transaction placement unless the repository itself is inconsistent.
- Preserve bounded-context boundaries; do not pull other modules into the target implementation for convenience.
- Preserve semantic capability meaning. Assignment, translation, hierarchy, policy-check, and state-transition behavior must not be collapsed into plain CRUD if that changes regeneration intent.
- Keep all cross-module dependencies explicit in the internal module schema.
- Prefer the nearest sibling module conventions over remote or generic project-wide assumptions when patterns conflict.
- Keep artifact generation deterministic: the same specification and repository context should produce materially the same module structure.
- Use the internal module schema as the authoritative intermediate representation when deciding artifacts, routes, and authorities.
- Do not add optional abstractions, background integrations, caching layers, or helper frameworks unless they are already part of the local architecture contract.
- If the specification includes invariants, authorities, translation requirements, lifecycle rules, or logging policies, reproduce them as hard constraints.
- Future DAG orchestration must be able to treat the module as an isolated node with declared inbound and outbound dependencies.
