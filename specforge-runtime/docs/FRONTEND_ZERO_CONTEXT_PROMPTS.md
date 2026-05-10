# Frontend Zero-Context Prompts

Use this document when another Codex session or a frontend repository needs to continue from an already generated backend.

## Goal

Start from:

- `specforge-runtime/outputs/<project-backend>/`

End at:

- a frontend agent can log in
- consume real business routes
- avoid inventing mock APIs

## Prompt A: Direct Frontend Handoff

```text
Use this repository's generated backend as the only backend contract source.
Do not ask me to restate the backend API manually.

Read these files first:
1. specforge-runtime/outputs/<project-backend>/logs/demo-access.yaml
2. specforge-runtime/outputs/<project-backend>/logs/api-smoke/postman-collection.json
3. specforge-runtime/outputs/<project-backend>/logs/api-smoke/postman-environment.json
4. specforge-runtime/outputs/<project-backend>/logs/delivery-validation.yaml
5. specforge-runtime/outputs/<project-backend>/logs/api-smoke/business-contract-validation.yaml

Execution contract:
1. Infer the frontend login flow, token usage, route groups, and business modules from those backend delivery assets.
2. Treat /v1/authorize/login as the canonical login entry.
3. Use the demo credentials and baseUrl contract from demo-access.yaml and postman-environment.json.
4. Build or adapt the frontend against the real generated business routes instead of inventing mock APIs.
5. Keep going until the frontend can complete login and call at least one representative business endpoint successfully.
6. If there is a backend/frontend mismatch, report the exact backend asset file that proves the contract.
7. Do not ask me for step-by-step confirmation unless there is a destructive risk.
```

## Prompt B: Frontend Repo + This Backend

```text
Use my frontend repository together with the generated backend from this SpecForge repository.
Treat the generated backend delivery assets as the source of truth for API contracts.

Read:
1. specforge-runtime/docs/FRONTEND_HANDOFF_BACKEND_CONTRACT.md
2. specforge-runtime/outputs/<project-backend>/logs/demo-access.yaml
3. specforge-runtime/outputs/<project-backend>/logs/api-smoke/postman-collection.json
4. specforge-runtime/outputs/<project-backend>/logs/api-smoke/postman-environment.json

Then:
1. connect the frontend login flow to /v1/authorize/login
2. apply token handling exactly as required by the backend
3. wire the main business pages to the generated route groups
4. verify at least one business API call after login
5. report any mismatch with file-level evidence from the backend assets
```

## Generator Script

If you want a ready-to-paste prompt, run:

```powershell
python skills/specforge-full-project-compiler/scripts/emit_frontend_handoff_prompt.py --backend-output specforge-runtime/outputs/<project-backend> --project-name "<project-name>"
```

## Minimum Backend Assets Required

- `logs/demo-access.yaml`
- `logs/api-smoke/postman-collection.json`
- `logs/api-smoke/postman-environment.json`
- `logs/delivery-validation.yaml`
- `logs/api-smoke/business-contract-validation.yaml`

## Rule

For frontend docking, do not treat:

- `backend/`
- `specforge-runtime/runs/`

as contract sources.

Treat only:

- `specforge-runtime/outputs/<project-backend>/`

as the final backend contract surface.
