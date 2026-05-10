# Tool Validation Status

This document records validation status for the SpecForge generation tool itself.

It is not a business demo document.
It is a toolchain verification snapshot.

## Current Verified Paths

### Verified path A: canonical scaffold + auto-build

Validated result:

- canonical specs authored under `specforge-runtime/specs/`
- multi-module project assembly succeeded
- compile passed
- boot passed
- business contract validation passed
- delivery validation passed
- SQL asset validation passed
- auth surface validation passed
- final backend exported under `specforge-runtime/outputs/`

### Verified path B: one-command requirement wrapper on laboratory domain

Validated command:

```powershell
python skills/specforge-full-project-compiler/scripts/run_requirement_project.py --repo-root . --project-name "Laboratory Management Platform" --requirement "Build a complete modular-monolith Spring Boot laboratory management backend covering laboratory resources, experiment projects, equipment, consumables, reservations, approvals, access control, notifications, schedule calendar, and statistics reporting." --run-id lab-tool-verify-001 --force
```

Validated behavior:

1. workspace readiness check executed
2. scaffold step executed
3. canonical auto-build executed
4. compile passed
5. boot passed
6. final output preserved under `specforge-runtime/outputs/`

Associated run:

- `specforge-runtime/runs/lab-tool-verify-001/`

Associated final output:

- `specforge-runtime/outputs/laboratory-management-platform-backend/`

### Verified path C: one-command requirement wrapper on insurance domain

Validated command:

```powershell
python skills/specforge-full-project-compiler/scripts/run_requirement_project.py --repo-root . --project-name "Insurance Operations Platform" --requirement "Build a complete modular-monolith Spring Boot insurance operations backend covering product center, customer center, policy center, claim center, premium payment center, renewal center, underwriting center, channel agent center, notification center, and statistics reporting center." --domain insurance-management --run-id insurance-tool-verify-001 --force
```

Validated behavior:

1. workspace readiness check executed
2. scaffold step executed
3. canonical auto-build executed
4. compile passed
5. boot passed
6. delivery validation passed
7. final output preserved under `specforge-runtime/outputs/`

Associated run:

- `specforge-runtime/runs/insurance-tool-verify-001/`

Associated final output:

- `specforge-runtime/outputs/insurance-operations-platform-backend/`

### Verified path D: requirement-file input plus automatic domain selection

Validated command:

```powershell
python skills/specforge-full-project-compiler/scripts/run_requirement_project.py --repo-root . --project-name "Insurance Operations Platform" --requirement-file sandbox/insurance-operations-requirement.txt --run-id insurance-tool-verify-002 --force
```

Validated behavior:

1. workspace readiness check executed
2. wrapper inferred `insurance-management` automatically from project name and requirement text
3. scaffold step executed without explicit `--domain`
4. canonical auto-build executed
5. compile passed
6. boot passed
7. delivery validation passed
8. SQL asset validation passed
9. auth surface validation passed
10. final output preserved under `specforge-runtime/outputs/`

### Verified path E: comprehensive laboratory platform scaffold plus automatic domain selection

Validated command:

```powershell
python skills/specforge-full-project-compiler/scripts/run_requirement_project.py --repo-root . --project-name "Laboratory Management Platform" --requirement-file sandbox/laboratory-management-requirement.txt --run-id lab-tool-verify-002 --force
```

Validated behavior:

1. workspace readiness check executed
2. wrapper inferred `laboratory-management` automatically from project name and requirement text
3. scaffold step assembled a broader laboratory platform blueprint
4. canonical auto-build executed
5. compile passed
6. boot passed
7. final output preserved under `specforge-runtime/outputs/`

### Verified path F: rerunnable validation suite after domain inference and output-export hardening

Validated behavior:

1. insurance inline requirement auto-selects `insurance-management`
2. laboratory inline requirement auto-selects `laboratory-management`
3. module assembly uses explicit template specs for all business modules
4. output export tolerates locked transient `.log` files on Windows
5. wrappers reject concurrent mutation of the same repository workspace through `specforge-runtime/.workspace.lock`
6. scenario-level summary now requires compile, boot, business, delivery, SQL, and auth statuses all equal `PASS`
7. boot verification now uses deterministic `max timeout + idle timeout` startup semantics instead of a fragile fixed 120-second window

### Verified path G: cold-start boot verification hardening

Validated behavior:

1. Spring Boot startup is allowed to complete under cold-cache and first-run conditions
2. boot checks use `-ntp` to reduce Maven transfer-noise during startup observation
3. boot verifier and hardening diagnostics now share the same deterministic startup-window model
4. the previously flaky `insurance-file-auto` scenario now passes inside the full serial validation suite

### Verified path H: third-domain portability validation on library management

Validated command:

```powershell
python skills/specforge-full-project-compiler/scripts/run_tool_validation_suite.py --repo-root . --scenario library-inline-auto --force
```

Validated behavior:

1. wrapper inferred `library-management` automatically from project name and requirement text
2. scaffold step assembled a complete library-platform blueprint
3. canonical auto-build executed without manual spec intervention
4. compile passed
5. boot passed
6. business contract validation passed
7. delivery validation passed
8. SQL asset validation passed
9. auth surface validation passed
10. final output preserved under `specforge-runtime/outputs/`

## Verified Success Evidence

From `lab-tool-verify-001`:

- `generated-project/logs/compile-diagnostics.yaml`
  - `status: PASS`
- `generated-project/logs/boot-diagnostics.yaml`
  - `status: PASS`
- `generated-project/logs/project-health-report.yaml`
  - `compile_status: PASS`
  - `boot_status: PASS`

From `insurance-tool-verify-001`:

- `generated-project/logs/compile-diagnostics.yaml`
  - `status: PASS`
- `generated-project/logs/boot-diagnostics.yaml`
  - `status: PASS`
- `generated-project/logs/project-health-report.yaml`
  - `compile_status: PASS`
  - `boot_status: PASS`
- `logs/auto-build-report.yaml`
  - `compile_status: PASS`
  - `boot_status: PASS`
- `outputs/insurance-operations-platform-backend/logs/delivery-validation.yaml`
  - `status: PASS`
- `outputs/insurance-operations-platform-backend/logs/sql-asset-validation.yaml`
  - `status: PASS`
- `outputs/insurance-operations-platform-backend/logs/auth-surface-validation.yaml`
  - `status: PASS`
  - `actual_business_module_count: 10`

From `insurance-tool-verify-002`:

- wrapper stdout
  - `[DOMAIN] insurance-management`
- `generated-project/logs/compile-diagnostics.yaml`
  - `status: PASS`
- `generated-project/logs/boot-diagnostics.yaml`
  - `status: PASS`
- `generated-project/logs/project-health-report.yaml`
  - `compile_status: PASS`
  - `boot_status: PASS`
- `logs/auto-build-report.yaml`
  - `compile_status: PASS`
  - `boot_status: PASS`
- `outputs/insurance-operations-platform-backend/logs/delivery-validation.yaml`
  - `status: PASS`

From `lab-tool-verify-002`:

- wrapper stdout
  - `[DOMAIN] laboratory-management`
- `generated-project/logs/compile-diagnostics.yaml`
  - `status: PASS`
- `generated-project/logs/boot-diagnostics.yaml`
  - `status: PASS`
- `generated-project/logs/project-health-report.yaml`
  - `compile_status: PASS`
  - `boot_status: PASS`
- `logs/auto-build-report.yaml`
  - `compile_status: PASS`
  - `boot_status: PASS`

From the rerunnable validation suite:

- command:
  - `python skills/specforge-full-project-compiler/scripts/run_tool_validation_suite.py --repo-root . --force`
- suite status:
  - `lab-inline-auto: PASS`
  - `lab-platform-file-auto: PASS`
  - `insurance-inline-auto: PASS`
  - `insurance-file-auto: PASS`
  - `library-inline-auto: PASS`
- rerun safety:
  - `--force` now resets the matching `specforge-runtime/runs/<run-id>/` directory before rebuilding
- workspace safety:
  - shared-workspace concurrent runs are now blocked by `specforge-runtime/.workspace.lock`
- Windows export safety:
  - locked transient `.log` files in prior outputs no longer fail final backend export
- cold-start boot safety:
  - first-run startup no longer fails only because the old fixed 120-second window elapsed

From `library-inline-auto`:

- wrapper stdout
  - `[DOMAIN] library-management`
- `generated-project/logs/compile-diagnostics.yaml`
  - `status: PASS`
- `generated-project/logs/boot-diagnostics.yaml`
  - `status: PASS`
- `generated-project/logs/project-health-report.yaml`
  - `compile_status: PASS`
  - `boot_status: PASS`
- `logs/auto-build-report.yaml`
  - `compile_status: PASS`
  - `boot_status: PASS`
- `outputs/library-management-platform-backend/logs/delivery-validation.yaml`
  - `status: PASS`
- `outputs/library-management-platform-backend/logs/sql-asset-validation.yaml`
  - `status: PASS`
- `outputs/library-management-platform-backend/logs/auth-surface-validation.yaml`
  - `status: PASS`

## What Is Now Considered Stable

- directory role contract
- canonical output location contract
- zero-context handoff documentation
- copy-paste Codex starter prompts
- one-line requirement workflow
- requirement-file workflow
- one-command wrapper execution path
- automatic supported-domain selection from requirement text
- compile and boot verification loop
- delivery validation loop
- SQL asset validation loop
- auth/login surface validation loop
- multi-domain scaffold validation for at least:
  - laboratory reservation
  - laboratory comprehensive management
  - insurance operations
- third-domain portability validation on library management
- rerunnable validation-suite execution with stable scenario commands
- Windows output export tolerance for locked transient log files
- shared-workspace mutation protection through a repository-local lock
- cold-start boot verification tolerance through deterministic total-timeout and idle-timeout startup checks

## What Is Not Yet Fully Closed

### 1. Domain blueprint coverage

The system still needs repeated verification on additional domains if the goal is:

- "any management platform can be generated with the same stability"

### 2. Zero-manual-repair breadth

The current verified runs succeeded without spec-side manual intervention during execution,
but broader domain coverage still requires more test samples before calling the whole toolchain universally stable.

## Current Practical Conclusion

The generated backend path is now closed for at least three independent domains:

- laboratory reservation
- laboratory comprehensive management
- insurance operations
- library management
- insurance operations complete-platform blueprint with:
  - product center
  - customer center
  - policy center
  - claim center
  - premium payment center
  - renewal center
  - underwriting center
  - channel agent center
  - notification center
  - statistics reporting center

The tool itself is now validated as:

- reproducible
- portable
- one-command runnable
- one-file-input runnable
- compile-and-boot verified
- SQL-delivery verified
- auth-surface verified
- multi-domain verified at the scaffold and assembly level
- capable of auto-selecting a supported scaffold blueprint from requirement semantics

for the currently verified laboratory reservation, laboratory comprehensive management, insurance, and library workflows.

## Recommended Next Validation Step

Do not deepen either demo as a business project.

Use a third domain to test the tool itself:

1. prepare a new requirement
2. run the same one-command wrapper
3. fix only the tool or scaffold layer if it fails
4. do not hand-edit generated business code as the primary fix path

## Automation Support

Portable regression entry:

```powershell
python skills/specforge-full-project-compiler/scripts/run_tool_validation_suite.py --repo-root . --force
```

Current built-in scenarios:

- `lab-inline-auto`
- `lab-platform-file-auto`
- `insurance-inline-auto`
- `insurance-file-auto`
- `library-inline-auto`
