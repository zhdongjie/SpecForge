> 历史归档：2026-05 旧版操作合同。新版入口见 [当前 README](../../README.md)。旧命令仅用于兼容调用。

> 历史记录：旧方案已于2026-10-28退役。下文中的旧路径、兼容承诺和命令仅反映当时状态，当前不可执行。

# SpecForge Workspace Layout

This file defines the repository-level directory contract.

## Directory Roles

- `backend/`
  - baseline backend template used as the compilation assembly target
  - not the final exported backend for generated projects

- `specforge-runtime/`
  - canonical compiler runtime source
  - all runtime-facing specs live under `specforge-runtime/specs/`
  - successful generated projects are exported to `specforge-runtime/outputs/`
  - temporary execution traces live under `specforge-runtime/runs/`

- `skills/`
  - Codex skills used to bootstrap, scaffold, and execute SpecForge flows

- `sandbox/`
  - local-only validation area
  - used for bundle bootstrap, cross-machine simulation, smoke tests, and failure reproduction
  - not part of the canonical source tree
  - ignored by git

## Human Shortcut

When operating the repo, treat the directories like this:

- "template input" = `backend/`
- "compiler source" = `specforge-runtime/`
- "this run's evidence" = `specforge-runtime/runs/<run-id>/`
- "final product" = `specforge-runtime/outputs/<project-backend>/`
- "scratchpad" = `sandbox/`

If you are only looking for the generated deliverable, skip everything else and open `specforge-runtime/outputs/`.

## Final Deliverable Rule

Treat only this location as the final generated backend:

- `specforge-runtime/outputs/<project-backend>/`

Do not treat these as final deliverables:

- `sandbox/...`
- `specforge-runtime/runs/<run-id>/generated-project/`

Those directories are temporary verification artifacts.

## Recommended Operator Flow

1. Update or scaffold specs under `specforge-runtime/specs/`
2. Run the canonical auto-build pipeline
3. Check:
   - `specforge-runtime/runs/<run-id>/logs/auto-build-report.yaml`
   - `specforge-runtime/outputs/<project-backend>/`
4. Handoff or commit only canonical source changes and intended exported outputs

## Cleanliness Rules

- Keep experimental bundles under `sandbox/`
- Keep reproducible failure evidence under `specforge-runtime/runs/`
- Keep handoff-ready generated backends under `specforge-runtime/outputs/`
- Do not scatter generated artifacts into the repository root
- Do not treat `backend/` and `outputs/` as duplicates:
  - `backend/` is the stable assembly baseline
  - `outputs/` is the compiled result
