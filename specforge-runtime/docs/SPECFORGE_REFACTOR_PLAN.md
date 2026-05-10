# SpecForge Refactor Plan

## Goal

Evolve SpecForge from:

- deterministic backend generator

into:

- deterministic graduation-project backend compiler
- reproducible cross-machine delivery workflow
- fail-fast generation platform with explicit delivery gates

## Phase Order

1. Delivery gate unification
2. Full-platform coverage enforcement
3. Cross-environment portability hardening
4. Higher-order runtime verification and smoke assets

## Phase 1: Delivery Gate Unification

### Objective

Unify final success judgment into one machine-readable delivery verdict.

### Why

Current reports already cover:

- compile
- boot
- business route and permission contract

But the final success contract is still spread across multiple files.
That makes it too easy for a future Codex run to report success too early.

### Deliverables

- delivery validation script
- delivery validation report
- auto-build integration
- README and skill contract updates

### Success Criteria

Success is reported only if:

- auto-build report says `compile_status: PASS`
- auto-build report says `boot_status: PASS`
- business contract validation says `status: PASS`
- expected enabled business modules from `project-assembly-plan.yaml` are all present in the final backend

## Phase 2: Full-Platform Coverage Enforcement

### Objective

Prevent thin or incomplete business-center outputs when the request clearly asks for a complete platform.

### Deliverables

- assembly-plan coverage validator
- expected module family checks by supported domain
- missing-center diagnostics in failure bundle

### Target Domains

- laboratory-management
- laboratory-reservation
- insurance-management

### Success Criteria

Platform generation is considered complete only if required business centers are present for the inferred domain.

## Phase 3: Cross-Environment Portability Hardening

### Objective

Ensure a fresh Codex environment can bootstrap, run, validate, and diagnose the pipeline without prior thread context.

### Deliverables

- migration runbook refinement
- one-command bootstrap and cleanup alignment
- validation suite documentation refresh
- explicit final-output and failure-bundle contract

### Success Criteria

A new machine can:

- load the repository
- run readiness check
- scaffold from one sentence
- auto-build
- validate delivery
- locate final backend and failure reports without chat context

## Phase 4: Higher-Order Verification

### Objective

Raise success criteria from “boots successfully” toward “demonstrably usable backend”.

### Candidate Deliverables

- SQL initialization verification
- default-login smoke verification
- OpenAPI or route-export completeness checks
- menu and permission linkage verification
- packaged Postman smoke assets

### Success Criteria

Generated backends are not only bootable, but also fast to verify in demo and migration environments.

## Working Rule

Each phase must end with:

- code changes
- docs updates where needed
- a deterministic verification path

Do not introduce a new success claim without also introducing a machine-checkable report.
