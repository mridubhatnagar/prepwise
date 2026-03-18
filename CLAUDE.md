# CLAUDE.md

## Project Overview
This project is a **Technical Interview Prep Knowledgebase Chat**.  
Purpose: Help users **brush up their tech knowledge before interviews** by querying a curated set of documents.  

The project consists of:  
- Frontend Agent: Generates Alpine.js UI from Figma/Uizard mockups.  
- Backend Agent: Handles document ingestion, chunking, vector DB storage, and provides FastAPI endpoints for chat queries.

---

## Coding Guidelines

1. Object-Oriented Programming (OOP)  
   - Use classes for all logical components.  
   - Keep code modular and reusable.  

2. Database Access Layer
   - Each DAO must have a corresponding interface (ABC) defined in the same file (e.g. `IUserDAO`, `IChatMessageDAO`, `IDocumentDAO`).
   - The interface declares abstract methods; the DAO class implements them.
   - DAOs import `SessionLocal` (or `weaviate_client`) from `infra` and create `self.db = SessionLocal()` in `__init__`; session closed in `__del__`.
   - DAO method names are generic: `create`, `list`, `get_*`, `clear` — the class name provides context.
   - Controllers / API endpoints must not directly call the database.

3. Service Layer
   - Implement a service layer to handle business logic.
   - Services accept the DAO interface in `__init__` — never instantiate the DAO internally: `def __init__(self, chat_message_dao: IChatMessageDAO)`.
   - Service method names are descriptive: `create_message`, `list_messages`, `clear_messages` — they call the corresponding generic DAO method internally.
   - Services are wired via FastAPI `Depends()` dependency injection — DAOs are injected into services, services into handlers/controllers.

4. Controllers / API
   - Should only call the service layer or request handler — never instantiate services or DAOs directly.
   - Responsible for request validation, response formatting, and routing.
   - Use Pydantic `BaseModel` for all API request and response schemas.

5. Environment Variables
   - Store all environment variables in a separate `.env` file.
   - Access variables in a `Config` class as class-level attributes using `os.environ.get(...)`.
   - All project components access configuration values through the `config` singleton — never call `os.environ` directly.

6. Code Quality
   - Follow PEP 8 guidelines for Python Code
   - Keep functions and classes small and focused.  
   - Use clear variable and method names.  
   - Add docstrings to non-trivial methods and any method whose purpose isn't immediately clear from its name and type hints. Skip docstrings where the name and signature are self-explanatory.
   - Do not add comments that merely restate what the code is doing. Only comment where the reasoning or intent is not immediately obvious from reading the code.
   - Do not use banner-style section separator comments (e.g. `# --- Section Name ---`). These are not production-grade and add no value.

7. Logging
   - Use Python's standard `logging` module throughout the backend.
   - Log at appropriate levels: `logger.info` for notable events (user allowed, chat cleared), `logger.warning` for rejected or unexpected inputs (auth failures, token mismatches, blocked requests), `logger.error` for exceptions and unexpected failures.
   - Prioritize logging at decision points that aid RCA: auth rejections (with email), context limit hits, confidence threshold outcomes, external API failures, and any redirect or early-return path.

---

## Agents

**Frontend Agent**  
- Generate UI code in Alpine.js based on Figma/Uizard mockups.  
- Create collapsible sidebar (read-only) showing document list.  
- Create chat window with AI/user messages.  
- Input box with Send button only; Clear Chat button lives inside context limit banner.  
- Build UI with hardcoded placeholder data. API calls are wired at integration stage.
- Follow CLAUDE.md styling guidelines.  
- Suggestions must be approved manually.  

**Backend Agent**  
- Ingest raw documents and chunk them.  
- Store embeddings in vector DB.  
- Implement FastAPI endpoints for chat + RAG query according to the plan file.
- Follow CLAUDE.md coding guidelines.  
- Suggestions must be approved manually.  

---

## Project Folder Structure (V1)

project_root/
├── app.py                      # FastAPI entry, router registration, page routes
├── config.py                   # Config class reading os.environ
├── constants.py                # Hardcoded business constants — OpenAI token pricing, Google OAuth URLs
├── enums.py                    # Shared enums: MessageRole, Scope
├── exceptions.py               # Custom app exceptions: DatabaseError, EmbeddingError, RetrievalError, LLMError, OAuthError
├── dependencies.py             # get_current_user FastAPI dependency (used across all protected routes)
├── auth/
│   ├── __init__.py
│   ├── models.py               # User, AllowedUser, AccessAttempt (SQLAlchemy ORM)
│   ├── scopes.py               # require_scope dependency (Scope enum lives in enums.py)
│   ├── utils.py                # generate_jwt_token(user_id, scopes) — JWT generation only
│   ├── controller.py           # Google OAuth endpoints + GET /api/auth/me
│   ├── service.py              # UserService, AllowedUserService, AccessAttemptService, AuthService
│   └── dao.py                  # IUserDAO + UserDAO, IAllowedUserDAO + AllowedUserDAO, IAccessAttemptDAO + AccessAttemptDAO
├── chat/
│   ├── __init__.py
│   ├── models.py               # ChatSession, ChatMessage (SQLAlchemy ORM)
│   ├── controller.py           # POST /api/chat/messages, GET /api/chat/messages, POST /api/chat/sessions
│   ├── request_handler.py      # ChatRequestHandler — handle_chat_message, list_messages
│   ├── service.py              # ChatService, ChatSessionService
│   └── dao.py                  # IChatMessageDAO + ChatMessageDAO, IChatSessionDAO + ChatSessionDAO
├── rag/
│   ├── __init__.py
│   ├── orchestrator.py         # RAGOrchestrator — retrieve_chunks, is_confident, build_response
│   ├── retrieval_client.py     # RetrievalClient — generate_embedding, search, retrieve
│   └── llm_client.py           # LLMClient — build_prompt, generate_response
├── spend/
│   ├── __init__.py
│   ├── models.py               # SpendLog (SQLAlchemy ORM)
│   ├── dao.py                  # ISpendDAO (ABC) + SpendDAO — create, get_total(date)
│   └── service.py              # SpendService — create_spend, get_total_spend, spend_email_alert
├── documents/
│   ├── __init__.py
│   ├── controller.py           # GET /api/documents
│   ├── service.py              # DocumentService — list_documents_by_categories
│   ├── models.py               # Document Pydantic model
│   └── dao.py                  # IDocumentDAO (ABC) + DocumentDAO — list
├── feedback/
│   ├── __init__.py
│   ├── models.py               # Feedback (SQLAlchemy ORM)
│   ├── controller.py           # POST /api/feedback
│   ├── service.py              # FeedbackService — submit_feedback
│   └── dao.py                  # IFeedbackDAO (ABC) + FeedbackDAO — create, update, delete_by_id, get_by_id, get_by_message_id
├── infra/
│   ├── __init__.py
│   ├── postgres.py             # SQLAlchemy engine, SessionLocal, Base, get_db dependency
│   └── weaviate.py             # Weaviate client
├── templates/
│   ├── landing.html            # Landing + Sign-In page
│   └── chat.html               # Chat interface
├── static/
│   ├── js/main.js              # Alpine.js app init + global state
│   ├── components/             # Alpine.js reusable components
│   └── img/                    # Static images (favicon.svg, Lost.gif)
├── scripts/
│   └── ingest.py               # One-time doc ingestion into Weaviate
├── migrations/                 # Alembic migration files
├── docs/                       # Raw KB documents
├── .env.local                  # Local dev secrets — never committed
├── .env.prod                   # Production secrets — never committed
├── .env.example                # All keys with empty values — committed
└── CLAUDE.md                   # Project guidelines

---

## Required Reading (Agents — do this first)

Before writing any code, read these five files in full:
- `.claude/plan.md` — tech design: problem, solution, key decisions, RAG pipeline, OAuth flow, folder structure, Alpine.js state contract
- `.claude/arch.md` — class-level architecture: every class, its methods, and responsibilities
- `.claude/schema.md` — PostgreSQL table definitions and Weaviate schema
- `.claude/api_contracts.md` — all API endpoint contracts, request/response shapes, auth conventions
- `.claude/todo.md` — your task list: find your phase, work only your section, stop at each approval gate

---

## Workflow Rules (V1)

- Frontend and backend agents can run independently using **mock API data** defined in plan files.
- Keep implementation minimal, safe, and aligned with project guidelines.

### Todo Tracking (IMPORTANT)
- After completing each task, mark it as done in `.claude/todo.md` by changing `- [ ]` to `- [x]`
- Do this immediately after completing the task, before moving to the next one
- Do not mark a task done until it is fully implemented and verified locally

### Approval Gates (IMPORTANT)
- Each phase is divided into sections. After completing each section, the agent **must stop and wait for explicit lead approval** before proceeding to the next section.
- Do not proceed to the next section on your own — even if it seems like a natural continuation.
- When stopping at a gate, clearly state:
  1. What was completed in this section
  2. What files were created or modified
  3. What the lead should verify before approving
- Only continue after the lead responds with explicit approval (e.g. "looks good", "proceed", "yes").
- If anything is unclear or a decision is needed mid-section, stop and ask — do not make assumptions.


## Tech Stack

**Frontend:**  
- HTML + Alpine.js (minimal, no React)  
- Bootstrap 5 for styling

**Backend:**
- Python 3.x
- FastAPI for API endpoints
- SQLAlchemy ORM + Alembic for PostgreSQL
- Service layer + Database classes for OOP structure

**Database / Storage:**
- PostgreSQL (relational) via SQLAlchemy ORM
- Weaviate (vector database) for embeddings and hybrid search
- Local storage for raw documents

**Environment & Config:**  
- .env file for all environment variables  
- Config class accessing os.environ  

**Other Tools:**  
- Claude Code for AI-assisted coding  
- Figma / Uizard for UI mockups  