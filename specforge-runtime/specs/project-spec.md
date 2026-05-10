project:
  name: Library Management Platform
  type: springboot-vue3
  platform_scope: complete-platform
architecture:
  style: modular-monolith
  description: A modular-monolith Spring Boot backend compiled from SpecForge project
    and module specifications.
modules:
- name: book-catalog-management
  responsibility: book catalog metadata and copy lifecycle management
  boundaries: Owns BookCatalog, BookCopy within book-catalog-center.
  apis:
  - book-catalog-management administration
  entities:
  - BookCatalog
  - BookCopy
- name: reader-membership-management
  responsibility: reader account, eligibility, and membership lifecycle management
  boundaries: Owns ReaderProfile, ReaderMembership within reader-membership-center.
  apis:
  - reader-membership-management administration
  entities:
  - ReaderProfile
  - ReaderMembership
- name: circulation-borrow-management
  responsibility: borrowing order placement and circulation record management
  boundaries: Owns BorrowOrder, BorrowRecord within circulation-borrow-center.
  apis:
  - circulation-borrow-management administration
  entities:
  - BorrowOrder
  - BorrowRecord
- name: return-inspection-management
  responsibility: return review, overdue handling, and damage assessment management
  boundaries: Owns ReturnInspection, FineAssessment within return-inspection-center.
  apis:
  - return-inspection-management administration
  entities:
  - ReturnInspection
  - FineAssessment
- name: reservation-queue-management
  responsibility: reservation queue, waiting list, and fulfillment management
  boundaries: Owns BookReservation, ReservationQueueEntry within reservation-queue-center.
  apis:
  - reservation-queue-management administration
  entities:
  - BookReservation
  - ReservationQueueEntry
- name: acquisition-supplier-management
  responsibility: procurement planning and supplier collaboration management
  boundaries: Owns BookAcquisition, SupplierProfile within acquisition-supplier-center.
  apis:
  - acquisition-supplier-management administration
  entities:
  - BookAcquisition
  - SupplierProfile
- name: shelf-inventory-management
  responsibility: shelf organization, stocktake, and in-library inventory management
  boundaries: Owns ShelfLocation, InventoryCheckRecord within shelf-inventory-center.
  apis:
  - shelf-inventory-management administration
  entities:
  - ShelfLocation
  - InventoryCheckRecord
- name: notification-management
  responsibility: borrowing reminder and reader notification delivery management
  boundaries: Owns LibraryNotification, NotificationDeliveryRecord within notification-center.
  apis:
  - notification-management administration
  entities:
  - LibraryNotification
  - NotificationDeliveryRecord
- name: report-statistics-management
  responsibility: library circulation reporting and statistics snapshot management
  boundaries: Owns LibraryStatisticSnapshot, BorrowStatisticReport within report-statistics-center.
  apis:
  - report-statistics-management administration
  entities:
  - LibraryStatisticSnapshot
  - BorrowStatisticReport
features:
- Support Book Catalog Management workflows.
- Support Reader Membership Management workflows.
- Support Circulation Borrow Management workflows.
- Support Return Inspection Management workflows.
- Support Reservation Queue Management workflows.
- Support Acquisition Supplier Management workflows.
- Support Shelf Inventory Management workflows.
- Support Notification Management workflows.
- Support Report Statistics Management workflows.
- Preserve business-center coverage for book-catalog-center.
- Preserve business-center coverage for reader-membership-center.
- Preserve business-center coverage for circulation-borrow-center.
- Preserve business-center coverage for return-inspection-center.
- Preserve business-center coverage for reservation-queue-center.
- Preserve business-center coverage for acquisition-supplier-center.
- Preserve business-center coverage for shelf-inventory-center.
- Preserve business-center coverage for notification-center.
- Preserve business-center coverage for report-statistics-center.
auth:
  type: jwt
  roles:
  - Administrator
  - Librarian
  - Reader
  - Auditor
database:
  type: mysql
  tables:
  - name: book_catalog
    purpose: Persistence for book-catalog-management
  - name: book_copy
    purpose: Persistence for book-catalog-management
  - name: reader_profile
    purpose: Persistence for reader-membership-management
  - name: reader_membership
    purpose: Persistence for reader-membership-management
  - name: borrow_order
    purpose: Persistence for circulation-borrow-management
  - name: borrow_record
    purpose: Persistence for circulation-borrow-management
  - name: return_inspection
    purpose: Persistence for return-inspection-management
  - name: fine_assessment
    purpose: Persistence for return-inspection-management
  - name: book_reservation
    purpose: Persistence for reservation-queue-management
  - name: reservation_queue_entry
    purpose: Persistence for reservation-queue-management
  - name: book_acquisition
    purpose: Persistence for acquisition-supplier-management
  - name: supplier_profile
    purpose: Persistence for acquisition-supplier-management
  - name: shelf_location
    purpose: Persistence for shelf-inventory-management
  - name: inventory_check_record
    purpose: Persistence for shelf-inventory-management
  - name: library_notification
    purpose: Persistence for notification-management
  - name: notification_delivery_record
    purpose: Persistence for notification-management
  - name: library_statistic_snapshot
    purpose: Persistence for report-statistics-management
  - name: borrow_statistic_report
    purpose: Persistence for report-statistics-management
frontend:
  pages: []
business_rules:
- book copies must remain traceable to a catalog entry and physical inventory location
- borrowing and return workflows must preserve centralized JWT authorization boundaries
- reservation queue actions must not bypass reader eligibility and stock availability
  checks
- reporting and notification flows must stay modular and consume library business
  events through explicit business modules
- Build a complete modular-monolith Spring Boot library management backend covering
  book catalog center, reader membership center, circulation borrowing center, return
  inspection center, reservation queue center, acquisition supplier center, shelf
  inventory center, notification center, and statistics reporting center.
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
