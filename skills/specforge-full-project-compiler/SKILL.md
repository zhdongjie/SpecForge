---
name: specforge-full-project-compiler
description: Compile a complete Spring Boot backend project from a short project name, a one-paragraph requirement, or a structured requirements document using the local SpecForge compiler pipeline. Use when Codex must autonomously turn minimal business requirements into project specs, module specs, assembly plans, generated backend code, compile/boot verification, and a final exported project with reproducible failure reports if generation does not succeed.
---

# SpecForge Full Project Compiler

Use this skill when the user wants full-project autonomous generation, not a single module tweak.

Read [references/pipeline-contract.md](references/pipeline-contract.md) before running the pipeline.
Read [references/spec-authoring-contract.md](references/spec-authoring-contract.md) before writing or changing any specs.
Read [references/default-project-inference.md](references/default-project-inference.md) when the user input is short or ambiguous.
Read [references/failure-bundle-contract.md](references/failure-bundle-contract.md) before reporting failure.
Read [references/starter-bundle-contract.md](references/starter-bundle-contract.md) when the workspace may need bootstrap or cross-machine handoff.
Read [references/module-blueprints.yaml](references/module-blueprints.yaml) when scaffolding a first-pass project from minimal requirements.

## Execution Mode

Operate as a deterministic project compiler driver.

Do not stop after planning.
Do not ask the user for step-by-step confirmation unless there is destructive risk or a genuine ambiguity with major downstream consequences.
Prefer making explicit assumptions, recording them in specs, and continuing.

The target outcome is one of:

- a bootable generated backend under `specforge-runtime/outputs/`
- or a reproducible failure bundle under `specforge-runtime/runs/<run-id>/logs/`

## Phase Order

Follow this order strictly:

1. Inspect repository state and toolchain readiness.
2. Normalize the user requirement into project scope and assumptions.
3. Author or update project-level specs.
4. Author or update module-level specs for all enabled modules.
5. Author or update `project-assembly-plan.yaml` and `build-plan.yaml`.
6. Run the canonical auto-build pipeline.
7. Inspect compile and boot reports.
8. If needed, repair specs or compiler inputs and rerun.
9. Stop only on full success or reproducible failure.

It is forbidden to claim completion before compile and boot verification.

## Repository Checks

Verify these paths first:

- `specforge-runtime/main.py`
- `specforge-runtime/specs/`
- `specforge-runtime/runtime/`

Prefer a baseline backend template at:

- `backend/`

If `specforge-runtime/` is missing, bootstrap the workspace from a known source bundle before continuing.

Preferred bootstrap command:

```powershell
python scripts/bootstrap_specforge_bundle.py --source-repo <source-repo> --target-workspace <target-workspace> --include-skill
```

If toolchain paths are unresolved, rely on the runtime toolchain discovery rules already implemented in `specforge-runtime/runtime/toolchain.py`.

Prefer running this readiness check first:

```powershell
python scripts/check_specforge_workspace.py --repo-root <repo-root>
```

Do not attempt full-project synthesis in an unbootstrapped empty workspace.

## Requirement Normalization

Accept any of these inputs:

- one project name
- one sentence of business scope
- a markdown or text requirements document
- an existing spec draft

If the input is short, infer:

- primary actors
- core business flows
- CRUD resources
- approval or workflow requirements
- notification needs
- access-control expectations
- modular split

Use pragmatic graduation-project defaults.
Do not wait for the user to provide exhaustive detail before authoring a first pass.

## Spec Authoring Workflow

Write or update these files in `specforge-runtime/specs/`:

- `project-spec.md`
- `project-assembly-plan.yaml`
- `build-plan.yaml`

For each enabled module, write or update:

- `module-spec.yaml`
- `module-schema.resolved.yaml`

If multiple modules are needed, store future-ready specs in:

- `specforge-runtime/specs/templates/<module-name>/`

Use these defaults:

- architecture: `modular-monolith`
- auth: centralized JWT
- output target: one bootable Spring Boot backend
- business modules under `org.eu.originalkeen.business.*`

When the requirement is very short, use the inference policy from [references/default-project-inference.md](references/default-project-inference.md).

Preferred first-pass scaffold command:

```powershell
python scripts/scaffold_requirement_project.py --repo-root <repo-root> --project-name "<project-name>" --requirement "<short requirement>"
```

This scaffold step should:

- write project-level specs
- write project assembly plan
- preserve the current proven enabled module where available
- create the full validated module set required by the project assembly plan

## Module Planning Rules

When the system is broader than a single business area, split modules by capabilities.

Good examples:

- resource management
- reservation management
- approval management
- notification management
- access management

Do not collapse a clearly multi-module platform into one oversized module just to make generation easier.

Do not enable speculative modules unless their specs are concrete enough to synthesize safely.

## Build Execution

Use the canonical auto-build command from `specforge-runtime/`.

Preferred wrapper:

```powershell
python ../skills/specforge-full-project-compiler/scripts/run_specforge_autobuild.py --repo-root .. --run-id <run-id>
```

Equivalent direct runtime command:

```powershell
python main.py --auto-build --build-plan build-plan.yaml --run-id <run-id>
```

Always inspect:

- `runs/<run-id>/logs/auto-build-report.yaml`
- `runs/<run-id>/generated-project/logs/project-health-report.yaml`
- `runs/<run-id>/generated-project/logs/project-assembly-report.yaml` when project assembly is used

Prefer unique run ids for every iteration so replay and failure analysis remain reproducible.

## Repair Loop

If compile or boot fails:

1. Read diagnostics before changing anything.
2. Prefer fixing specs, assembly plans, or compiler inputs over ad hoc generated-code surgery.
3. Rerun the same build plan with a new run id.
4. Preserve each failed run's logs.

Do not silently abandon failed modules.
Follow [references/failure-bundle-contract.md](references/failure-bundle-contract.md) when the pipeline does not converge.

## Success Contract

A task is complete only if:

- final backend exists under `specforge-runtime/outputs/`
- auto-build report shows `compile_status: PASS`
- auto-build report shows `boot_status: PASS`

If that is not achieved, return the failure bundle path and the blocking cause.
