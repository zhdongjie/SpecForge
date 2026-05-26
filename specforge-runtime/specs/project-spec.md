project:
  name: laboratory-reservation
  type: springboot-vue3
architecture:
  style: modular-monolith
  description: A modular-monolith Spring Boot backend compiled from SpecForge project
    and module specifications.
modules:
- name: laboratory-reservation-management
  responsibility: laboratory resource and reservation lifecycle management
  boundaries: Owns Laboratory, LaboratoryReservation within laboratory-operations.
  apis:
  - laboratory-reservation-management administration
  entities:
  - Laboratory
  - LaboratoryReservation
- name: reservation-approval-management
  responsibility: reservation approval decisions and audit trail
  boundaries: Owns ReservationApproval, ReservationApprovalRecord within reservation-governance.
  apis:
  - reservation-approval-management administration
  entities:
  - ReservationApproval
  - ReservationApprovalRecord
- name: laboratory-access-management
  responsibility: laboratory access scope and reservable policy management
  boundaries: Owns LaboratoryAccessPolicy, LaboratoryAccessScope within laboratory-access-control.
  apis:
  - laboratory-access-management administration
  entities:
  - LaboratoryAccessPolicy
  - LaboratoryAccessScope
- name: equipment-management
  responsibility: laboratory equipment lifecycle and maintenance management
  boundaries: Owns LaboratoryEquipment, EquipmentMaintenanceRecord within equipment-center.
  apis:
  - equipment-management administration
  entities:
  - LaboratoryEquipment
  - EquipmentMaintenanceRecord
- name: consumable-inventory-management
  responsibility: laboratory consumable stock and inventory management
  boundaries: Owns ConsumableItem, ConsumableStockRecord within consumable-inventory-center.
  apis:
  - consumable-inventory-management administration
  entities:
  - ConsumableItem
  - ConsumableStockRecord
- name: experiment-project-management
  responsibility: experiment project planning and member management
  boundaries: Owns ExperimentProject, ExperimentProjectMember within experiment-project-center.
  apis:
  - experiment-project-management administration
  entities:
  - ExperimentProject
  - ExperimentProjectMember
- name: schedule-calendar-management
  responsibility: laboratory schedule and calendar event management
  boundaries: Owns ScheduleCalendar, ScheduleCalendarEvent within schedule-calendar-center.
  apis:
  - schedule-calendar-management administration
  entities:
  - ScheduleCalendar
  - ScheduleCalendarEvent
- name: report-statistics-management
  responsibility: laboratory reporting and statistics snapshot management
  boundaries: Owns ReservationStatisticSnapshot, EquipmentUsageReport within report-statistics-center.
  apis:
  - report-statistics-management administration
  entities:
  - ReservationStatisticSnapshot
  - EquipmentUsageReport
- name: notification-management
  responsibility: laboratory workflow and approval notifications
  boundaries: Owns NotificationMessage, NotificationDeliveryRecord within notification-center.
  apis:
  - notification-management administration
  entities:
  - NotificationMessage
  - NotificationDeliveryRecord
features:
- Support Laboratory Reservation Management workflows.
- Support Reservation Approval Management workflows.
- Support Laboratory Access Management workflows.
- Support Equipment Management workflows.
- Support Consumable Inventory Management workflows.
- Support Experiment Project Management workflows.
- Support Schedule Calendar Management workflows.
- Support Report Statistics Management workflows.
- Support Notification Management workflows.
auth:
  type: jwt
  roles:
  - Administrator
  - Teacher
  - Student
  - LabManager
database:
  type: mysql
  tables:
  - name: system_laboratory
    purpose: Persistence for laboratory-reservation-management
  - name: system_laboratory_reservation
    purpose: Persistence for laboratory-reservation-management
  - name: reservation_approval
    purpose: Persistence for reservation-approval-management
  - name: reservation_approval_record
    purpose: Persistence for reservation-approval-management
  - name: laboratory_access_policy
    purpose: Persistence for laboratory-access-management
  - name: laboratory_access_scope
    purpose: Persistence for laboratory-access-management
  - name: laboratory_equipment
    purpose: Persistence for equipment-management
  - name: equipment_maintenance_record
    purpose: Persistence for equipment-management
  - name: consumable_item
    purpose: Persistence for consumable-inventory-management
  - name: consumable_stock_record
    purpose: Persistence for consumable-inventory-management
  - name: experiment_project
    purpose: Persistence for experiment-project-management
  - name: experiment_project_member
    purpose: Persistence for experiment-project-management
  - name: schedule_calendar
    purpose: Persistence for schedule-calendar-management
  - name: schedule_calendar_event
    purpose: Persistence for schedule-calendar-management
  - name: reservation_statistic_snapshot
    purpose: Persistence for report-statistics-management
  - name: equipment_usage_report
    purpose: Persistence for report-statistics-management
  - name: notification_message
    purpose: Persistence for notification-management
  - name: notification_delivery_record
    purpose: Persistence for notification-management
frontend:
  pages: []
business_rules:
- laboratory reservation slots must not conflict within the same laboratory
- equipment usage actions must reference an existing laboratory and equipment record
- consumable inventory actions must remain behind centralized JWT authorization
- experiment project operations must preserve modular business boundaries
- 'Build a graduation project: laboratory reservation management system. It must support
  login, laboratory room management, equipment management, reservation orders, approval
  workflow, reservation cancellation, status tracking, and admin statistics. Generate
  real business CRUD modules for laboratory rooms, equipment, and reservation orders.'
dependencies:
  backend:
  - Spring Boot
  - Spring Security
  - Spring Validation
  - MyBatis-Flex
  - MySQL
  - Redis
  - Jose4j
  frontend: []
generation_contract:
- Preserve modular-monolith boundaries.
- Keep business-domain code under org.eu.originalkeen.business.*.
- Require compile and boot verification before success.
