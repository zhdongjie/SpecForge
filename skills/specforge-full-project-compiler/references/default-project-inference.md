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

For a graduation-project platform that sounds like an industry management system, do not stop at the minimal split above.
Prefer a business-center level design with roughly 8-12 bounded modules when the domain naturally supports it.

Typical complete-platform business centers include:

- product center
- customer center
- policy or order center
- approval or underwriting center
- claim or after-sales center
- payment center
- renewal or lifecycle center
- channel or agent center
- notification center
- statistics or reporting center

Also infer non-module deliverable expectations when the user asks for a "complete" project:

- user/role/menu linkage explanation
- database initialization SQL organization
- business module boundary explanation
- compile and boot verified backend export

Do not reduce a platform requirement to 3-4 modules unless the user explicitly asks for an MVP.

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

1. infer a credible full-system module set at business-center granularity
2. include surrounding support surfaces such as notification, reporting, and lifecycle modules when they are typical for the domain
3. include user/role/menu linkage and database initialization SQL as expected deliverable surfaces
4. enable validated blueprint modules by default in the assembly plan, and only disable modules that fall outside verified synthesis coverage
5. fully enable only the modules with sufficient semantic detail to synthesize safely
6. continue the pipeline for enabled modules rather than stalling

## Insurance Platform Default

For an insurance management platform, prefer a complete split close to:

- `insurance-product-center`
- `insurance-customer-center`
- `insurance-policy-center`
- `underwriting-approval-center`
- `insurance-claim-center`
- `premium-payment-center`
- `policy-renewal-center`
- `channel-agent-center`
- `notification-center`
- `report-statistics-center`

Expected supporting deliverables:

- user, role, and menu linkage description
- database initialization SQL organization
- centralized JWT auth and authority mapping
- bootable backend export
