# SpecForge core v1

The independent core lives in `specforge/`. The historical runtime and skill entrypoints remain unchanged.

## Installation and toolchain

Use WSL/Linux, Python 3.10+, JDK 17 and Maven 3.9+, and the template-pinned Node/pnpm versions. Put each on PATH. The core requires PyYAML; `pip install -e .` installs the CLI. `pip install -e ".[acceptance]"` installs optional Python Playwright; then run `python -m playwright install chromium` and install browser OS dependencies if required.

Run from the SpecForge repository:

```bash
python -m unittest discover -s tests_core -v
python -m specforge validate --workspace /absolute/workspace/device-borrow --spec examples/device_borrow.yaml
python -m specforge run --workspace /absolute/workspace/device-borrow --spec examples/device_borrow.yaml --template /absolute/path/to/admin-platform --acceptance-pack device-borrow
```

The workspace must be outside the template and dedicated to one project ID. Repeated generation creates a new run, preserving all earlier attempts. No command modifies the template or historical shared specs. The `run` command generates, verifies, optionally attempts a proven repair, and publishes only after all checks pass.

For staged execution use `generate`, `verify`, `repair`, `package`, each with `--workspace`; the last three accept `--run-id` (otherwise latest generated run). `verify --build-only` is useful for diagnosis, but its result cannot be packaged. `verify --reuse-build` reuses a previous successful build only when source and artifact hashes still match; it reruns full isolated business/browser acceptance. `validate` and `generate` also require `--spec`; `generate` requires `--template`. Full `verify` and `run` require an explicit `--acceptance-pack device-borrow`; an unsupported or incompatible pack fails before builds or deployment. `verify --build-only` needs no pack or browser runtime.

## Specification contract

`version: 1` is a closed YAML schema. The example is executable documentation. Unknown fields, unsupported types/actions, invalid names, broken relations, invalid state transitions, missing form fields and unsafe exclusivity definitions are rejected before generation. Identifiers are lowercase snake_case. Internal `id`, `owner_id`, `created_at`, `status` fields are reserved. Supported field types: string (255 characters), signed 64-bit integer, boolean, ISO local datetime, enum, and foreign key to another entity or system_user. Create/update are full input operations, not patches. Requiredness, unique constraints, enum values and supported defaults are enforced.

`access: admin` gives template admin roles management permissions; owner workflows give normal users create/page/detail permissions and enforce login ownership. Admin manage permission enables all-request visibility. Reference catalogs are readable by applicants. Workflow transitions are administrator actions; forbid_self and exclusive flags are explicit. The exclusive reference must identify a required business entity field. Only one active record per referenced entity is allowed. A shared row lock precedes state checks and conditional updates. JDBC writes use an explicit transaction manager bound to the same datasource. A generated nullable active-reference column with a unique database index additionally enforces at most one active borrow. Optional state_labels provide human-readable workflow names.

Two independent integration packs are available: device-borrow (single-item exclusivity) and book-lending (quantity-based stock allocation). Other valid specifications can generate and build, but publication requires a compatible, dedicated business acceptance pack. No silent fallback to an unrelated domain exists.

## Template extension contract

The template must provide its existing backend/pom.xml, sql/schema.sql, frontend frozen lockfile and dynamic page glob, user permission store and deploy/compose.yaml. The core adds `com.original.business.generated`, metadata under resources/specforge, generated DTO records, typed frontend input interfaces, a shared Vue business panel, and pages beneath business/sf_<entity>. Existing dynamic routes load those pages from permission records. Only the generated copy of schema.sql is extended; SF001__business.sql is also included for inspection. This is fresh-database SQL, not an upgrade migration. No authentication/platform permission implementation is patched.

Tables and authorities are prefixed sf_ / business:sf_. Generated entities use soft deletion to preserve completed history. Unfinished workflow references block deletion; a deleted catalog entry cannot be used in a new request. Business actions, field validation and row ownership are checked server-side in addition to UI permissions.

## Workspaces, verification and release

Each run contains immutable input snapshots, source, reports and manifest. Identity includes template source SHA-256 per file, available Git revision, spec hash and project identity. Input paths are recorded for traceability. Secret environments, keys, dependency directories, caches and runtime state are excluded from template copying and delivery.

Verification builds with Maven clean verify, frozen pnpm install, Vue type check and production build. It then creates a uniquely named sf-accept-* Compose environment with random credentials, fresh volumes and a loopback-only ephemeral frontend port. The API pack exercises CRUD, validation, ownership, denial, illegal/repeated/self transitions, competing approvals and reborrowing. Chromium submits through real login and business forms and checks administrator workflow plus readonly/no-access behavior. No external mail is configured. Containers and acceptance volumes are removed in finally; daily preflight services are never targeted.

Only a full PASS can publish. Source and production artifact hashes must still equal the verified hashes. Archives contain source, production JAR, frontend dist, deployment configuration and a manifest. Publishing replaces the published pointer only after the new archive is complete; earlier releases remain available. The generated application retains the template's standalone Compose deployment and platform features.

The only initial automatic repair rule restores a missing LocalDateTime import in generated input records when the matching compiler diagnostic is present. It has a unit test. Unknown failures stop with reports. Maximum two attempts; no platform/security edits or model invocation.

## Browser adapter for Windows/WSL

There is one JavaScript browser scenario per acceptance pack. The portable default uses the Node runtime and Playwright core bundled with the optional Python Playwright distribution; Python contains no duplicate UI workflow. An optional Windows Node adapter can reuse a locally installed Playwright and Chromium without downloading a second browser into WSL:

```bash
export SPECFORGE_BROWSER_NODE=/mnt/c/path/to/node.exe
export SPECFORGE_PLAYWRIGHT_MODULE=C:/path/to/node_modules/playwright
export SPECFORGE_CHROMIUM_EXECUTABLE='C:/Program Files/Google/Chrome/Application/chrome.exe'
```

Credentials pass via stdin, never command-line arguments. The adapter stages its script and screenshots on a Windows native temporary drive, then copies only browser reports/screenshots back into the WSL run. Credentials are not retained in handoff reports. For hosts whose long-running WSL sessions lose Windows interop access, use `tools/run-core-windows.ps1`: it starts a hidden native worker, executes the full CLI, and cleans its private staging directory. Its Node, Playwright module, browser, distribution, template, spec and workspace paths are configurable. `-ReuseBuild` retries full acceptance without rebuilding matching artifacts.

## Failure diagnosis and old baseline

Start with reports/verify.json, then backend.log, frontend.log, compose.log, api.json or browser.json. A failed or build-only run cannot replace a published deliverable. Repair reports state why no known rule applies.

The historical Python suite was rerun before core integration: 25 tests, 12 passing, 10 failures and 3 errors. Failures include shared-spec/fixture drift (missing artifact_contract, old module source path, expected security schema) and scheduler verification scenarios. They are not treated as new-core acceptance gates; this iteration does not repair or replace that suite.

## Maintaining the core after the first audit

- `acceptance_packs/` owns domain fixtures, capability checks and browser scenarios. Register a new pack in its small explicit registry; the verifier does not inspect domain names or guess which pack to run.
- `browser.py` owns runtime discovery and checks the resulting browser report; `windows_browser.py` owns only native-drive staging and optional worker handoff. Business steps stay in the pack's single `browser.cjs`.
- Verification reports include failed_stage, acceptance_pack and build_only. Build/environment/API/browser/cleanup failures remain distinguishable. Cleanup errors are recorded alongside a primary failure rather than replacing it.
- Automatic repair is eligible only for backend compilation failure with unchanged source. Unknown compiler errors preserve their original diagnostic. Build-only repair stays build-only; UI or environment failures never enter code repair.
- Source inventory prunes excluded dependency directories before traversal and rejects included symlinks. Atomic JSON writes use unique temporary names; latest run pointers cannot escape the workspace.

This audit does not establish a second business acceptance pack. Cross-domain generation has a fixed regression case, but a second real business still needs end-to-end validation.

## Second business: quantity-based lending

`examples/book_lending.yaml` uses the same CLI, template, frontend panel, backend extension and verification engine as device borrowing. Select `--acceptance-pack book-lending` explicitly. Use a separate workspace because project identities cannot share a workspace.

```bash
python3 -m specforge run --workspace /home/zhang/.local/state/specforge-core/book-lending --spec examples/book_lending.yaml --template /mnt/e/Project/Zhang/openclaw-codegen/templates/admin-platform --acceptance-pack book-lending
```

Windows wrapper arguments:

```powershell
./run-specforge-core.ps1 -Spec /home/zhang/projects/ai/SpecForge/examples/book_lending.yaml -Workspace /home/zhang/.local/state/specforge-core/book-lending -AcceptancePack book-lending
```

Integer fields may declare `min`; schema validation, generated SQL CHECK constraints, backend validation and form controls all use that bound. A `capacity_reference` names the foreign reference, capacity field on its catalog, quantity field on the request, active state and terminal states. Quantity must be a required integer with min >= 1; capacity must be a required integer with min >= 0. Exactly one resource mode is allowed per workflow. A resource catalog cannot mix single-item and quantity workflows.

Pending requests do not reserve stock, including when total stock is zero. Entering the active state automatically checks and reserves quantity; no single-item exclusive transition flag is needed. Leaving the active state releases the complete request quantity. Partial returns are outside this example. Existing single-item specs keep their existing exclusive flags and database unique constraints.

Catalog rows are locked before request rows. All active quantity workflows sharing the same catalog/capacity field contribute to usage. Approval checks requested quantity against remaining capacity under the lock; capacity edits use the same lock and cannot reduce total below active usage. Returning changes state instead of incrementing a mutable stock counter, so duplicate returns cannot inflate total stock. Request quantities remain immutable after submission.

Catalog page/detail responses add `<capacity_field>_available`, derived from active usage. The generated panel displays this as a read-only availability column; it is never accepted as an input field. List values are informational snapshots; approval rechecks capacity inside the transaction. Completed history is preserved when a catalog row is soft deleted.

The two packs share HTTP/SQL fixture primitives and browser login/report infrastructure. The generated business engine has no book/loan/device/borrow name branches. Adding a new domain still means writing a suitable spec and domain assertions rather than duplicating an execution pipeline.
