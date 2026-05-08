# Default Project Inference

Use this file when the user gives only a project name or a very short requirement.

## Inference Goal

Expand a short requirement into a practical graduation-project backend plan without asking follow-up questions unless a major ambiguity would change module boundaries or platform architecture.

## Default Platform Assumptions

- architecture: modular-monolith
- backend: Spring Boot
- auth: JWT
- response contract: unified wrapper
- pagination: standard page query/page result
- audit: create/update/delete traceability
- database: MySQL unless the user explicitly says otherwise
- cache: Redis enabled if auth/session/token flow benefits from it

## Default Business Inference

Infer:

- primary actor roles
- primary managed resources
- main transaction lifecycle
- approval requirements
- notification requirements
- reporting or statistics surface

## Default Module Split

For a broad business platform, start from this split and merge only when the domain is truly small:

- master-data or resource management
- transaction or workflow management
- approval management
- notification management
- access or policy management

## Laboratory Reservation Default

For a laboratory reservation platform, prefer:

- `laboratory-resource-management`
- `laboratory-reservation-management`
- `reservation-approval-management`
- `notification-management`
- `laboratory-access-management`

Possible supporting system capabilities:

- reservation rules
- open-time calendar
- conflict checking
- user role and laboratory scope control
- reservation status history
- approval comments
- message delivery records

## Under-Specification Rule

If the user gives only a project title:

1. infer the smallest credible full-system module set
2. enable validated blueprint modules by default in the assembly plan, and only disable modules that fall outside verified synthesis coverage
3. fully enable only the modules with sufficient semantic detail to synthesize safely
4. continue the pipeline for enabled modules rather than stalling
