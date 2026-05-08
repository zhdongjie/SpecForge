All checks below must pass before the skill is finished.

- Confirm that exactly one target business module was generated.
- Confirm that repository naming, package layout, and layering conventions were discovered before generation.
- Confirm that the generated package root matches sibling modules in the same bounded context.
- Confirm that each generated endpoint maps to a capability in the module schema.
- Confirm that each generated artifact maps back to a declared module-schema element.
- Confirm that each capability preserved its semantic meaning rather than being flattened into a weaker CRUD approximation.
- Confirm that taxonomy-backed patterns were used for assignment, translation, hierarchy, or state transitions when those semantics exist.
- Confirm that DTO, VO, entity, mapper, manager, and service naming is internally consistent.
- Confirm that security annotations and authority strings match the repository's authorization style.
- Confirm that transaction boundaries are placed consistently with sibling modules.
- Confirm that response wrappers, exception handling, and validation style match adjacent modules.
- Confirm that logging annotations or audit hooks are applied consistently when similar mutations are logged elsewhere.
- Confirm that cross-module dependencies are explicit and minimal.
- Confirm that semantic invariants and generation contract requirements from the specification are preserved.
- Confirm that no unrelated module was rewritten just for stylistic cleanup.
- Confirm that generation contracts from the project specification and `generation-contract.md` were preserved.
- Confirm that the module remains compatible with modular-monolith boundaries and future DAG-style generation.
- Confirm that a repeat run against the same repository and specification would not require a materially different module layout.
