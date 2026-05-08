project:
  name: Laboratory Reservation Center
  type: springboot-vue3

architecture:
  style: modular-monolith
  description: A single Spring Boot application organized around laboratory resource administration, laboratory reservation administration, centralized JWT security, shared response wrapping, and cross-cutting audit infrastructure.

modules:
  - name: laboratory-management
    responsibility: Manages laboratories as reservable resources, including identification, display naming, availability status, and administrative maintenance.
    boundaries: Owns laboratory master data and does not own reservation lifecycle decisions beyond laboratory existence and availability.
    apis:
      - Laboratory administration
      - Laboratory page query
      - Laboratory detail query
      - Laboratory list lookup
      - Laboratory uniqueness validation
    entities:
      - Laboratory
  - name: laboratory-reservation-management
    responsibility: Manages reservation records bound to laboratories, including creation, update, cancellation, administrative maintenance, and query workflows.
    boundaries: Owns reservation records and reservation time-slot constraints, but relies on laboratory-management for laboratory identity.
    apis:
      - Reservation administration
      - Reservation page query
      - Reservation detail query
      - Reservation list lookup
      - Reservation uniqueness and slot conflict validation
    entities:
      - LaboratoryReservation
      - Laboratory
  - name: audit-logging
    responsibility: Records administrative mutation traces for laboratory and reservation operations.
    boundaries: Owns audit persistence and cross-cutting logging, but not reservation business decisions.
    apis:
      - Operation log recording for create, update, and delete actions
    entities:
      - OperateLog

features:
  - Administer laboratory resources through create, update, batch delete, page query, detail query, and list query workflows.
  - Administer reservation records through create, update, batch delete, page query, detail query, and list query workflows.
  - Enforce reservation code uniqueness.
  - Enforce laboratory code and laboratory name uniqueness.
  - Enforce reservation slot uniqueness within the same laboratory and reservation time window.
  - Require all non-public APIs to remain behind centralized JWT-based authorization.
  - Record administrative mutation trails for laboratory and reservation management.

auth:
  type: jwt
  roles:
    - Admin
    - Teacher
    - Student

database:
  type: mysql
  tables:
    - name: system_laboratory
      purpose: Stores laboratory master data used for reservation administration.
    - name: system_laboratory_reservation
      purpose: Stores reservation records bound to laboratories and reservation time windows.
    - name: system_operate_log
      purpose: Stores auditable create, update, and delete operations.

frontend:
  pages: []

business_rules:
  - Only authenticated users may access laboratory and reservation administration endpoints.
  - Laboratory codes and laboratory names must remain unique.
  - Reservation codes must remain unique.
  - The same laboratory must not be reserved for the same start and end time window more than once.
  - Reservation records must always reference an existing laboratory.
  - Administrative mutation endpoints must remain protected by centralized authority-based method security.

dependencies:
  backend:
    - Spring Boot
    - Spring Web
    - Spring Security
    - Spring Validation
    - Spring AOP
    - Spring Data Redis
    - MyBatis-Flex
    - MySQL
    - Redis
    - Jose4j
    - Lombok
  frontend: []

generation_contract:
  - Rebuild the system as a single deployable backend with distinct laboratory-management and laboratory-reservation-management module boundaries.
  - Preserve authority-based centralized authorization and JWT-backed stateless API access.
  - Preserve administrative CRUD consistency across laboratory and reservation aggregates.
  - Preserve reservation-to-laboratory referential integrity.
  - Preserve slot-conflict validation as a first-class reservation invariant.
  - Preserve audit logging as shared cross-cutting infrastructure rather than embedding logging logic into controllers.
