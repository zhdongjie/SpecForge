Execution discipline for this skill:

- Follow phase ordering strictly: inventory, evidence mapping, module grouping, then YAML construction.
- Do not skip any phase.
- Do not generate final YAML before completing evidence mapping and module grouping.
- Do not promote any module, role, table, page, or business rule into the final YAML unless repository evidence exists.
- If evidence is partial, contradictory, or weak, prefer `unknown`, empty arrays, or a narrower summary.
- Maintain internal working state for:
  - inventory of discovered artifacts
  - evidence map for candidate modules and cross-cutting concerns
  - grouped business modules
- Return only the final YAML document. Do not expose internal working state in the final answer.