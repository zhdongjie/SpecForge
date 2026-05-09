project:
  name: Insurance Operations Platform
  type: springboot-vue3
architecture:
  style: modular-monolith
  description: A modular-monolith Spring Boot backend compiled from SpecForge project
    and module specifications.
modules:
- name: insurance-customer-management
  responsibility: insured customer profile and beneficiary lifecycle management
  boundaries: Owns InsuranceCustomer, CustomerBeneficiary within insurance-customer-center.
  apis:
  - insurance-customer-management administration
  entities:
  - InsuranceCustomer
  - CustomerBeneficiary
- name: insurance-claim-management
  responsibility: claim submission, settlement, and tracking management
  boundaries: Owns InsuranceClaim, ClaimSettlement within insurance-claim-operations.
  apis:
  - insurance-claim-management administration
  entities:
  - InsuranceClaim
  - ClaimSettlement
- name: premium-payment-management
  responsibility: premium collection and refund processing management
  boundaries: Owns PremiumPayment, PaymentRefund within premium-payment-center.
  apis:
  - premium-payment-management administration
  entities:
  - PremiumPayment
  - PaymentRefund
- name: policy-renewal-management
  responsibility: policy renewal cycle and reminder management
  boundaries: Owns PolicyRenewal, RenewalReminder within policy-renewal-center.
  apis:
  - policy-renewal-management administration
  entities:
  - PolicyRenewal
  - RenewalReminder
- name: underwriting-approval-management
  responsibility: underwriting review decision and approval governance management
  boundaries: Owns UnderwritingApproval, UnderwritingDecisionRecord within underwriting-governance.
  apis:
  - underwriting-approval-management administration
  entities:
  - UnderwritingApproval
  - UnderwritingDecisionRecord
- name: channel-agent-management
  responsibility: sales channel and agent relationship management
  boundaries: Owns InsuranceChannel, InsuranceAgent within channel-agent-center.
  apis:
  - channel-agent-management administration
  entities:
  - InsuranceChannel
  - InsuranceAgent
features:
- Support Insurance Customer Management workflows.
- Support Insurance Claim Management workflows.
- Support Premium Payment Management workflows.
- Support Policy Renewal Management workflows.
- Support Underwriting Approval Management workflows.
- Support Channel Agent Management workflows.
auth:
  type: jwt
  roles:
  - Administrator
  - Underwriter
  - ClaimsAdjuster
  - FinanceOperator
  - ChannelManager
database:
  type: mysql
  tables:
  - name: insurance_customer
    purpose: Persistence for insurance-customer-management
  - name: customer_beneficiary
    purpose: Persistence for insurance-customer-management
  - name: insurance_claim
    purpose: Persistence for insurance-claim-management
  - name: claim_settlement
    purpose: Persistence for insurance-claim-management
  - name: premium_payment
    purpose: Persistence for premium-payment-management
  - name: payment_refund
    purpose: Persistence for premium-payment-management
  - name: policy_renewal
    purpose: Persistence for policy-renewal-management
  - name: renewal_reminder
    purpose: Persistence for policy-renewal-management
  - name: underwriting_approval
    purpose: Persistence for underwriting-approval-management
  - name: underwriting_decision_record
    purpose: Persistence for underwriting-approval-management
  - name: insurance_channel
    purpose: Persistence for channel-agent-management
  - name: insurance_agent
    purpose: Persistence for channel-agent-management
frontend:
  pages: []
business_rules:
- claim requests must reference an existing insured customer record
- premium payment actions must remain behind centralized JWT authorization
- renewal and underwriting operations must preserve modular business boundaries
- Build a complete modular-monolith Spring Boot insurance operations backend covering
  insured customer management, claim management, premium payments, policy renewals,
  underwriting approvals, and channel agent management.
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
