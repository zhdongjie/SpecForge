# SpecForge Environment Migration Runbook

This runbook defines the portable execution contract for moving SpecForge to a new machine or handing it to another Codex session.

## Goals

- Reproduce backend generation on a clean machine
- Avoid local hardcoded JDK or Maven assumptions
- Preserve deterministic build, compile, and boot verification

## Required Layout

Clone or copy the repository so that this directory exists:

- `specforge-runtime/`

Canonical runtime entrypoint:

- `specforge-runtime/main.py`

Canonical final backend export location:

- `specforge-runtime/outputs/<plan-id-or-custom-output>/`

## Toolchain Discovery Contract

SpecForge now resolves Java and Maven in this order.

### Java

1. `SPECFORGE_JAVA_HOME`
2. `JAVA_HOME`
3. `java` available on `PATH`
4. common local install directories scanned on Windows

### Maven

1. `SPECFORGE_MAVEN_CMD`
2. `SPECFORGE_MAVEN_HOME`
3. `MAVEN_HOME`
4. `M2_HOME`
5. `mvn.cmd` or `mvn` on `PATH`
6. common local install directories scanned on Windows

## Recommended New-Machine Bootstrap

1. Install JDK 17.
2. Install Maven 3.9+.
3. Set environment variables:
   - `SPECFORGE_JAVA_HOME`
   - `SPECFORGE_MAVEN_CMD`
4. Verify commands:
   - `java -version`
   - `mvn -version`
5. Open the repo root:
   - `E:\Project\Generate\SpecForge`
6. Run from:
   - `E:\Project\Generate\SpecForge\specforge-runtime`

## Canonical Commands

IR lowering:

```powershell
python main.py --lower-ir --run-id lowering-smoke
```

Module synthesis:

```powershell
python main.py --synthesize-module --verify-compile --run-id synth-smoke
```

Backend compile and boot:

```powershell
python main.py --compile-backend --verify-boot --run-id backend-smoke
```

Deterministic hardening pipeline:

```powershell
python main.py --harden-backend --auto-repair --verify-boot --run-id hardening-smoke
```

Canonical end-to-end export:

```powershell
python main.py --auto-build --build-plan build-plan.yaml --run-id laboratory-reservation-final
```

## Output Contract

Successful end-to-end runs must produce:

- `runs/<run-id>/logs/auto-build-report.yaml`
- `outputs/<target>/logs/final-output-report.yaml`

The final backend for handoff or deployment review is always the exported backend under:

- `specforge-runtime/outputs/...`

Do not treat temporary generated directories inside `runs/` as final deliverables.

## Reproducibility Rules

- Use canonical specs from `specforge-runtime/specs/`.
- Keep runtime version and specs in the same commit when migrating.
- Always prefer `build-plan.yaml` driven runs over ad hoc command combinations.
- Treat any compile or boot failure as a reproducible artifact only if the matching logs in `runs/<run-id>/logs/` are preserved.

## Another Codex Handoff Contract

When another Codex session resumes this repository, it should:

1. Read `specforge-runtime/specs/README.md`.
2. Read `specforge-runtime/docs/PROJECT_COMPILER_PROTOCOL.md`.
3. Read `specforge-runtime/docs/ENVIRONMENT_MIGRATION_RUNBOOK.md`.
4. Use `specforge-runtime/specs/build-plan.yaml` as the canonical entry spec.
5. Export final deliverables only into `specforge-runtime/outputs/`.

## Failure Report Contract

If generation cannot succeed on the new machine, preserve:

- `compile-diagnostics.yaml`
- `compile-repair-report.yaml`
- `boot-diagnostics.yaml`
- `boot-repair-report.yaml`
- `project-health-report.yaml`
- `auto-build-report.yaml`

These files together are the minimum reproducible failure bundle.
