# SpecForge Project Compiler Protocol

This document defines the canonical project-level flow for deterministic backend generation.

## Compiler Chain

```text
project-spec
  -> module-spec
  -> module-schema.resolved
  -> field-schema.generated/resolved
  -> platform synthesis
  -> module synthesis
  -> backend assembly
  -> compile verification
  -> boot verification
  -> final exported backend
```

## Operating Principles

- Determinism over creativity
- Business-domain modules must compile under `business/*`
- Platform and administrative infrastructure may remain under `core/*` and `system/*`
- Final deliverables must export into `specforge-runtime/outputs/`
- Build plans are the canonical execution interface

## Current Stable Invariant

For any module with:

- `semantic_role: business-domain`

the compiler must preserve:

- package root under `org.eu.originalkeen.business.*`
- route root under `/v1/business/*`
- authority root under `business:*`

## Canonical Inputs

- `specforge-runtime/specs/project-spec.md`
- `specforge-runtime/specs/module-spec.yaml`
- `specforge-runtime/specs/module-schema.resolved.yaml`
- `specforge-runtime/specs/build-plan.yaml`
- optional project-level plan:
  - `specforge-runtime/specs/project-assembly-plan.yaml`

## Canonical Execution Modes

### 1. Compiler component validation

Use this when validating a specific layer.

- IR lowering
- module synthesis
- project compilation
- hardening

### 2. End-to-end backend generation

Use this for reproducible system delivery.

```powershell
python main.py --auto-build --build-plan build-plan.yaml --run-id <run-id>
```

## Final Output Rule

The only stable exported backend is:

- `specforge-runtime/outputs/<target>/`

Everything inside:

- `specforge-runtime/runs/`

is execution state, trace data, or intermediate output.

## Full-System Growth Strategy

SpecForge has already proven:

- single business-module generation
- compile pass
- boot pass
- deterministic repair loop

The next system-scale workflow should remain:

1. define project assembly plan
2. declare module boundaries
3. order modules by dependency
4. compile platform once
5. synthesize bounded business modules
6. assemble one bootable backend
7. harden until pass or emit failure bundle

## Migration Discipline

- Never rely on local drive-specific paths
- Never treat temporary run folders as the product
- Always preserve run logs for replay and failure comparison
- Keep specs, runtime, and template backend in a single versioned commit when sharing
