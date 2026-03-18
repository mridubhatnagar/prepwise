# PrepIt Code Review Skill

When reviewing code in this project, check all of the following:

---

## Layering

- [ ] Controllers only call the service layer or request handler — never DAOs directly
- [ ] Services only call DAOs — never instantiate them internally
- [ ] DAOs only access the database — no business logic
- [ ] RAG module (`rag/`) has no DAOs — `RetrievalClient` and `LLMClient` call external APIs directly

## Dependency Injection

- [ ] Services accept DAO interfaces in `__init__` — never instantiate DAOs internally
- [ ] Controllers receive services via FastAPI `Depends()` — never instantiate services directly
- [ ] DAOs import `SessionLocal` (or `weaviate_client`) from `infra` — not from anywhere else

## DAO Pattern

- [ ] Every DAO has a corresponding ABC interface defined in the same file (e.g. `IUserDAO` + `UserDAO`)
- [ ] Interface declares abstract methods; DAO class implements them
- [ ] Session managed at class level: `self.db = SessionLocal()` in `__init__`, closed in `__del__`
- [ ] DAO method names are generic: `create`, `list`, `get_*`, `clear`

## API Contract

- [ ] All API responses follow the standard envelope: `{ "success": bool, "data": {...} | null, "error": str | null }`
- [ ] All POST request bodies follow: `{ "data": { ... } }`
- [ ] Data inside `data` is nested by resource name (e.g. `{ "user": {...} }`, `{ "messages": [...] }`)
- [ ] `user_id` is always extracted from JWT payload — never from request body
- [ ] Pydantic `BaseModel` used for all request and response schemas

## Auth & Scopes

- [ ] Chat and Documents endpoints use `Depends(require_scope(Scope.APP))` — not `get_current_user` directly
- [ ] Auth endpoints (`/me`, `/logout`) use `Depends(get_current_user)`
- [ ] `/docs` (Swagger) uses `Depends(require_scope(Scope.DOCS))`

## Config & Environment

- [ ] `config.py` defines a `Config` class that reads all env vars as class-level attributes via `os.environ.get(...)`
- [ ] All modules access env vars through the `Config` class instance — never `os.environ` directly
- [ ] No secrets hardcoded anywhere

## Exception Handling

- [ ] Library exceptions (`sqlalchemy.exc.*`, `openai.*`, `weaviate.exceptions.*`) never leak past the layer that catches them
- [ ] DAOs catch SQLAlchemy exceptions → raise `DatabaseError`
- [ ] `RetrievalClient` catches Weaviate exceptions → raise `RetrievalError`; catches OpenAI exceptions → raise `EmbeddingError`
- [ ] `LLMClient` catches OpenAI exceptions → raise `LLMError`
- [ ] Controllers catch custom app exceptions → raise `HTTPException` with appropriate status + detail
- [ ] SMTP failures in `SpendService` are caught and logged silently — never affect chat response

## Logging

- [ ] `logger.info` for notable events (user allowed, chat cleared)
- [ ] `logger.warning` for rejected/unexpected inputs (auth failures, blocked requests)
- [ ] `logger.error` for exceptions and unexpected failures
- [ ] No sensitive data (passwords, tokens) in log messages

## Code Quality

- [ ] PEP 8 followed
- [ ] Docstrings only on non-trivial methods where purpose isn't clear from name + type hints
- [ ] No comments that merely restate what the code does
- [ ] Functions and classes are small and focused
