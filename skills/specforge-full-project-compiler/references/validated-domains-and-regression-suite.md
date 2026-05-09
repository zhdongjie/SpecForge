# Validated Domains And Regression Suite

Use this reference when the user asks:

- whether the tool itself is stable
- which domains are already proven
- how to validate the tool on a new machine
- how to run a repeatable regression suite

## Currently Validated Automatic Scaffold Domains

- `laboratory-reservation`
- `laboratory-management`
- `insurance-management`

## Proven Input Shapes

- inline one-line requirement
- requirement document file
- explicit domain override
- automatic domain selection from project name plus requirement text

## Proven Success Standard

Treat a run as successful only if:

- `compile_status: PASS`
- `boot_status: PASS`
- final backend exists under `specforge-runtime/outputs/`

## Regression Entry

Run the portable regression suite with:

```powershell
python skills/specforge-full-project-compiler/scripts/run_tool_validation_suite.py --repo-root . --force
```

Run a single scenario with:

```powershell
python skills/specforge-full-project-compiler/scripts/run_tool_validation_suite.py --repo-root . --scenario <scenario-name> --force
```

Use `--force` to allow safe reruns of the same validation scenario and reset the matching `specforge-runtime/runs/<run-id>/` workspace before rebuilding.

## Current Built-In Scenarios

- `lab-inline-auto`
- `lab-platform-file-auto`
- `insurance-inline-auto`
- `insurance-file-auto`

## Purpose Of The Regression Suite

Use the suite to validate:

- workspace readiness
- requirement normalization
- automatic domain selection
- scaffold generation
- canonical auto-build execution
- compile viability
- boot viability

## Recommended New-Machine Validation Order

1. Run `check_specforge_workspace.py`
2. Run `run_tool_validation_suite.py --scenario insurance-file-auto --force`
3. Run `run_tool_validation_suite.py --scenario lab-platform-file-auto --force`
4. Accept the environment as ready only after both compile and boot pass

## Final Deliverable Rule

Always treat:

- `specforge-runtime/outputs/<target>/`

as the product.

Treat:

- `specforge-runtime/runs/<run-id>/`

as execution evidence only.
