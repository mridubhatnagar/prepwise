---
name: Debug
description: Diagnose and fix bugs in PrepIt, respecting the layered architecture and project conventions.
---

## Approach

1. **Read before touching anything**
   - Read the file with the bug and any files it depends on.
   - Understand the full call chain: controller → service → DAO (or request_handler → service → DAO).
   - Do not guess — trace the actual code path.

2. **Identify the layer where the bug lives**
   - Controller: request validation, response formatting, auth scope
   - Service: business logic, orchestration
   - DAO: database query, session management
   - RAG: embedding, retrieval, LLM call
   - Config: missing or misread env var

3. **Fix in the right layer**
   - Do not push business logic into controllers.
   - Do not push DB queries into services.
   - Do not bypass the service layer from a controller to fix a quick bug.

4. **Check exception handling**
   - Ensure the fix doesn't swallow exceptions silently.
   - Library exceptions must not leak past the layer that catches them.
   - If adding error handling, follow the project's exception hierarchy (`DatabaseError`, `EmbeddingError`, `RetrievalError`, `LLMError`, `OAuthError`).

5. **Check response shape**
   - API responses must follow: `{ "success": bool, "data": {...} | null, "error": str | null }`
   - Error responses: `{ "success": false, "data": null, "error": "Human-readable message" }`

## Common Bug Locations

| Symptom | Where to look |
|---|---|
| 401 on valid JWT | `dependencies.py` — `get_current_user` |
| 403 on valid user | `auth/scopes.py` — scope mismatch or wrong scope on endpoint |
| Empty chat response | `rag/orchestrator.py` — confidence check or LLM structured output parsing |
| Missing citations | `rag/orchestrator.py` — output guardrail stripping too aggressively |
| Context limit not triggering | `chat/dao.py` — `get_context_status` query |
| Spend not logged | `chat/request_handler.py` — `_log_spend` call |
| DB connection error | `infra/postgres.py` — `SessionLocal` config or missing env var |
| Weaviate connection error | `infra/weaviate.py` — host/port config (check `WEAVIATE_PORT=8083`) |
| Env var not found | `config.py` — missing key or `SETUP_ENV` not set |

## Rules
- Do not introduce `os.environ` calls outside `config.py`.
- Do not add direct DB access in controllers or services.
- Do not skip approval gates when fixing bugs across multiple phases.
- Add a `logger.error` or `logger.warning` at the fix point if one isn't already there.
- Keep the fix minimal — do not refactor surrounding code unless it is the direct cause of the bug.
