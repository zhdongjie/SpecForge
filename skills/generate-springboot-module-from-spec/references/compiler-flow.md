Semantic compiler flow for bounded-module regeneration:

1. Read the module spec as semantic source input.
   - isolate one target module
   - enumerate capabilities
   - capture invariants, dependencies, and contract requirements

2. Discover repository conventions.
   - inspect nearest sibling modules
   - identify package, annotation, transaction, security, and persistence patterns
   - record stability anchors

3. Normalize capabilities.
   - map each semantic intent into the capability taxonomy
   - preserve richer semantics such as translation, assignment, hierarchy, and state transitions
   - mark any repo-dependent mappings explicitly

4. Build the internal module schema.
   - produce the compiler-context, module-identity, capability-set, dependency-graph, artifact-graph, and invariants
   - treat this schema as the authoritative intermediate representation

5. Generate bounded output.
   - emit only the target module and minimal compatibility edits
   - keep artifact naming and layering consistent with sibling modules

6. Validate determinism and contract preservation.
   - run the validation checklist
   - confirm the output could be regenerated with materially the same shape from the same inputs
