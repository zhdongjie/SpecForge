All checks below must pass before the skill is finished.

- Confirm that exactly one target business module was generated.
- Confirm that repository naming, package layout, and layering conventions were discovered before generation.
- Confirm that the generated package root matches sibling modules in the same bounded context.
- Confirm that each generated endpoint maps to a capability in the module plan.
- Confirm that CRUD-like capabilities follow the repository's standard artifact pattern.
- Confirm that DTO, VO, entity, mapper, manager, and service naming is internally consistent.
- Confirm that security annotations and authority strings match the repository's authorization style.
- Confirm that transaction boundaries are placed consistently with sibling modules.
- Confirm that response wrappers, exception handling, and validation style match adjacent modules.
- Confirm that logging annotations or audit hooks are applied consistently when similar mutations are logged elsewhere.
- Confirm that cross-module dependencies are explicit and minimal.
- Confirm that no unrelated module was rewritten just for stylistic cleanup.
- Confirm that generation contracts from the project specification were preserved.
- Confirm that the module remains compatible with modular-monolith boundaries and future DAG-style generation.
