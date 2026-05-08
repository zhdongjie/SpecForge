# SpecForge

SpecForge is a deterministic Spring Boot backend compiler workflow.

Its goal is:

- input a short project requirement or a requirement document
- compile project specs and module specs
- generate a full backend
- verify compile and boot
- export the final backend into a stable output directory

## Directory Map

- `backend/`
  - baseline backend template

- `specforge-runtime/`
  - compiler runtime
  - canonical specs live in `specforge-runtime/specs/`
  - final generated projects export into `specforge-runtime/outputs/`

- `skills/`
  - Codex skills, including the full-project compiler skill

- `sandbox/`
  - local-only validation area
  - ignored by git

See [WORKSPACE_LAYOUT.md](WORKSPACE_LAYOUT.md) for the full workspace contract.

## Fastest Path

If you want:

- one project name
- or one short requirement
- and one complete generated backend

use this flow.

### 1. Prepare toolchain

Install:

- JDK 17+
- Maven 3.9+

Recommended environment variables:

- `SPECFORGE_JAVA_HOME`
- `SPECFORGE_MAVEN_CMD`

See [ENVIRONMENT_MIGRATION_RUNBOOK.md](E:/Project/Generate/SpecForge/specforge-runtime/docs/ENVIRONMENT_MIGRATION_RUNBOOK.md) for the portability contract.

### 2. Check workspace

```powershell
python skills/specforge-full-project-compiler/scripts/check_specforge_workspace.py --repo-root .
```

Expected result:

- `"ready": true`

### 3. Scaffold from a short requirement

Example:

```powershell
python skills/specforge-full-project-compiler/scripts/scaffold_requirement_project.py --repo-root . --project-name "Laboratory Reservation Platform" --requirement "Build a complete laboratory reservation management backend with reservation approval, notification, and laboratory access control under a modular-monolith Spring Boot architecture." --force
```

This writes canonical specs into:

- `specforge-runtime/specs/project-spec.md`
- `specforge-runtime/specs/project-assembly-plan.yaml`
- `specforge-runtime/specs/build-plan.yaml`
- `specforge-runtime/specs/templates/...`

### 4. Run the canonical auto-build

```powershell
python skills/specforge-full-project-compiler/scripts/run_specforge_autobuild.py --repo-root . --run-id lab-platform-001
```

### 5. Check results

Success report:

- `specforge-runtime/runs/lab-platform-001/logs/auto-build-report.yaml`

Health report:

- `specforge-runtime/runs/lab-platform-001/generated-project/logs/project-health-report.yaml`

Final exported backend:

- `specforge-runtime/outputs/<project-backend>/`

## Final Output Rule

Treat only this as the final generated project:

- `specforge-runtime/outputs/<project-backend>/`

Do not treat these as final deliverables:

- `sandbox/...`
- `specforge-runtime/runs/<run-id>/generated-project/`

Those are validation and intermediate directories.

## Canonical End-to-End Commands

Workspace readiness:

```powershell
python skills/specforge-full-project-compiler/scripts/check_specforge_workspace.py --repo-root .
```

Scaffold project specs:

```powershell
python skills/specforge-full-project-compiler/scripts/scaffold_requirement_project.py --repo-root . --project-name "<project-name>" --requirement "<requirement>" --force
```

Compile full backend:

```powershell
python skills/specforge-full-project-compiler/scripts/run_specforge_autobuild.py --repo-root . --run-id <run-id>
```

Direct runtime equivalent:

```powershell
cd specforge-runtime
python main.py --auto-build --build-plan build-plan.yaml --run-id <run-id>
```

## Handoff Rule

When moving to another machine or another Codex session:

1. Read [README.md](README.md)
2. Read [WORKSPACE_LAYOUT.md](WORKSPACE_LAYOUT.md)
3. Read [PROJECT_COMPILER_PROTOCOL.md](E:/Project/Generate/SpecForge/specforge-runtime/docs/PROJECT_COMPILER_PROTOCOL.md)
4. Read [ENVIRONMENT_MIGRATION_RUNBOOK.md](E:/Project/Generate/SpecForge/specforge-runtime/docs/ENVIRONMENT_MIGRATION_RUNBOOK.md)
5. Use `specforge-runtime/specs/build-plan.yaml` as the canonical execution entry

## Current Proven Flow

The validated local flow now supports:

- scaffold from a one-line requirement
- assemble multiple business modules
- compile pass
- boot pass
- final export under `specforge-runtime/outputs/`
