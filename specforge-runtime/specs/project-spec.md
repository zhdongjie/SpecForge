project:
  name: Laboratory Management Platform
  type: springboot-vue3

architecture:
  style: modular-monolith
  description: A single Spring Boot backend organized around laboratory resources, experiment projects, equipment, consumable inventory, reservations, approvals, access control, notifications, scheduling, reporting, centralized JWT security, unified responses, and cross-cutting audit infrastructure.

modules:
  - name: laboratory-resource-management
    responsibility: Manages laboratory buildings and laboratory rooms as the core physical resource center.
    boundaries: Owns laboratory resource master data and room availability attributes, but does not own reservation approval or inventory transactions.
    apis:
      - Laboratory resource administration
      - Laboratory resource page query
      - Laboratory resource detail query
      - Laboratory resource list lookup
    entities:
      - LaboratoryBuilding
      - LaboratoryRoom
  - name: experiment-project-management
    responsibility: Manages experiment projects and project membership records.
    boundaries: Owns experiment project master data and project-member associations, but does not own equipment inventory or reservation scheduling.
    apis:
      - Experiment project administration
      - Experiment project page query
      - Experiment project detail query
      - Experiment project list lookup
    entities:
      - ExperimentProject
      - ExperimentProjectMember
  - name: equipment-management
    responsibility: Manages laboratory equipment and maintenance records.
    boundaries: Owns equipment master data and maintenance traces, but does not own consumable stock or reservation approval decisions.
    apis:
      - Equipment administration
      - Equipment page query
      - Equipment detail query
      - Equipment list lookup
    entities:
      - LaboratoryEquipment
      - EquipmentMaintenanceRecord
  - name: consumable-inventory-management
    responsibility: Manages consumable items and consumable stock records.
    boundaries: Owns consumable catalog and inventory movement records, but does not own experiment project approval or equipment maintenance.
    apis:
      - Consumable inventory administration
      - Consumable inventory page query
      - Consumable inventory detail query
      - Consumable inventory list lookup
    entities:
      - ConsumableItem
      - ConsumableStockRecord
  - name: laboratory-reservation-management
    responsibility: Manages laboratory reservation requests and reservation schedules.
    boundaries: Owns reservation records and time-slot scheduling, but relies on laboratory resources for room identity and approval workflows for final authorization.
    apis:
      - Laboratory reservation administration
      - Laboratory reservation page query
      - Laboratory reservation detail query
      - Laboratory reservation list lookup
    entities:
      - LaboratoryReservation
      - ReservationSchedule
  - name: reservation-approval-management
    responsibility: Manages reservation approval decisions and approval operation records.
    boundaries: Owns approval workflows and approval logs, but does not own the physical room catalog.
    apis:
      - Reservation approval administration
      - Reservation approval page query
      - Reservation approval detail query
      - Reservation approval list lookup
    entities:
      - ReservationApproval
      - ReservationApprovalRecord
  - name: laboratory-access-management
    responsibility: Manages laboratory access policies and access scopes.
    boundaries: Owns access-control policies and scope rules, but does not own JWT infrastructure or user master data.
    apis:
      - Laboratory access administration
      - Laboratory access page query
      - Laboratory access detail query
      - Laboratory access list lookup
    entities:
      - LaboratoryAccessPolicy
      - LaboratoryAccessScope
  - name: notification-management
    responsibility: Manages notification messages and notification delivery records for reservation, approval, and inventory events.
    boundaries: Owns notification persistence and delivery traces, but does not embed message logic into other controllers.
    apis:
      - Notification administration
      - Notification page query
      - Notification detail query
      - Notification list lookup
    entities:
      - NotificationMessage
      - NotificationDeliveryRecord
  - name: schedule-calendar-management
    responsibility: Manages schedule calendars and holiday rules for laboratory availability windows.
    boundaries: Owns calendar and holiday configuration, but does not own reservation approval state.
    apis:
      - Schedule calendar administration
      - Schedule calendar page query
      - Schedule calendar detail query
      - Schedule calendar list lookup
    entities:
      - ScheduleCalendar
      - HolidayRule
  - name: report-statistics-management
    responsibility: Manages report tasks and dashboard snapshots for laboratory operations oversight.
    boundaries: Owns reporting tasks and dashboard snapshots, but not the source transaction lifecycle itself.
    apis:
      - Report statistics administration
      - Report statistics page query
      - Report statistics detail query
      - Dashboard snapshot lookup
    entities:
      - ReportTask
      - DashboardSnapshot

features:
  - Administer laboratory buildings and rooms through create, update, batch delete, page query, detail query, and list query workflows.
  - Administer experiment projects and project membership records through create, update, batch delete, page query, detail query, and list query workflows.
  - Administer laboratory equipment and maintenance records through create, update, batch delete, page query, detail query, and list query workflows.
  - Administer consumable items and stock records through create, update, batch delete, page query, detail query, and list query workflows.
  - Administer laboratory reservations and reservation schedules through create, update, batch delete, page query, detail query, and list query workflows.
  - Administer reservation approvals through create, update, batch delete, page query, detail query, and list query workflows.
  - Administer laboratory access policies through create, update, batch delete, page query, detail query, and list query workflows.
  - Administer notifications through create, update, batch delete, page query, detail query, and list query workflows.
  - Administer schedule calendars and holiday rules through create, update, batch delete, page query, detail query, and list query workflows.
  - Administer report tasks and dashboard snapshots through create, update, batch delete, page query, detail query, and list query workflows.
  - Require all non-public APIs to remain behind centralized JWT-based authorization.
  - Record administrative mutation trails for laboratory platform operations.

auth:
  type: jwt
  roles:
    - Admin
    - LaboratoryManager
    - Teacher
    - Student
    - SafetyOfficer

database:
  type: mysql
  tables:
    - name: laboratory_building
      purpose: Stores laboratory building master data.
    - name: laboratory_room
      purpose: Stores laboratory room master data.
    - name: experiment_project
      purpose: Stores experiment project master data.
    - name: experiment_project_member
      purpose: Stores experiment project member records.
    - name: laboratory_equipment
      purpose: Stores laboratory equipment master data.
    - name: equipment_maintenance_record
      purpose: Stores equipment maintenance trace records.
    - name: consumable_item
      purpose: Stores consumable item catalog data.
    - name: consumable_stock_record
      purpose: Stores consumable stock movement records.
    - name: laboratory_reservation
      purpose: Stores laboratory reservation requests.
    - name: reservation_schedule
      purpose: Stores reservation schedule records.
    - name: reservation_approval
      purpose: Stores reservation approval decisions.
    - name: reservation_approval_record
      purpose: Stores reservation approval operation records.
    - name: laboratory_access_policy
      purpose: Stores laboratory access policy configuration.
    - name: laboratory_access_scope
      purpose: Stores laboratory access scope records.
    - name: notification_message
      purpose: Stores outbound notification messages.
    - name: notification_delivery_record
      purpose: Stores notification delivery traces.
    - name: schedule_calendar
      purpose: Stores schedule calendar records.
    - name: holiday_rule
      purpose: Stores holiday and unavailable-day rules.
    - name: report_task
      purpose: Stores report task definitions.
    - name: dashboard_snapshot
      purpose: Stores dashboard snapshot records.

frontend:
  pages: []

business_rules:
  - Only authenticated users may access laboratory administration endpoints.
  - Reservation and access workflows must remain protected by centralized authority-based method security.
  - Notifications should remain a bounded business module and not be embedded into reservation or approval controllers.
  - Equipment, consumables, schedules, and reservations should remain separate business centers rather than being collapsed into one oversized module.
  - User, role, and menu linkage should be described as a project-level concern for platform integration.
  - Database initialization SQL should be organized as a project-level deliverable surface.

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
  - Rebuild the system as a single deployable backend with distinct laboratory resource, project, equipment, inventory, reservation, approval, access, notification, calendar, and reporting module boundaries.
  - Preserve authority-based centralized authorization and JWT-backed stateless API access.
  - Preserve administrative CRUD consistency across all laboratory business aggregates.
  - Preserve notification management as a separate business module rather than embedding messaging logic into other controllers.
  - Preserve user, role, and menu linkage as a documented platform-level concern.
  - Preserve database initialization SQL organization as a project-level deliverable.
