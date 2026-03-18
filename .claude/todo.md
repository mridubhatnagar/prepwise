# PrepIt V1 — TODO List

## Phase 0 — Design (Claude)
- [x] Generate `mockups/landing.html` — landing + Google Sign-In
- [x] Generate `mockups/chat.html` — chat interface with sidebar
- [x] Generate `mockups/error.html` — 403/404 error page with Lost.gif illustration
- [x] User approves all mockups

---

## Phase 0b — Infrastructure Setup (Lead)
### Docker Compose — Infra services (do before agent handoff)
- [x] Create `docker-compose.yml` with 4 services: `postgres`, `weaviate`, `phoenix`, `pgadmin`
- [x] Fill `.env.local` with real values (DB credentials, Weaviate port, Phoenix port, pgadmin credentials)
- [x] Run `docker compose up` — verify all 4 services healthy

### Virtualenv (do after backend agent generates requirements.txt)
- [x] Create virtualenv: `python -m venv venv && source venv/bin/activate`
- [x] Install dependencies: `pip install -r requirements.txt`
- Packages include: `fastapi`, `sqlalchemy`, `alembic`, `psycopg2-binary`, `weaviate-client`, `openai`, `tiktoken`, `python-jose[cryptography]`, `httpx`, `python-dotenv`, `arize-phoenix-otel`, `openinference-instrumentation-openai`, `slowapi`

### Docker Compose — App service (do after requirements.txt is ready)
- [x] Write `Dockerfile` for the FastAPI app (after backend agent generates `requirements.txt`)
- [x] Add `app` service to `docker-compose.yml`
- [x] Run `docker compose up` — verify app starts and connects to postgres + weaviate

### SMTP Setup
- [x] Create Gmail app password for spend alert emails
- [x] Add SMTP credentials to `.env.local`

---

## Phase 1a — Database Agent
### PostgreSQL
- [x] Create `infra/postgres.py` — SQLAlchemy engine, SessionLocal, Base
- [x] Create `infra/__init__.py` — expose `SessionLocal` from `infra.postgres` and `weaviate_client` from `infra.weaviate` for DAO imports
- [x] Create `auth/models.py` — `User`, `AllowedUser` (with `scope` column), `AccessAttempt` ORM models
- [x] Create `chat/models.py` — `ChatMessage` ORM model with `content TEXT`, `citations JSONB`, `follow_up_questions JSONB` columns
- [x] Set up Alembic (`alembic init`, configure `alembic.ini` with env-based DB URL)
- [x] Generate and apply initial migration — creates all 4 tables: `users`, `allowed_users`, `access_attempts`, `chat_messages`
- [x] Create `auth/dao.py` — three interfaces and their implementations, all with session managed at class level (`self.db = SessionLocal()` in `__init__`, closed in `__del__`):
  - `IUserDAO(ABC)` — abstract methods: `create`, `update`, `get_by_auth_id`, `get_by_id`; `UserDAO(IUserDAO)` implements all
  - `IAllowedUserDAO(ABC)` — abstract method: `is_allowed`; `AllowedUserDAO(IAllowedUserDAO)` implements it
  - `IAccessAttemptDAO(ABC)` — abstract method: `create`; `AccessAttemptDAO(IAccessAttemptDAO)` implements it
- [x] Create `chat/dao.py` — `IChatMessageDAO(ABC)` interface with abstract methods: `create`, `list`, `get_context_status`, `clear`; `ChatMessageDAO(IChatMessageDAO)` implements all methods; session managed at class level (`self.db = SessionLocal()` in `__init__`, closed in `__del__`); assistant messages store `content` (answer text), `citations` (JSONB array), `follow_up_questions` (JSONB array); user messages store only `content`

> **PAUSE — PostgreSQL section complete. Show lead created files and wait for approval before continuing.**

- [x] Create `spend/models.py` — `SpendLog` SQLAlchemy ORM model
- [x] Create `spend/dao.py` — `ISpendDAO (ABC)` + `SpendDAO` — `create`, `get_total(date)`; session managed at class level

> **PAUSE — Spend models complete. Show lead created files and wait for approval before continuing.**

### Weaviate
- [x] Create `infra/weaviate.py` — Weaviate client
- [x] Define `KnowledgeChunk` class schema in Weaviate (content, source_doc, section_title, category, chunk_index)
- [x] Create `documents/models.py` — `Document` Pydantic model (API response shape only — NOT a Weaviate schema; Weaviate schema is defined via the client in `scripts/ingest.py`)
- [x] Create `documents/dao.py` — `IDocumentDAO(ABC)` interface with abstract method `list`; `DocumentDAO(IDocumentDAO)` implements it; Weaviate client managed at class level (`self.client = weaviate_client` in `__init__`); queries Weaviate for all KnowledgeChunk metadata, deduplicates in Python

> **PAUSE — Weaviate section complete. Show lead created files and wait for approval before continuing.**

### Ingestion Script
- [x] Create `scripts/ingest.py` — walk /docs, chunk by markdown headers, embed via OpenAI, upload to Weaviate. **Skip the `docs/logs/` folder entirely** — these are informal learning notes and should not be ingested.
- [x] Test: run ingest script → verify chunk count and metadata in Weaviate

> **PAUSE — Ingestion script complete. Show lead output and wait for approval before continuing.**

### Seed
- [x] Manually insert lead's email into `allowed_users` with `scope = 'app,docs'` so the lead can sign in and access Swagger on first use

> **PAUSE — Seed complete. Wait for lead approval before running verification.**

### Verification
- [x] `psql` → `\dt` shows all 4 tables: `users`, `allowed_users`, `access_attempts`, `chat_messages`
- [x] `psql` → `SELECT * FROM allowed_users` shows lead's email
- [x] Run `scripts/ingest.py` → N docs, M chunks printed
- [x] `http://localhost:8080/v1/objects` → KnowledgeChunk objects visible

---

## Phase 1b — Backend Agent
### Setup
- [x] Create `__init__.py` in `auth/`, `chat/`, `documents/`, `rag/`, `spend/` — required for Python package imports (`infra/__init__.py` is owned by the Database agent)
- [x] Create `enums.py` (project root) — `MessageRole(str, Enum)` with `USER`, `ASSISTANT`; `Scope(str, Enum)` with `APP`, `DOCS`
- [x] Create `config.py` — Config class reading all env vars via `os.environ`; includes timeout values `OPENAI_TIMEOUT`, `GOOGLE_API_TIMEOUT`, rate limit values, and spend alert values (`SPEND_ALERT_THRESHOLD`, `ALERT_EMAIL`, `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`)
- [x] Create `constants.py` — OpenAI token pricing constants: `GPT4O_INPUT_COST_PER_1M = 2.50`, `GPT4O_OUTPUT_COST_PER_1M = 10.00`, `EMBEDDING_INPUT_COST_PER_1M = 0.02`; Google OAuth URLs: `GOOGLE_TOKEN_URL`, `GOOGLE_USERINFO_URL`
- [x] Create `exceptions.py` (project root) — defines all custom app exceptions: `DatabaseError`, `EmbeddingError`, `RetrievalError`, `LLMError`, `OAuthError`
- [x] Create `dependencies.py` (project root) — `get_current_user` FastAPI dependency; reads JWT from `jwt` HttpOnly cookie in browser requests; reads from `Authorization: Bearer` header in curl/testing requests; verifies signature + expiry, confirms user exists in DB; imported by all protected controllers via `Depends(get_current_user)`
- [x] Create `app.py` — FastAPI app, register all routers, mount `/static` (StaticFiles), serve page routes using `FileResponse` (`GET /` — public; `GET /chat` — protected by `require_scope(Scope.APP)`), serve `/docs` protected by `require_scope(Scope.DOCS)`, register 403 + 404 exception handlers returning `FileResponse("templates/error.html")`, initialize Phoenix tracer + OpenAI instrumentation on startup, add security headers middleware (X-Content-Type-Options, X-Frame-Options), initialize `slowapi` Limiter and register rate limit exception handler
- [x] Create `.env.example` — all keys with empty values, committed to git as reference; also add `SETUP_ENV=` as the first key (defaults to `local` in config.py if not set)
- [x] Create `requirements.txt` — include: fastapi, uvicorn, sqlalchemy, alembic, psycopg2-binary, weaviate-client, openai, tiktoken, python-jose[cryptography], httpx, python-dotenv, arize-phoenix-otel, openinference-instrumentation-openai, slowapi

> **PAUSE — Setup section complete. Show lead created files and wait for approval before continuing.**

### Auth
- [x] Create `auth/scopes.py` — `require_scope(Scope)` FastAPI dependency; imports `Scope` from `enums.py`
- [x] Create `auth/utils.py` — `generate_jwt_token(user_id, scopes)` JWT generation only (HS256, 1-hour expiry)
- [x] Create `auth/service.py` — `AuthService(user_dao: IUserDAO)`; methods: `prepare_oauth_redirect` (generates state nonce + Google auth URL), `fetch_oauth_user_info` (verifies state, hits Google token endpoint + userinfo API), `handle_oauth_callback` (calls `fetch_oauth_user_info`, checks allowlist, creates/updates user, generates JWT); calls `generate_jwt_token` from `auth/utils.py`; includes `scopes` claim from `allowed_users.scope`
- [x] Create `auth/controller.py` — `GET /api/auth/initiate` (generate state, set oauth_state cookie, 302 redirect to Google; rate limited `AUTH_RATE_LIMIT/minute` per IP), `GET /auth/callback` (verify state, clear cookie, exchange code, set JWT cookie; redirect to `/chat` on success, `/?error=invite_only` if not in allowlist, `/?error=unverified_email` if email unverified, `/?error=auth_failed` on state mismatch or Google API failure), `POST /api/auth/logout`, `GET /api/auth/me`; wire `AuthService` via FastAPI `Depends()` chain

> **PAUSE — Auth section complete. Show lead created files and wait for approval before continuing.**

### RAG
- [x] Create `rag/llm_client.py` — `LLMClient`; methods: `build_prompt(query, chunks, history)`, `generate_response(messages)` — GPT-4o call with OpenAI `response_format` (JSON schema); returns `{ answer, citations, follow_up_questions, input_tokens, output_tokens }`; no free-text parsing
- [x] Create `rag/retrieval_client.py` — `RetrievalClient`; methods: `generate_embedding(query)`, `search(query, embedding)`, `retrieve(query)` — Weaviate hybrid search (BM25 + cosine, alpha=0.5, top_k=5)
- [x] Create `rag/orchestrator.py` — `RAGOrchestrator(retrieval_client: RetrievalClient, llm_client: LLMClient)`; methods: `retrieve_chunks(query)`, `is_confident(chunks)`, `build_response(query, chunks, history)`; prompt injection regex blocklist check inside `build_response` before LLM call; output guardrail inside `build_response` — strip citations not in retrieved chunks

> **PAUSE — RAG section complete. Show lead created files and wait for approval before continuing.**

### Chat
- [x] Create `chat/service.py` — `ChatService(chat_message_dao: IChatMessageDAO)`; methods: `get_chat_context_details(session_id)`, `list_chat_messages(user_id, limit)`, `list_chat_messages_by_session(session_id)`, `create_chat_message(session_id, user_id, role, content, token_count, citations, follow_up_questions)`, `get_message_by_id(message_id)`; all DB access via `chat_message_dao`
- [x] Create `chat/request_handler.py` — `ChatRequestHandler(chat_service: ChatService, rag_orchestrator: RAGOrchestrator, spend_service: SpendService)`; methods: `handle_chat_message(user_id, query)`, `list_messages(user_id)`, `clear_messages(user_id)`; private methods: `_check_context`, `_get_history`, `_generate_response`, `_persist`, `_log_spend`
- [x] Create `chat/controller.py` — `POST /api/chat/messages` (rate limited `CHAT_RATE_LIMIT/minute` per user_id), `GET /api/chat/messages`, `POST /api/chat/sessions` (Clear Chat — deactivates current session, creates new one; messages retained in DB); all routes use `Depends(require_scope(Scope.APP))`; wire `ChatRequestHandler` via FastAPI `Depends()` chain

> **PAUSE — Chat section complete. Show lead created files and wait for approval before continuing.**

### Spend
- [x] Create `spend/service.py` — `SpendService(spend_dao: ISpendDAO)`; methods: `create_spend(user_id, model, input_tokens, output_tokens, endpoint)` — calculates cost using `constants.py`, saves via `spend_dao.create`; `get_total_spend(date)` — calls `spend_dao.get_total(date)`; `spend_email_alert()` — crossing-point check, sends email via `smtplib` if threshold crossed

> **PAUSE — Spend service complete. Show lead created files and wait for approval before continuing.**

### Documents
- [x] Create `documents/service.py` — `DocumentService(document_dao: IDocumentDAO)`; method: `list_documents_by_categories()` — calls `document_dao.list()`, groups by category in Python, returns `{ category: [doc_names] }`
- [x] Create `documents/controller.py` — `GET /api/documents`; returns grouped `{ documents: { category: [doc_names] } }`; route uses `Depends(require_scope(Scope.APP))`; wire `DocumentService` via FastAPI `Depends()` chain

> **PAUSE — Documents section complete. Show lead created files and wait for approval before continuing.**

### Feedback
- [x] Create `feedback/service.py` — `FeedbackService(feedback_dao: IFeedbackDAO)`; method: `submit_feedback(user_id, message_id, rating)` — if rating is non-null: upsert; if null: delete (deselect); validates message_id belongs to the authenticated user via `ChatMessageDAO` (404 if not found)
- [x] Create `feedback/controller.py` — `POST /api/feedback`; body: `{ "data": { "message_id": string, "rating": "up" | "down" | null } }`; rating null = remove feedback; route uses `Depends(require_scope(Scope.APP))`; wire `FeedbackService` via FastAPI `Depends()` chain

> **PAUSE — Feedback section complete. Show lead created files and wait for approval before continuing.**

### Error Page
- [x] Create `templates/error.html` — 403/404 error page with `static/img/Lost.gif`, badge, headline, message, "Go to Home" button (`static/img/Lost.gif` already exists — do not recreate)

> **PAUSE — Error page complete. Show lead and wait for approval before continuing.**

### Health
- [x] Add `GET /health` endpoint → `{ status: "ok" }`

> **PAUSE — Health endpoint complete. Wait for lead approval before running verification.**

### Verification
- [x] `docker compose ps` → `prepit_app` container is `Up`
- [x] `curl http://localhost:8000/health` → `{ "status": "ok" }`
- [x] `curl .../api/auth/me` with valid JWT → returns `{ user: { id, name, email, avatar_url } }`
- [x] `curl .../api/documents` with `app` scoped JWT → returns doc list
- [x] `curl -X POST .../api/chat/messages` with "What is CAP theorem?" → answer + citations + follow-ups
- [x] `curl -X POST .../api/chat/messages` with "What is React?" → "Sorry, this is beyond my current scope"
- [x] `curl -X GET .../api/chat/messages` with `app` scoped JWT → returns message list
- [x] `curl -X POST .../api/chat/sessions` → `{ "success": true, "data": { "session_id": "..." } }`
- [x] `curl -X POST .../api/chat/messages` with `docs`-only scoped JWT → `403 Forbidden`
- [x] `GET /chat` with `docs`-only scoped JWT → 403 error page served

---

## Phase 1c — Frontend Agent
### Prerequisites
- [x] Phase 0 mockups approved

### Landing Page
- [x] Create `templates/landing.html` — two-panel layout, Google Sign-In button (Bootstrap styled); reference mockup at `mockups/landing.html`; `static/img/favicon.svg` already exists — do not recreate
- [x] Wire Google OAuth redirect on Sign-In button click: `window.location.href = '/api/auth/initiate'` — backend handles state generation, cookie, and redirect to Google; detect `?error=invite_only`, `?error=unverified_email`, `?error=auth_failed`, and `?error=session_expired` params on init to show appropriate flash messages (Bootstrap alert, top-center, auto-dismiss after 5s, manually dismissable)

> **PAUSE — Landing page complete. Show lead in browser and wait for approval before continuing.**

### Chat Interface
- [x] Create `templates/chat.html` — app bar, collapsible sidebar, chat window, input bar; reference mockup at `mockups/chat.html`; `static/img/favicon.svg` already exists — do not recreate
- [x] Sidebar: render doc list using `x-for` over `documents` grouped by category (hardcoded values in state for Phase 1c, replaced by API in Phase 2); collapse/expand toggle
- [x] Chat window: empty state (shown when `messages.length === 0`) with greeting + suggestion chips rendered via `x-for` over `suggestions`; messages area (shown when `messages.length > 0`) with placeholder messages rendered via `x-for` over `messages` (user right-aligned, AI left-aligned); citation chips via `x-for` over `message.citations`; follow-up pills via `x-for` over `message.follow_up_questions`; app bar name + avatar initials bound to `user.name` / `user.initials`
- [x] Input bar: textarea + Send button only (no Clear Chat button)
- [x] Context limit banner: controlled by `contextLimitReached` flag — contains "Clear Chat" button when visible
- [x] Create `static/js/main.js` — Alpine.js app with the following state structure (hardcoded values, API wired in Phase 2):
  ```js
  {
    messages: [],           // array of { role, content, citations: [{ doc_name, section_title, category }], follow_up_questions: string[], time } — all three arrays rendered with x-for
    documents: [],          // array of { name, category } — drives sidebar with x-for, grouped by category
    suggestions: [          // starter chips on empty state — rendered with x-for
      'What is the CAP theorem?', 'Explain consistent hashing',
      'SQL vs NoSQL — when to use which?', 'How does a vector database work?',
      'What is sharding?', 'Explain the Transformer architecture'
    ],
    user: { name: 'Mridu', initials: 'MR' },  // populated from JWT in Phase 2; drives app bar name + avatar initials
    inputText: '',          // bound to textarea
    isLoading: false,       // shows typing indicator bubble while awaiting API response
    contextLimitReached: false,  // shows/hides context limit banner
    sidebarCollapsed: false,
  }
  ```
- [x] Typing indicator: show an animated "..." AI bubble when `isLoading === true`
- [x] Implement `sendMessage(text)` Alpine.js method — Phase 1c stub: append message + hardcoded AI response to `messages` array; Send button, suggestion chips, and follow-up pills all call this method
- [x] Error handling on API responses: on 503 → disable Send button for 5 seconds, display `detail` field as error message; on 429 → disable Send button for 60 seconds with a visible countdown timer, display `"You're sending messages too fast. Please wait a moment."`
- [x] Auto-scroll messages area to bottom whenever a new message is added
- [x] Add `static/components/` for reusable Alpine.js components (message bubble, citation chip, sidebar item)

> **PAUSE — Chat interface complete. Show lead in browser and wait for approval before running verification.**

### Verification (open HTML files directly in browser — no server needed)
- [x] `templates/chat.html`: empty state visible by default (messages array empty)
- [x] Set `messages` to hardcoded array in state → messages area renders with bubbles, citation chips, follow-up pills via x-for
- [x] Set `isLoading: true` → typing indicator bubble appears
- [x] Set `contextLimitReached: true` → context limit banner appears with Clear Chat button
- [x] Change `user.name` / `user.initials` in state → app bar updates
- [x] Sidebar collapses and expands
- [x] `templates/landing.html`: Google Sign-In button visible and styled

---

## Phase 2 — Integration Agent
### Prerequisites
- [x] Phase 1a, 1b, 1c all verified

### Wiring
- [x] Call `GET /api/auth/me` on chat page init → populate `user.name` and `user.initials` in Alpine state
- [x] Replace hardcoded doc list with `GET /api/documents`
- [x] Replace hardcoded chat history with `GET /api/chat/messages` on page load
- [x] Replace `sendMessage(text)` stub with `POST /api/chat/messages` — renders answer, citation chips, follow-up pills; used by Send button, suggestion chips, and follow-up pills
- [x] Wire Clear Chat button to `POST /api/chat/sessions` — deactivates current session, creates new one, clears message thread in UI (messages retained in DB)
- [x] Wire Sign Out to `POST /api/auth/logout` → redirect to `/`
- [x] Wire 401 response on any API call → redirect to `/?error=session_expired` with flash message: "Your session has expired. Please sign in again."
- [x] Show context limit banner when `context_status.limit_reached = true`
- [x] Wire thumbs up/down buttons on AI messages to `POST /api/feedback` — send `message_id` + `rating`; rating null on re-click to deselect
- [x] Run Alembic migrations on backend startup (skipped — migrations already applied; auto-run risks revision mismatch)
- [x] Run `scripts/ingest.py` to populate Weaviate

> **PAUSE — All wiring complete. Show lead what was changed and wait for approval before running verification.**

### Verification
- [x] Full flow: Sign In → chat loads history → ask "What is CAP theorem?" → answer with citations renders
- [x] User name and avatar initials populate correctly in app bar from `GET /api/auth/me`
- [x] Ask "What is React?" → "Sorry, this is beyond my current scope" message renders
- [x] Click a suggestion chip → message sent, AI response renders, empty state replaced by messages area
- [x] Click a follow-up pill → message sent, new AI response renders
- [x] Send 20 messages → context limit banner appears
- [x] Click Clear Chat → conversation resets, empty state shown
- [x] Phoenix traces visible at `http://localhost:6006`
- [x] Sign in as `docs`-only user → navigate to `/chat` → 403 error page served (never reaches chat UI)

---

## Addendum — Session Handling & Feedback (New Work)

These tasks were not part of the original implementation. They must be completed by the relevant agent in a follow-up pass.

### Database Agent
- [x] Add `ChatSession` ORM model to `chat/models.py` — columns: `id UUID PK default gen_random_uuid()`, `user_id UUID FK → users(id) ON DELETE CASCADE`, `is_active BOOLEAN NOT NULL default true`, `created_at TIMESTAMP default NOW()`; `__tablename__ = 'chat_sessions'`
- [x] Add `session_id UUID FK → chat_sessions(id) ON DELETE CASCADE` column to `ChatMessage` ORM model in `chat/models.py`; add `message_index INTEGER NOT NULL` column (sequential counter per user); add composite index on `(user_id, message_index)`; add `token_count INTEGER NOT NULL default 0` column if not already present
- [x] Add `Feedback` ORM model to `feedback/models.py` — columns: `id UUID PK default gen_random_uuid()`, `message_id UUID FK → chat_messages(id) ON DELETE CASCADE NOT NULL UNIQUE`, `user_id UUID FK → users(id) ON DELETE CASCADE NOT NULL`, `rating VARCHAR(10) NOT NULL CHECK IN ('up', 'down')`, `created_at TIMESTAMP default NOW()`; `__tablename__ = 'feedback'`; add index on `(user_id)`
- [x] Generate and apply new Alembic migration — adds `chat_sessions` table, adds `session_id`, `message_index`, `token_count` columns to `chat_messages`, adds `feedback` table; migration must be reversible (downgrade removes same)
- [x] Add `IChatSessionDAO(ABC)` + `ChatSessionDAO` to `chat/dao.py` — session managed at class level (`self.db = SessionLocal()` in `__init__`, closed in `__del__`); wrap all DB calls in try/except → catch `sqlalchemy.exc.*` → log `logger.error` → raise `DatabaseError`:
  - `create(user_id: str) → ChatSession` — inserts new session with `is_active=True`, commits, returns it
  - `get_active(user_id: str) → ChatSession | None` — queries for session where `user_id` matches and `is_active=True`; returns first result or None
  - `update_status(session_id: str, is_active: bool) → None` — sets `is_active` on the given session and commits
- [x] Update `IChatMessageDAO` abstract methods and `ChatMessageDAO` in `chat/dao.py`:
  - `create(session_id: str, user_id: str, role: MessageRole, content: str, token_count: int, citations: list | None, follow_up_questions: list | None) → ChatMessage` — computes `message_index` as `MAX(message_index) + 1` for this `user_id` (0 if no prior messages); inserts and commits
  - `list(user_id: str, limit: int = None) → list[ChatMessage]` — returns messages for user ordered by `created_at`; applies limit if provided
  - `list_by_session_id(session_id: str) → list[ChatMessage]` — returns all messages for a session ordered by `created_at`
  - `get_current_context_details(session_id: str) → dict` — returns `{ "message_count": int, "token_count": int }` — `message_count` is COUNT of rows for session; `token_count` is SUM of `token_count` for session
  - `get_by_id(message_id: str) → ChatMessage | None` — fetch single message by primary key; returns None if not found
- [x] Create `feedback/dao.py` — `IFeedbackDAO(ABC)` + `FeedbackDAO`; session managed at class level; wrap all DB calls in try/except → catch `sqlalchemy.exc.*` → log `logger.error` → raise `DatabaseError`:
  - `create(message_id: str, user_id: str, rating: str) → Feedback` — inserts new feedback row, commits, returns it
  - `update(feedback_id: str, rating: str) → Feedback` — updates `rating` on existing row by `id`, commits, returns updated row
  - `delete_by_id(feedback_id: str) → None` — deletes row by `id`, commits
  - `get_by_id(feedback_id: str) → Feedback | None` — fetch feedback by primary key
  - `get_by_message_id(message_id: str) → Feedback | None` — fetch feedback by `message_id` (UNIQUE constraint — at most one row per message)
- [x] Create `feedback/__init__.py` — empty, required for Python package imports
- [x] Verify: `psql` → `\dt` shows all 7 tables: `users`, `allowed_users`, `access_attempts`, `chat_sessions`, `chat_messages`, `spend_log`, `feedback`

> **PAUSE — Show lead updated files and migration output. Wait for approval before continuing.**

### Backend Agent
- [x] Add `feedback/__init__.py` if not already created by Database agent (empty file)
- [x] Add `langchain-text-splitter` to `requirements.txt`
- [x] Register `feedback` router in `app.py` alongside existing routers
- [x] Add `ChatSessionService(chat_session_dao: IChatSessionDAO)` class to `chat/service.py`:
  - `get_active_session(user_id: str) → ChatSession | None` — calls `chat_session_dao.get_active(user_id)`
  - `create_session(user_id: str) → ChatSession` — calls `chat_session_dao.create(user_id)`; returns new session
  - `update_session_status(session_id: str, is_active: bool) → None` — calls `chat_session_dao.update_status(session_id, is_active)`
- [x] Update `ChatService` in `chat/service.py` — rename and update methods to match arch.md:
  - `get_chat_context_details(session_id: str) → dict` — calls `chat_message_dao.get_current_context_details(session_id)`; returns `{ message_count, token_count, limit_reached }` where `limit_reached = message_count >= 20 OR token_count >= 2000`
  - `list_chat_messages(user_id: str, limit: int = None) → list[ChatMessage]` — calls `chat_message_dao.list(user_id, limit)`
  - `list_chat_messages_by_session(session_id: str) → list[ChatMessage]` — calls `chat_message_dao.list_by_session_id(session_id)`
  - `create_chat_message(session_id: str, user_id: str, role: MessageRole, content: str, token_count: int, citations: list | None = None, follow_up_questions: list | None = None) → ChatMessage` — calls `chat_message_dao.create(...)`
  - `get_message_by_id(message_id: str) → ChatMessage | None` — calls `chat_message_dao.get_by_id(message_id)`
- [x] Update `chat/request_handler.py` — `ChatRequestHandler` injects only `chat_service: ChatService`, `rag_orchestrator: RAGOrchestrator`, `spend_service: SpendService` (no session service — session_id resolved in controller and passed in); update method signatures:
  - `handle_chat_message(user_id: str, session_id: str, query: str) → dict` — calls `_check_context(session_id)`, `_get_history(session_id)`, `_generate_response(query, history)`, `_persist(user_id, session_id, query, response)`, `_log_spend(user_id, response)`; returns full response shape
  - `list_messages(session_id: str) → list[ChatMessage]` — calls `chat_service.list_chat_messages_by_session(session_id)`
  - `_check_context(session_id: str) → dict | None` — calls `chat_service.get_chat_context_details(session_id)`; if `limit_reached` is True: returns early response shape with `"answer": "You've reached the conversation limit. Clear your chat to continue."`, `citations: []`, `follow_up_questions: []`, `limit_reached: true`; otherwise returns None
  - `_get_history(session_id: str) → list[ChatMessage]` — calls `chat_service.list_chat_messages_by_session(session_id, limit=10)` for last 10 messages used in LLM prompt
  - `_generate_response(query: str, history: list[ChatMessage]) → dict` — calls `rag_orchestrator.retrieve_chunks(query)`, `rag_orchestrator.is_confident(chunks)` (returns out-of-scope message if not confident), `rag_orchestrator.build_response(query, chunks, history)`; returns `{ answer, citations, follow_up_questions, input_tokens, output_tokens }`
  - `_persist(user_id: str, session_id: str, query: str, response: dict) → str` — calculates token counts via `tiktoken` `cl100k_base` encoding for user message and assistant answer; calls `chat_service.create_chat_message` twice — user turn then assistant turn; returns `assistant_message_id`
  - `_log_spend(user_id: str, response: dict) → None` — calls `spend_service.create_spend` for LLM call (`gpt-4o`, `input_tokens`, `output_tokens`, endpoint=`/api/chat/messages`) and separately for embedding (`text-embedding-3-small`, embedding token count); calls `spend_service.spend_email_alert(current_cost=spend_log.estimated_cost_usd)` after each
- [x] Update `chat/controller.py` — inject `ChatSessionService` via `Depends()` in addition to `ChatRequestHandler`; controller resolves session before delegating:
  - `POST /api/chat/messages`: call `chat_session_service.get_active_session(user.id)` → if None call `chat_session_service.create_session(user.id)` to get `session_id`; pass `session_id` to `request_handler.handle_chat_message(user.id, session_id, message)`
  - `GET /api/chat/messages`: call `chat_session_service.get_active_session(user.id)` → if None create one; call `request_handler.list_messages(session_id)`; return `{ session_id, messages }` shape
  - `POST /api/chat/sessions` (Clear Chat): call `chat_session_service.get_active_session(user.id)` → if found call `chat_session_service.update_session_status(session_id, False)`; call `chat_session_service.create_session(user.id)` → return `{ "success": true, "data": { "session_id": new_session.id }, "error": null }`; messages from old session retained in DB — never deleted
- [x] Create `feedback/service.py` — `FeedbackService(feedback_dao: IFeedbackDAO)`:
  - `get_by_message_id(message_id: str) → Feedback | None` — calls `feedback_dao.get_by_message_id(message_id)`
  - `create_feedback(message_id: str, user_id: str, rating: str) → Feedback` — calls `feedback_dao.create(message_id, user_id, rating)`
  - `update_feedback(feedback_id: str, rating: str) → Feedback` — calls `feedback_dao.update(feedback_id, rating)`
  - `delete_feedback(feedback_id: str) → None` — calls `feedback_dao.delete_by_id(feedback_id)`
  - `submit_feedback(user_id: str, message_id: str, rating: str | None) → None` — orchestrates create/update/delete: call `get_by_message_id(message_id)` to get existing feedback; if `rating` is None → call `delete_feedback(existing.id)` if exists, else no-op; if `rating` is non-null and no existing → call `create_feedback`; if `rating` is non-null and existing → call `update_feedback(existing.id, rating)`; emits Phoenix OTEL span with `message_id`, `user_id`, `rating`
- [x] Create `feedback/controller.py` — `POST /api/feedback`; request body Pydantic model: `{ data: { message_id: str, rating: Literal["up", "down"] | None } }`; validate `message_id` is a valid UUID format → return 422 if invalid; inject `ChatService` via `Depends()` to verify ownership — call `chat_service.get_message_by_id(message_id)` → if None or `message.user_id != user.id` raise `HTTPException(404)`; call `feedback_service.submit_feedback(user.id, message_id, rating)`; return `{ "success": true, "data": null, "error": null }`; route uses `Depends(require_scope(Scope.APP))`; wire `FeedbackService` and `ChatService` via FastAPI `Depends()` chain
- [x] Verify: `curl -X POST .../api/chat/sessions` with valid JWT → `{ "success": true, "data": { "session_id": "..." } }`
- [x] Verify: `curl -X POST .../api/feedback` with `{ "data": { "message_id": "<id>", "rating": "up" } }` → `{ "success": true, "data": null }`
- [x] Verify: re-submit same `message_id` with `rating: "down"` → rating updated in DB; re-submit with `rating: null` → feedback row deleted

> **PAUSE — Show lead updated and new files. Wait for approval before continuing.**

### Frontend Agent
- [x] Add `feedbacks: {}` to Alpine.js state in `static/js/main.js` — map of `message_id → 'up' | 'down' | null`; tracks current rating per AI message; used to show active/inactive state on thumbs buttons
- [x] Add thumbs up / thumbs down buttons to AI message bubble in `templates/chat.html` — rendered below each assistant message (not user messages); bound to `feedbacks[message.id]` for active state styling; clicking an already-active button sets rating to null (deselect); Phase 1c stub: `submitFeedback(message_id, rating)` method updates `feedbacks` map in local state only — API call wired in Phase 2
- [x] Verify: hardcoded assistant message in state shows thumbs up/down buttons; clicking up highlights it; clicking again deselects; clicking down switches highlight

> **PAUSE — Show lead in browser. Wait for approval before continuing.**

### Integration Agent
- [x] Load `session_id` from `GET /api/chat/messages` response and store in Alpine state as `sessionId`; pass `session_id` in `POST /api/chat/messages` request body
- [x] Wire thumbs up/down buttons to `POST /api/feedback` — on click: call `submitFeedback(message_id, rating)` which posts `{ data: { message_id, rating } }`; on success: update `feedbacks[message_id]` in Alpine state; on error: show brief error toast; clicking already-active button sends `rating: null` to deselect
- [ ] Verify: click thumbs up on an AI response → button highlights, `POST /api/feedback` returns 200; click again → deselects, `POST /api/feedback` with `rating: null` returns 200; refresh page → feedback state not persisted client-side (by design — no persistence in V1)

> **PAUSE — Show lead end-to-end flow. Wait for approval.**

---

## Prerequisites (Lead to complete before agents start)
- [x] Create Google Cloud Console project + enable OAuth → get Client ID + Secret
- [x] Get OpenAI API key
- [x] Fill in `.env.local` with all values
- [x] Gmail App Password → add `SMTP_PASSWORD` to `.env.local`
- [x] Provide `docker-compose.yml` with all 4 services
