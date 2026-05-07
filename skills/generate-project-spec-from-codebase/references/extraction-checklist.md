Before writing the final YAML, all checks below must pass. If any check fails, continue analysis instead of producing the final answer.

- Confirm whether the repository actually contains both backend and frontend artifacts.
- Identify the strongest evidence for architecture style.
- Group technical layers into business modules rather than listing package names.
- Collapse repetitive CRUD resources into business-level features.
- Confirm auth evidence from filters, interceptors, tokens, sessions, annotations, docs, or menus.
- Confirm roles only when role names are directly visible.
- Confirm database engine from datasource config, SQL dialect, migration files, or dependency names.
- List only the tables that help explain the domain.
- List only pages that map to meaningful user tasks.
- Keep business rules domain-specific and behavior-changing.
- Remove file paths, code fragments, version numbers, and framework boilerplate.
- Ensure the final answer is a single YAML document with no Markdown fence and no surrounding explanation.