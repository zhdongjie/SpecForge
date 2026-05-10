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
Read [references/portable-one-line-project-protocol.md](references/portable-one-line-project-protocol.md) when the user wants a one-sentence or one-document portable generation workflow that another Codex session can execute without prior chat context.
Read [references/zero-context-handoff-checklist.md](references/zero-context-handoff-checklist.md) when the user explicitly wants migration, handoff, portability, or a copy-paste starter prompt for a fresh Codex session.
Read [references/requirement-template-contract.md](references/requirement-template-contract.md) when the user wants a reusable requirement template or a structured document contract for future generation runs.
Read [references/validated-domains-and-regression-suite.md](references/validated-domains-and-regression-suite.md) when the user asks whether the tool itself is stable, wants a new-machine shakeout, or wants a repeatable validation command.
Read [../../specforge-runtime/docs/FINAL_ONE_SHOT_PROTOCOL.md](../../specforge-runtime/docs/FINAL_ONE_SHOT_PROTOCOL.md) when the user wants the shortest end-to-end protocol for a new machine or fresh Codex session.

## Execution Mode

Operate as a deterministic project compiler driver.

Do not stop after planning.
Do not ask the user for step-by-step confirmation unless there is destructive risk or a genuine ambiguity with major downstream consequences.
Prefer making explicit assumptions, recording them in specs, and continuing.

The target outcome is one of:

- a bootable generated backend under `specforge-runtime/outputs/`
- or a reproducible failure bundle under `specforge-runtime/runs/<run-id>/logs/`

Treat these directory roles as fixed:

- `backend/` = assembly baseline
- `specforge-runtime/runs/<run-id>/` = execution trace for one attempt
- `specforge-runtime/outputs/<target>/` = final deliverable
- `sandbox/` = local scratch or migration rehearsal area

Treat one repository checkout as one mutable generation workspace.
Do not run multiple generation jobs in parallel against the same checkout.

Prefer automatic scaffold-domain selection first.
Use explicit `--domain` only when automatic matching is wrong or the user wants a forced domain.

## Phase Order

Follow this order strictly:

1. Inspect repository state and toolchain readiness.
2. Normalize the user requirement into project scope and assumptions.
3. Author or update project-level specs.
4. Author or update module-level specs for all enabled modules.
5. Author or update `project-assembly-plan.yaml` and `build-plan.yaml`.
6. Run the canonical auto-build pipeline.
7. Inspect compile, boot, delivery, SQL asset, and auth surface reports.
8. If needed, repair specs or compiler inputs and rerun.
9. Stop only on full success or reproducible failure.

It is forbidden to claim completion before compile and boot verification.
It is also forbidden to claim completion when business-domain modules fail route or permission contract validation.
It is also forbidden to claim completion when SQL asset validation or auth surface validation fails.

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
- whether the user expects an MVP or a complete business platform

If the user asks for a full platform, do not stop at a thin CRUD skeleton.
Infer a business-center level project shape and carry user/role/menu linkage plus database initialization SQL organization as project-level deliverable expectations.

If the user wants a workflow that can be repeated on another machine or by another Codex instance, optimize for:

- zero reliance on prior conversation state
- explicit scaffold command plus explicit auto-build command
- final artifact only under `specforge-runtime/outputs/`
- reproducible failure bundle under `specforge-runtime/runs/<run-id>/logs/`

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

Preferred one-command wrapper for portable execution:

```powershell
python scripts/run_requirement_project.py --repo-root <repo-root> --project-name "<project-name>" --requirement "<short requirement>" --run-id <run-id> --force
```

Preferred one-command wrapper for requirement-file execution:

```powershell
python scripts/run_requirement_project.py --repo-root <repo-root> --project-name "<project-name>" --requirement-file "<requirement-file>" --run-id <run-id> --force
```

This scaffold step should:

- write project-level specs
- write project assembly plan
- preserve the current proven enabled module where available
- create the full validated module set required by the project assembly plan

When the requirement is only one sentence, still author a complete first-pass project scope rather than asking the user to expand it manually unless the domain is genuinely ambiguous.

## Module Planning Rules

When the system is broader than a single business area, split modules by capabilities.

Good examples:

- resource management
- reservation management
- approval management
- notification management
- access management

For complete industry platforms, prefer business centers such as:

- product center
- customer center
- policy or order center
- approval center
- claim center
- payment center
- renewal center
- channel or agent center
- notification center
- statistics or reporting center

Do not collapse a clearly multi-module platform into one oversized module just to make generation easier.
Do not call the result "complete" if it only covers a subset of the expected business centers for that domain.

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
- `outputs/<target>/logs/api-smoke/business-contract-validation.yaml` for business route and permission coverage
- `outputs/<target>/logs/delivery-validation.yaml` for module coverage and full-platform contract coverage
- `outputs/<target>/logs/sql-asset-validation.yaml` for generated SQL asset completeness
- `outputs/<target>/logs/auth-surface-validation.yaml` for login/auth route readiness
- `outputs/<target>/logs/demo-access.yaml` for deterministic demo credentials and login endpoint
- `outputs/<target>/logs/api-smoke/postman-environment.json` for frontend or Postman handoff
- `outputs/<target>/src/main/resources/sql/demo-password-reset.sql` for reproducible demo account reset

Prefer unique run ids for every iteration so replay and failure analysis remain reproducible.
Prefer separate repository copies if you need parallel domain generation on the same machine.

When the user asks to validate the tool itself instead of generating a single business project, prefer:

```powershell
python scripts/run_tool_validation_suite.py --repo-root <repo-root> --force
```

When the user wants a copy-paste prompt for another Codex session, prefer:

```powershell
python scripts/emit_codex_handoff_prompt.py --project-name "<project-name>" --requirement "<one-line requirement>" --mode inline
```

When reporting success, point the user first to:

- `specforge-runtime/outputs/<target>/`

When reporting failure, point the user first to:

- `specforge-runtime/runs/<run-id>/logs/auto-build-report.yaml`

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
- business contract validation under `specforge-runtime/outputs/<target>/logs/api-smoke/business-contract-validation.yaml` shows `status: PASS`
- delivery validation under `specforge-runtime/outputs/<target>/logs/delivery-validation.yaml` shows `status: PASS`
- SQL asset validation under `specforge-runtime/outputs/<target>/logs/sql-asset-validation.yaml` shows `status: PASS`
- auth surface validation under `specforge-runtime/outputs/<target>/logs/auth-surface-validation.yaml` shows `status: PASS`

If the user asked for a complete platform, completion also requires that the authored project spec and assembly plan cover the expected business-center surfaces, along with user/role/menu linkage and initialization SQL organization at the project level.

If that is not achieved, return the failure bundle path and the blocking cause.
