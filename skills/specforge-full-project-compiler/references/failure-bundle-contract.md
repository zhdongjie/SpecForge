# Failure Bundle Contract

When the pipeline cannot reach a bootable backend, produce a reproducible failure bundle instead of a vague summary.

## Required Files

Preserve:

- `specforge-runtime/runs/<run-id>/logs/auto-build-report.yaml`
- `specforge-runtime/runs/<run-id>/generated-project/logs/compile-diagnostics.yaml`
- `specforge-runtime/runs/<run-id>/generated-project/logs/compile-repair-report.yaml`
- `specforge-runtime/runs/<run-id>/generated-project/logs/boot-diagnostics.yaml`
- `specforge-runtime/runs/<run-id>/generated-project/logs/boot-repair-report.yaml`
- `specforge-runtime/runs/<run-id>/generated-project/logs/project-health-report.yaml`

If project assembly was used, also preserve:

- `project-assembly-report.yaml`
- per-module `merge-report.yaml`
- per-module `module-assembly-report.yaml`

## Reporting Rules

The final response should state:

- the run id
- the exact blocking phase
- whether compile failed or boot failed
- whether the failure came from:
  - spec authoring
  - project assembly
  - compiler generation
  - baseline backend conflict
  - external toolchain/environment

## Retry Rules

- keep the failed run directory
- rerun with a new run id
- never overwrite the prior failure evidence
