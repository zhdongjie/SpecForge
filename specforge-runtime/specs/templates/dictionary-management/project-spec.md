project:
  name: Original Keen Auth Center
  type: springboot-vue3

architecture:
  style: modular-monolith
  description: A single Spring Boot application organized into distinct authorization, personal-center, and system-administration domains, with centralized JWT security, Redis-backed session state, and shared auditing and localization infrastructure.

modules:
  - name: authorization
    responsibility: Handles account registration, credential-based login, token refresh, and public username availability checks.
    boundaries: Owns public access flows and token lifecycle, while delegating persistent user, role, and permission data to the system administration domain.
    apis:
      - Public account registration
      - User login and JWT issuance
      - Access and refresh token renewal
      - Username availability validation for sign-up
    entities:
      - User
      - UserRole
      - Role
      - Permission
  - name: personal-center
    responsibility: Lets authenticated users inspect their own profile, roles, permissions, and change their password.
    boundaries: Owns self-service account actions for the current user and does not manage other users or global authorization structures.
    apis:
      - Current user profile retrieval
      - Self-service password change
      - Username availability validation for profile updates
    entities:
      - User
      - Role
      - Permission
  - name: user-access-management
    responsibility: Manages internal users, roles, permissions, and their assignments for back-office administration.
    boundaries: Owns administrative CRUD workflows for identity and access control data, including permission trees and user-role-role-permission relationships.
    apis:
      - User administration
      - Role administration
      - Permission tree administration
      - Role list lookup for assignment workflows
      - Uniqueness validation for usernames, role names, role codes, permission names, and authorities
    entities:
      - User
      - Role
      - Permission
      - UserRole
      - RolePermission
      - RoleTranslation
      - PermissionTranslation
  - name: dictionary-management
    responsibility: Maintains configurable dictionary types and dictionary values with multilingual labels for system-wide options.
    boundaries: Owns reusable reference data and translations used by other domains, but not the business workflows that consume those values.
    apis:
      - Dictionary type administration
      - Dictionary value administration
      - Dictionary option list lookup by type code
      - Uniqueness validation for dictionary type names, codes, labels, and values
    entities:
      - DictionaryType
      - DictionaryTypeTranslation
      - DictionaryData
      - DictionaryDataTranslation
  - name: audit-logging
    responsibility: Persists access and operation audit trails for authentication and administrative actions.
    boundaries: Owns log storage and asynchronous audit recording, but does not expose business CRUD workflows of its own.
    apis:
      - Access log recording for register and login events
      - Operation log recording for create, update, and delete administration actions
    entities:
      - AccessLog
      - OperateLog

features:
  - Register new accounts after validating username availability.
  - Authenticate users with JWT access and refresh tokens backed by Redis login state.
  - Let authenticated users view their own profile, roles, permissions, and change their password.
  - Administer users through paginated listing, detail viewing, creation, update, and batch deletion.
  - Administer roles with uniqueness validation, paginated listing, detail viewing, assignment-ready lists, creation, update, and batch deletion.
  - Administer permission nodes as a hierarchical tree with uniqueness validation and CRUD operations.
  - Administer multilingual dictionary types and dictionary values, including list lookups for UI options.
  - Record access and operation audit trails for security-sensitive and administrative actions.

auth:
  type: jwt
  roles:
    - Admin
    - User

database:
  type: mysql
  tables:
    - name: system_user
      purpose: Stores user identities, contact fields, and encoded passwords for authentication and administration.
    - name: system_role
      purpose: Stores role definitions that group permissions for access control.
    - name: system_user_role
      purpose: Maps users to roles.
    - name: system_permission
      purpose: Stores hierarchical permission nodes and authorities used for authorization and navigation structures.
    - name: system_role_permission
      purpose: Maps roles to permissions.
    - name: system_role_translation
      purpose: Stores localized role names and descriptions.
    - name: system_permission_translation
      purpose: Stores localized permission labels and descriptions.
    - name: system_dictionary_type
      purpose: Stores dictionary type definitions for configurable reference data.
    - name: system_dictionary_type_translation
      purpose: Stores localized dictionary type names and descriptions.
    - name: system_dictionary_data
      purpose: Stores dictionary values under a dictionary type.
    - name: system_dictionary_data_translation
      purpose: Stores localized dictionary value labels.
    - name: system_access_log
      purpose: Stores register, login, and logout access events with environment context and result status.
    - name: system_operate_log
      purpose: Stores auditable create, update, and delete operations triggered by administrative actions.

frontend:
  pages: []

business_rules:
  - Only authorization endpoints are public; all other APIs require authenticated access.
  - Access control is authority-based, with endpoint access enforced through centralized method security.
  - Access tokens and refresh tokens must belong to the same user before token renewal is allowed.
  - Refreshing tokens extends the cached login state in Redis rather than creating an independent session model.
  - Users can change their password only after providing the correct current password.
  - Usernames, role names, role codes, permission names, permission authorities, dictionary type names, dictionary type codes, dictionary data labels, and dictionary data values must remain unique within their respective scopes.
  - Permissions are modeled as a tree and role assignments are built from those permission nodes.
  - Localized names for roles, permissions, dictionary types, and dictionary values must remain available for at least Chinese and English contexts.

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
  - Rebuild the system as a single deployable backend with clearly separated authorization, personal-center, user-access-management, dictionary-management, and audit-logging domains.
  - Keep JWT authentication stateless at the API layer while preserving Redis-backed login state for refresh-token and current-user workflows.
  - Preserve authority-based authorization and keep endpoint protection centralized rather than embedding ad hoc permission logic inside controllers.
  - Keep permission management tree-based and preserve the role-to-permission and user-to-role relationship model.
  - Preserve the multilingual translation model for roles, permissions, dictionary types, and dictionary values.
  - Keep administrative CRUD workflows consistent across users, roles, permissions, dictionary types, and dictionary values, including uniqueness checks and paginated enquiry patterns.
  - Preserve self-service personal-center behavior as distinct from back-office user administration.
  - Continue recording access events and administrative mutations as audit logs through shared cross-cutting infrastructure.
