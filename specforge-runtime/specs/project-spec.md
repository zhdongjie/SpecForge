project:
  name: Dormitory Management Platform
  type: springboot-vue3
  platform_scope: complete-platform
architecture:
  style: modular-monolith
  description: A modular-monolith Spring Boot backend compiled from SpecForge project
    and module specifications.
modules:
- name: dormitory-building-management
  responsibility: dormitory building, floor, and physical capacity management
  boundaries: Owns DormitoryBuilding, DormitoryFloor within dormitory-building-center.
  apis:
  - dormitory-building-management administration
  entities:
  - DormitoryBuilding
  - DormitoryFloor
- name: room-bed-allocation-management
  responsibility: room inventory, bed assignment, and occupancy allocation management
  boundaries: Owns DormitoryRoom, BedAllocation within room-bed-allocation-center.
  apis:
  - room-bed-allocation-management administration
  entities:
  - DormitoryRoom
  - BedAllocation
- name: move-in-out-management
  responsibility: student accommodation check-in and check-out lifecycle management
  boundaries: Owns MoveInRecord, MoveOutRecord within move-in-move-out-center.
  apis:
  - move-in-out-management administration
  entities:
  - MoveInRecord
  - MoveOutRecord
- name: repair-maintenance-management
  responsibility: dormitory repair reporting and maintenance dispatch management
  boundaries: Owns RepairWorkOrder, MaintenanceDispatchRecord within repair-maintenance-center.
  apis:
  - repair-maintenance-management administration
  entities:
  - RepairWorkOrder
  - MaintenanceDispatchRecord
- name: visitor-access-management
  responsibility: dormitory visitor application and access record management
  boundaries: Owns VisitorAccessRequest, VisitorAccessRecord within visitor-access-center.
  apis:
  - visitor-access-management administration
  entities:
  - VisitorAccessRequest
  - VisitorAccessRecord
- name: fee-billing-management
  responsibility: accommodation billing and payment collection management
  boundaries: Owns AccommodationBill, PaymentCollectionRecord within fee-billing-center.
  apis:
  - fee-billing-management administration
  entities:
  - AccommodationBill
  - PaymentCollectionRecord
- name: hygiene-inspection-management
  responsibility: dormitory hygiene inspection and scoring management
  boundaries: Owns HygieneInspection, HygieneScoreRecord within hygiene-inspection-center.
  apis:
  - hygiene-inspection-management administration
  entities:
  - HygieneInspection
  - HygieneScoreRecord
- name: notification-management
  responsibility: accommodation event and policy notification delivery management
  boundaries: Owns DormitoryNotification, NotificationDeliveryRecord within notification-center.
  apis:
  - notification-management administration
  entities:
  - DormitoryNotification
  - NotificationDeliveryRecord
- name: report-statistics-management
  responsibility: dormitory occupancy reporting and statistics snapshot management
  boundaries: Owns DormitoryStatisticSnapshot, OccupancyStatisticReport within report-statistics-center.
  apis:
  - report-statistics-management administration
  entities:
  - DormitoryStatisticSnapshot
  - OccupancyStatisticReport
features:
- Support Dormitory Building Management workflows.
- Support Room Bed Allocation Management workflows.
- Support Move In Out Management workflows.
- Support Repair Maintenance Management workflows.
- Support Visitor Access Management workflows.
- Support Fee Billing Management workflows.
- Support Hygiene Inspection Management workflows.
- Support Notification Management workflows.
- Support Report Statistics Management workflows.
- Preserve business-center coverage for dormitory-building-center.
- Preserve business-center coverage for room-bed-allocation-center.
- Preserve business-center coverage for move-in-move-out-center.
- Preserve business-center coverage for repair-maintenance-center.
- Preserve business-center coverage for visitor-access-center.
- Preserve business-center coverage for fee-billing-center.
- Preserve business-center coverage for hygiene-inspection-center.
- Preserve business-center coverage for notification-center.
- Preserve business-center coverage for report-statistics-center.
auth:
  type: jwt
  roles:
  - Administrator
  - DormitoryManager
  - Student
  - Counselor
database:
  type: mysql
  tables:
  - name: dormitory_building
    purpose: Persistence for dormitory-building-management
  - name: dormitory_floor
    purpose: Persistence for dormitory-building-management
  - name: dormitory_room
    purpose: Persistence for room-bed-allocation-management
  - name: bed_allocation
    purpose: Persistence for room-bed-allocation-management
  - name: move_in_record
    purpose: Persistence for move-in-out-management
  - name: move_out_record
    purpose: Persistence for move-in-out-management
  - name: repair_work_order
    purpose: Persistence for repair-maintenance-management
  - name: maintenance_dispatch_record
    purpose: Persistence for repair-maintenance-management
  - name: visitor_access_request
    purpose: Persistence for visitor-access-management
  - name: visitor_access_record
    purpose: Persistence for visitor-access-management
  - name: accommodation_bill
    purpose: Persistence for fee-billing-management
  - name: payment_collection_record
    purpose: Persistence for fee-billing-management
  - name: hygiene_inspection
    purpose: Persistence for hygiene-inspection-management
  - name: hygiene_score_record
    purpose: Persistence for hygiene-inspection-management
  - name: dormitory_notification
    purpose: Persistence for notification-management
  - name: notification_delivery_record
    purpose: Persistence for notification-management
  - name: dormitory_statistic_snapshot
    purpose: Persistence for report-statistics-management
  - name: occupancy_statistic_report
    purpose: Persistence for report-statistics-management
frontend:
  pages: []
business_rules:
- room and bed allocations must remain consistent with building, floor, and occupancy
  capacity constraints
- move-in, move-out, and visitor actions must remain behind centralized JWT authorization
- repair, hygiene, and billing workflows must stay modular with explicit business
  ownership
- reporting and notifications must reflect dormitory events without leaking across
  business boundaries
- Build a complete modular-monolith Spring Boot dormitory management backend covering
  dormitory building center, room bed allocation center, move-in move-out center,
  repair maintenance center, visitor access center, fee billing center, hygiene inspection
  center, notification center, and statistics reporting center.
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
- Preserve required business-center coverage from the selected domain profile.
