# Codex Chrome Test Loop

This document defines the browser-testing loop for SpecForge when you want Codex to:

- generate a backend from a one-line requirement
- open the generated app in a browser
- test core business flows
- feed failures back into the same generation loop
- repeat until the system is usable or a reproducible failure report is produced

## When To Use

Use this loop when the goal is not only compile and boot success, but also:

- real browser reachability
- login and authorization checks
- menu and page navigation
- list/create/edit/delete flow checks
- form validation checks
- error handling checks

## Recommended Division Of Labor

### Phase 1: Requirement To Backend

Ask Codex to:

- read the repository
- generate or load the requirement document
- run the SpecForge build pipeline
- stop only when compile and boot pass
- export the final backend into `specforge-runtime/outputs/`

### Phase 2: Browser Verification

Open the generated backend with Codex for Chrome and ask it to:

- log in with the expected test account
- verify menu entry points
- open each target page
- exercise one representative CRUD flow per module
- verify validation and error messages
- capture any broken page, network error, or missing permission

### Phase 3: Failure Feedback

When a browser issue appears, send Codex:

- the page name
- the visible failure
- the browser screenshot or console output
- the related `specforge-runtime/runs/<run-id>/` logs if available

Codex should then:

- update the requirement/spec if the problem is semantic
- repair the generated backend if the problem is structural
- rerun compile and boot
- repeat the browser test

## Loop Contract

The loop is successful only if all of the following pass:

- project compiles
- Spring Boot starts
- browser pages load
- core CRUD flows work
- permission checks behave correctly
- validation messages are correct

If the loop cannot converge, preserve a reproducible failure bundle:

- `specforge-runtime/runs/<run-id>/logs/auto-build-report.yaml`
- `specforge-runtime/runs/<run-id>/generated-project/logs/project-health-report.yaml`
- `specforge-runtime/runs/<run-id>/generated-project/logs/compile-diagnostics.yaml`
- `specforge-runtime/runs/<run-id>/generated-project/logs/boot-diagnostics.yaml`

## Suggested Browser Prompt

Use this prompt in Codex for Chrome:

> Open the generated backend, verify the main flows in the browser, and report only concrete failures. If a page fails, tell me the exact page, action, and symptom, then let Codex repair the backend and rerun until the browser flow passes or a reproducible failure bundle is produced.

## Suggested Continuation Prompt

When the browser finds a failure, continue with:

> Use the failure evidence to repair the generated backend, rerun compile and boot, then re-test the same browser flow. Do not ask me for step-by-step approval unless the problem requires a new business decision.

## Stable Output Rule

For this loop, treat these as the only important deliverables:

- `specforge-runtime/outputs/<project-backend>/`
- browser evidence from Codex for Chrome
- reproducible failure logs under `specforge-runtime/runs/<run-id>/`

