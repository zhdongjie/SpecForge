Architecture discovery workflow:

1. Identify repository root conventions.
   - package root
   - module directory layout
   - naming suffixes
   - layering order

2. Identify domain artifact conventions.
   - entity location and base classes
   - dto, vo, bo naming
   - manager, service, service.impl, mapper usage
   - controller or resource naming

3. Identify cross-cutting conventions.
   - security annotations and authority expression style
   - response wrapper type
   - exception handling pattern
   - transaction placement
   - validation annotations
   - logging or audit annotations

4. Identify persistence conventions.
   - ORM or mapper framework
   - query dto patterns
   - page response pattern
   - translation or localization model when present

5. Identify bounded-context conventions.
   - sibling modules in the same business area
   - whether module names reflect business nouns, workflows, or admin domains
   - acceptable external dependencies

6. Record the strongest evidence before generation.
   - which files define the conventions
   - which conventions are mandatory versus inferred

Discovery rule:

- Prefer local project evidence over framework defaults.
- If conventions conflict, follow the most repeated pattern in the nearest sibling modules.
- If no strong convention exists, choose the smallest deterministic pattern that fits the current repository.
