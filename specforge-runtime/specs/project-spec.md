project:
  name: Insurance Management Platform
  type: springboot-vue3

architecture:
  style: modular-monolith
  description: A single Spring Boot backend organized around insurance product and policy administration, claim administration, underwriting approval, notification delivery, centralized JWT security, unified responses, and cross-cutting audit infrastructure.

modules:
  - name: insurance-policy-management
    responsibility: Manages insurance products and customer policies, including product maintenance, policy issuance records, and policy query workflows.
    boundaries: Owns insurance product master data and policy master records within the policy domain, but does not own claim adjudication or notification dispatch state.
    apis:
      - Insurance product administration
      - Insurance policy administration
      - Insurance product page query
      - Insurance policy page query
      - Insurance product and policy detail query
      - Insurance product and policy list lookup
    entities:
      - InsuranceProduct
      - InsurancePolicy
  - name: insurance-claim-management
    responsibility: Manages claim intake and claim settlement records for insurance business workflows.
    boundaries: Owns claim records and claim settlement tracking, but does not own policy issuance or centralized security infrastructure.
    apis:
      - Insurance claim administration
      - Insurance claim page query
      - Insurance claim detail query
      - Insurance claim list lookup
    entities:
      - InsuranceClaim
      - ClaimSettlement
  - name: underwriting-approval-management
    responsibility: Manages underwriting approval decisions and approval record trails for insurance applications.
    boundaries: Owns underwriting decisions and approval records, but does not own policy issuance persistence or notification dispatch.
    apis:
      - Underwriting approval administration
      - Underwriting approval page query
      - Underwriting approval detail query
      - Underwriting approval list lookup
    entities:
      - UnderwritingApproval
      - UnderwritingDecisionRecord
  - name: notification-management
    responsibility: Manages insurance notification messages and notification delivery records across policy, claim, and approval workflows.
    boundaries: Owns notification message and delivery persistence, but does not own claim or policy business decisions.
    apis:
      - Notification administration
      - Notification page query
      - Notification detail query
      - Notification list lookup
    entities:
      - NotificationMessage
      - NotificationDispatchRecord
  - name: insurance-customer-management
    responsibility: Manages insurance customers and beneficiary records for policy enrollment and service workflows.
    boundaries: Owns customer master data and beneficiary relationships, but does not own policy issuance or claim adjudication.
    apis:
      - Insurance customer administration
      - Customer page query
      - Customer detail query
      - Customer list lookup
    entities:
      - InsuranceCustomer
      - CustomerBeneficiary
  - name: premium-payment-management
    responsibility: Manages premium payments and refund records across insurance billing workflows.
    boundaries: Owns payment and refund persistence, but does not own policy issuance decisions or centralized notification infrastructure.
    apis:
      - Premium payment administration
      - Premium payment page query
      - Premium payment detail query
      - Premium payment list lookup
    entities:
      - PremiumPayment
      - PaymentRefund
  - name: policy-renewal-management
    responsibility: Manages policy renewal records and renewal reminder workflows.
    boundaries: Owns renewal records and reminder persistence, but does not own premium collection infrastructure.
    apis:
      - Policy renewal administration
      - Policy renewal page query
      - Policy renewal detail query
      - Policy renewal list lookup
    entities:
      - PolicyRenewal
      - RenewalReminder
  - name: channel-agent-management
    responsibility: Manages insurance sales channels and insurance agent records.
    boundaries: Owns channel and agent master data, but does not own policy issuance or claim settlement workflows.
    apis:
      - Channel administration
      - Agent administration
      - Channel and agent page query
      - Channel and agent detail query
    entities:
      - InsuranceChannel
      - InsuranceAgent
  - name: report-statistics-management
    responsibility: Manages report tasks and dashboard snapshot records for insurance operations oversight.
    boundaries: Owns reporting task definitions and snapshot persistence, but does not own source transaction systems.
    apis:
      - Report task administration
      - Report statistics page query
      - Report statistics detail query
      - Dashboard snapshot lookup
    entities:
      - ReportTask
      - DashboardSnapshot

features:
  - Administer insurance products through create, update, batch delete, page query, detail query, and list query workflows.
  - Administer insurance policies through create, update, batch delete, page query, detail query, and list query workflows.
  - Administer insurance claims through create, update, batch delete, page query, detail query, and list query workflows.
  - Administer underwriting approvals through create, update, batch delete, page query, detail query, and list query workflows.
  - Administer insurance notifications through create, update, batch delete, page query, detail query, and list query workflows.
  - Administer insurance customers through create, update, batch delete, page query, detail query, and list query workflows.
  - Administer premium payments through create, update, batch delete, page query, detail query, and list query workflows.
  - Administer policy renewals through create, update, batch delete, page query, detail query, and list query workflows.
  - Administer channels and agents through create, update, batch delete, page query, detail query, and list query workflows.
  - Administer report tasks and dashboard snapshots through create, update, batch delete, page query, detail query, and list query workflows.
  - Enforce insurance product code uniqueness.
  - Enforce insurance product name uniqueness.
  - Enforce insurance policy number uniqueness.
  - Require all non-public APIs to remain behind centralized JWT-based authorization.
  - Record administrative mutation trails for policy, claim, approval, and notification operations.

auth:
  type: jwt
  roles:
    - Admin
    - Underwriter
    - ClaimAdjuster
    - CustomerService

database:
  type: mysql
  tables:
    - name: insurance_product
      purpose: Stores insurance product master data.
    - name: insurance_policy
      purpose: Stores insurance policy master records linked to products.
    - name: insurance_claim
      purpose: Stores claim intake and processing records.
    - name: claim_settlement
      purpose: Stores claim settlement detail records.
    - name: underwriting_approval
      purpose: Stores underwriting approval decisions.
    - name: underwriting_decision_record
      purpose: Stores underwriting decision audit records.
    - name: notification_message
      purpose: Stores outbound insurance notification messages.
    - name: notification_dispatch_record
      purpose: Stores notification dispatch trace records.
    - name: insurance_customer
      purpose: Stores insurance customer master data.
    - name: customer_beneficiary
      purpose: Stores customer beneficiary records.
    - name: premium_payment
      purpose: Stores premium payment records.
    - name: payment_refund
      purpose: Stores premium refund records.
    - name: policy_renewal
      purpose: Stores policy renewal records.
    - name: renewal_reminder
      purpose: Stores renewal reminder records.
    - name: insurance_channel
      purpose: Stores insurance channel master data.
    - name: insurance_agent
      purpose: Stores insurance agent master data.
    - name: report_task
      purpose: Stores report task definitions.
    - name: dashboard_snapshot
      purpose: Stores dashboard snapshot records.

frontend:
  pages: []

business_rules:
  - Only authenticated users may access insurance administration endpoints.
  - Insurance product codes and product names must remain unique.
  - Insurance policy numbers must remain unique.
  - Insurance policy records must reference an existing insurance product.
  - Administrative mutation endpoints must remain protected by centralized authority-based method security.
  - Notifications should remain a bounded business module and not be embedded into controllers of policy, claim, or approval modules.
  - Customer and agent master data should remain independently maintainable business modules.
  - Payment, renewal, and reporting workflows should remain bounded business modules rather than being embedded into policy controllers.

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
  - Rebuild the system as a single deployable backend with distinct policy, claim, approval, notification, customer, payment, renewal, channel, and reporting module boundaries.
  - Preserve authority-based centralized authorization and JWT-backed stateless API access.
  - Preserve administrative CRUD consistency across all insurance business aggregates.
  - Preserve policy-to-product referential integrity.
  - Preserve notification management as a separate business module rather than embedding messaging logic into other controllers.
  - Preserve audit logging as shared cross-cutting infrastructure rather than embedding logging logic into controllers.
