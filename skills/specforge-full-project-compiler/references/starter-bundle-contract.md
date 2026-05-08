# Starter Bundle Contract

This skill is strongest when paired with a portable SpecForge starter bundle.

## Bundle Goal

Make a fresh workspace runnable with minimal manual setup:

- install Codex
- install the skill
- prepare a workspace containing the SpecForge compiler runtime
- provide a baseline backend template
- run one command to compile a full backend from requirements

## Required Bundle Contents

A ready-to-run workspace should contain:

- `specforge-runtime/`
- `backend/`
- optional `skills/specforge-full-project-compiler/`

## Bootstrap Strategy

If a fresh workspace does not already contain the runtime, initialize it by copying:

- `specforge-runtime/`
- `backend/`

from a known source bundle.

Do not attempt full-project generation in an empty workspace without these compiler assets.

## Portable Handoff Rule

For cross-machine handoff, version and transport these together:

- the runtime
- the backend baseline
- the skill
- the current specs

This is the minimum reproducible generation bundle.

## New Environment Success Criteria

A new environment is considered ready only if:

- workspace readiness check returns `ready: true`
- toolchain resolves
- canonical auto-build command executes
