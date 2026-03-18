# PrepIt — Class Architecture Reference

---

## Exception Handling

### `rag/retrieval_client.py` — `RetrievalClient`
- `generate_embedding()` — catch `openai.APIError`, `openai.APITimeoutError`, `openai.RateLimitError` → log `logger.error` → raise `EmbeddingError`
- `search()` — catch `weaviate.exceptions.WeaviateConnectionError`, `weaviate.exceptions.WeaviateQueryError`, `weaviate.exceptions.WeaviateTimeoutError`, `weaviate.exceptions.UnexpectedStatusCodeError` → log `logger.error` → raise `RetrievalError`
- Do NOT mix OpenAI and Weaviate exceptions — each method catches only its own client's exceptions
- No backend retry

### `rag/llm_client.py` — `LLMClient`
- `generate_response()` — catch `openai.APIError`, `openai.APITimeoutError`, `openai.RateLimitError`, and JSON parse failures → log `logger.error` → raise `LLMError`
- No backend retry

### DAOs (Postgres)
- All DB calls — catch `sqlalchemy.exc.OperationalError`, `sqlalchemy.exc.IntegrityError`, `sqlalchemy.exc.DatabaseError` → log `logger.error` with full SQLAlchemy exception details → raise `DatabaseError`
- SQLAlchemy connection pool handles reconnects automatically; `OperationalError` is caught if pool retries are exhausted

### Controllers
- Catch `EmbeddingError`, `RetrievalError` → raise `HTTPException(503, detail="Couldn't reach the knowledge base. Please try again in a moment.")`
- Catch `LLMError` → raise `HTTPException(503, detail="Couldn't generate a response. Please try again.")`
- Catch `DatabaseError` → raise `HTTPException(503, detail="Something went wrong. Please try again.")`

### `auth/service.py` — `AuthService.fetch_oauth_user_info`
- State mismatch (CSRF check fails) → log `logger.warning` → raise `OAuthError`
- Google token endpoint failure (network error, invalid/expired code) → log `logger.error` → raise `OAuthError`
- Single `OAuthError` covers both — controller handles both the same way
- Controller catches `OAuthError` → redirects to `/?error=auth_failed`

### `spend/service.py` — `SpendService.spend_email_alert`
- Catch `smtplib.SMTPException` → log `logger.error` → return silently
- smtp failure must not affect the chat response or roll back the spend log
- `create_spend()` and the email alert are independent — failure in one does not affect the other

### `dependencies.py` — `get_current_user`
- JWT missing, invalid signature, or expired → catch `jwt.ExpiredSignatureError`, `jwt.InvalidTokenError` → raise `HTTPException(401, detail="Invalid or expired token")`
- `user_id` not found in DB → raise `HTTPException(401, detail="User not found")`
- Raises `HTTPException(401)` directly — `get_current_user` is a FastAPI dependency and is HTTP-aware by design

### `exceptions.py` (project root)
- Defines all custom app exceptions: `DatabaseError`, `EmbeddingError`, `RetrievalError`, `LLMError`, `OAuthError`
- Library exceptions (`sqlalchemy.exc.*`, `openai.*`, `weaviate.exceptions.*`) never leak past the layer that catches them

### Frontend — Send button
- On 503 response: disable Send button for 5 seconds, display the `detail` field as the error message
- On 429 response: disable Send button for 60 seconds with a countdown timer, display `"You're sending messages too fast. Please wait a moment."`

---

## `auth/`

### `auth/models.py`

```python
class User(Base):
    id: UUID (PK)
    google_auth_id: str (unique, not null)
    email: str (not null)
    name: str (nullable)
    avatar_url: str (nullable)
    created_at: datetime (default now)

class AllowedUser(Base):
    id: UUID (PK)
    email: str (unique, not null)
    scope: str (not null)        # "app" or "app,docs"
    added_at: datetime (default now)

class AccessAttempt(Base):
    id: UUID (PK)
    email: str (not null)
    attempted_at: datetime (default now)
```

### `auth/dao.py`

```python
class IUserDAO(ABC):
    @abstractmethod
    def create(self, google_auth_id: str, email: str, name: str, avatar_url: str) -> User: ...
    @abstractmethod
    def update(self, user_id: str, name: str, avatar_url: str) -> User: ...
    @abstractmethod
    def get_by_auth_id(self, google_auth_id: str) -> User | None: ...
    @abstractmethod
    def get_by_id(self, user_id: str) -> User | None: ...

class UserDAO(IUserDAO):
    def __init__(self):
        self.db = SessionLocal()
    def __del__(self):
        self.db.close()


class IAllowedUserDAO(ABC):
    @abstractmethod
    def is_allowed(self, email: str) -> AllowedUser | None: ...

class AllowedUserDAO(IAllowedUserDAO):
    def __init__(self):
        self.db = SessionLocal()
    def __del__(self):
        self.db.close()


class IAccessAttemptDAO(ABC):
    @abstractmethod
    def create(self, email: str) -> None: ...

class AccessAttemptDAO(IAccessAttemptDAO):
    def __init__(self):
        self.db = SessionLocal()
    def __del__(self):
        self.db.close()
```

### `auth/utils.py`

```python
def generate_jwt_token(user_id: str, scopes: list[str]) -> str:
    # builds payload: { user_id, scopes, exp }
    # signs with JWT_SECRET, algorithm HS256
    # returns token string
```

### `auth/service.py`

```python
class UserService:
    def __init__(self, user_dao: IUserDAO):
        self.user_dao = user_dao

    def get_user_by_auth_id(self, google_auth_id: str) -> User | None: ...
    def get_user_by_id(self, user_id: str) -> User | None: ...
    def create_user(self, google_auth_id: str, email: str, name: str, avatar_url: str) -> User: ...
    def update_user(self, user_id: str, name: str, avatar_url: str) -> User: ...


class AllowedUserService:
    def __init__(self, allowed_user_dao: IAllowedUserDAO):
        self.allowed_user_dao = allowed_user_dao

    def is_user_allowed(self, email: str) -> AllowedUser | None:
        # calls self.allowed_user_dao.is_allowed(email)


class AccessAttemptService:
    def __init__(self, access_attempt_dao: IAccessAttemptDAO):
        self.access_attempt_dao = access_attempt_dao

    def create_user_access_attempt(self, email: str) -> None:
        # calls self.access_attempt_dao.create(email)


class AuthService:
    def __init__(
        self,
        user_service: UserService,
        allowed_user_service: AllowedUserService,
        access_attempt_service: AccessAttemptService,
    ):
        self.user_service = user_service
        self.allowed_user_service = allowed_user_service
        self.access_attempt_service = access_attempt_service

    def prepare_oauth_redirect(self) -> tuple[str, str]: ...
    def fetch_oauth_user_info(self, code: str, state: str, stored_state: str) -> dict: ...
    def handle_oauth_callback(self, code: str, state: str, stored_state: str) -> tuple[User, str]:
        # fetch_oauth_user_info()
        # allowed_user_service.is_user_allowed() → access_attempt_service.create_user_access_attempt() + raise if not allowed
        # user_service.get_user_by_auth_id() → if None: create_user() → if found: update_user() if changed
        # generate_jwt_token()
        # returns (user, token)
```

### `auth/scopes.py`

```python
# Scope imported from enums.py
# get_current_user imported from dependencies.py

def require_scope(scope: Scope) -> Callable:
    def dependency(user = Depends(get_current_user)):
        if scope not in user.scopes:
            raise HTTPException(status_code=403)
        return user
    return dependency
```

---

## `chat/`

### `chat/models.py`

```python
class ChatSession(Base):
    id: UUID (PK)
    user_id: UUID (FK → users.id, ON DELETE CASCADE)
    is_active: bool (not null, default True)
    created_at: datetime (default now)

class ChatMessage(Base):
    id: UUID (PK)
    user_id: UUID (FK → users.id, ON DELETE CASCADE)
    session_id: UUID (FK → chat_sessions.id, ON DELETE CASCADE)
    role: Enum(MessageRole) (not null)      # imported from enums.py
    content: str (not null)
    citations: JSON (nullable)              # assistant only
    follow_up_questions: JSON (nullable)    # assistant only
    message_index: int (not null)           # sequential counter per user
    token_count: int (not null, default 0)
    created_at: datetime (default now)
```

### `chat/dao.py`

```python
class IChatMessageDAO(ABC):
    @abstractmethod
    def create(self, session_id: str, user_id: str, role: MessageRole, content: str, token_count: int, citations: list | None, follow_up_questions: list | None) -> ChatMessage: ...
    @abstractmethod
    def list(self, user_id: str, limit: int = None) -> list[ChatMessage]: ...
    @abstractmethod
    def list_by_session_id(self, session_id: str) -> list[ChatMessage]: ...
    @abstractmethod
    def get_current_context_details(self, session_id: str) -> dict: ...
    @abstractmethod
    def get_by_id(self, message_id: str) -> ChatMessage | None: ...

class ChatMessageDAO(IChatMessageDAO):
    def __init__(self):
        self.db = SessionLocal()
    def __del__(self):
        self.db.close()


class IChatSessionDAO(ABC):
    @abstractmethod
    def create(self, user_id: str) -> ChatSession: ...
    @abstractmethod
    def get_active(self, user_id: str) -> ChatSession | None: ...
    @abstractmethod
    def update_status(self, session_id: str, is_active: bool) -> None: ...

class ChatSessionDAO(IChatSessionDAO):
    def __init__(self):
        self.db = SessionLocal()
    def __del__(self):
        self.db.close()
```

### `chat/service.py`

```python
class ChatService:
    def __init__(self, chat_message_dao: IChatMessageDAO):
        self.chat_message_dao = chat_message_dao

    def get_chat_context_details(self, session_id: str) -> dict:
        # calls self.chat_message_dao.get_current_context_details(session_id)

    def list_chat_messages(self, user_id: str, limit: int = None) -> list[ChatMessage]:
        # calls self.chat_message_dao.list(user_id, limit)

    def list_chat_messages_by_session(self, session_id: str) -> list[ChatMessage]:
        # calls self.chat_message_dao.list_by_session_id(session_id)

    def create_chat_message(self, session_id: str, user_id: str, role: MessageRole, content: str, token_count: int, citations: list | None = None, follow_up_questions: list | None = None) -> ChatMessage:
        # calls self.chat_message_dao.create(...)

    def get_message_by_id(self, message_id: str) -> ChatMessage | None:
        # calls self.chat_message_dao.get_by_id(message_id)


class ChatSessionService:
    def __init__(self, chat_session_dao: IChatSessionDAO):
        self.chat_session_dao = chat_session_dao

    def get_active_session(self, user_id: str) -> ChatSession | None:
        # calls self.chat_session_dao.get_active(user_id)

    def create_session(self, user_id: str) -> ChatSession:
        # calls self.chat_session_dao.create(user_id)
        # returns new session

    def update_session_status(self, session_id: str, is_active: bool) -> None:
        # calls self.chat_session_dao.update_status(session_id, is_active)
```

### `chat/request_handler.py`

```python
class ChatRequestHandler:
    def __init__(
        self,
        chat_service: ChatService,
        rag_orchestrator: RAGOrchestrator,
        spend_service: SpendService,
    ):
        self.chat_service = chat_service
        self.rag_orchestrator = rag_orchestrator
        self.spend_service = spend_service

    def handle_chat_message(self, user_id: str, session_id: str, query: str) -> dict:
        # calls _check_context, _get_history, _generate_response, _persist, _log_spend

    def list_messages(self, session_id: str) -> list[ChatMessage]:
        # calls chat_service.list_chat_messages_by_session(session_id)

    def _check_context(self, session_id: str) -> dict:
        # calls chat_service.get_chat_context_details(session_id)

    def _get_history(self, session_id: str) -> list[ChatMessage]:
        # calls chat_service.list_chat_messages_by_session(session_id, limit=LLM_HISTORY_WINDOW)

    def _generate_response(self, query: str, history: list[ChatMessage]) -> dict:
        # calls rag_orchestrator.retrieve_chunks()
        # calls rag_orchestrator.is_confident()
        # calls rag_orchestrator.build_response()
        # returns { answer, citations, follow_up_questions, input_tokens, output_tokens }

    def _persist(self, user_id: str, session_id: str, query: str, response: dict) -> None:
        # calls chat_service.create_chat_message() twice — user message + assistant response

    def _log_spend(self, user_id: str, response: dict) -> None:
        # calls spend_service.create_spend() → returns SpendLog
        # calls spend_service.spend_email_alert(current_cost=spend_log.estimated_cost_usd)
```

---

## `rag/`

> **Note:** `rag/` has no DAOs and no database access. `RetrievalClient` and `LLMClient` call external APIs directly (Weaviate and OpenAI). Do not create DAO classes for this module.

### `rag/retrieval_client.py`

```python
class RetrievalClient:
    def generate_embedding(self, query: str) -> list[float]:
        # calls OpenAI text-embedding-3-small API
        # returns embedding vector

    def search(self, query: str, embedding: list[float]) -> list[dict]:
        # calls Weaviate hybrid search (BM25 + cosine, alpha=0.5, top_k=5)
        # returns list of chunks: [{ content, source_doc, section_title, category, score }]

    def retrieve(self, query: str) -> list[dict]:
        # calls self.generate_embedding()
        # calls self.search()
        # returns chunks
```

### `rag/llm_client.py`

```python
class LLMClient:
    def build_prompt(self, query: str, chunks: list[dict], history: list[ChatMessage]) -> list[dict]:
        # builds system prompt with role, question type classification, response structure rules
        # injects KB chunks as context
        # appends chat history
        # returns OpenAI messages format: [{ role, content }, ...]

    def generate_response(self, messages: list[dict]) -> dict:
        # calls GPT-4o with response_format (JSON schema)
        # returns { answer, citations, follow_up_questions, input_tokens, output_tokens }
```

### `rag/orchestrator.py`

```python
class RAGOrchestrator:
    def __init__(
        self,
        retrieval_client: RetrievalClient,
        llm_client: LLMClient,
    ):
        self.retrieval_client = retrieval_client
        self.llm_client = llm_client

    def retrieve_chunks(self, query: str) -> list[dict]:
        # calls self.retrieval_client.retrieve(query)
        # returns chunks with scores

    def is_confident(self, chunks: list[dict]) -> bool:
        # checks max_score >= RETRIEVAL_CONFIDENCE_THRESHOLD (0.55)
        # returns True or False

    def build_response(self, query: str, chunks: list[dict], history: list[ChatMessage]) -> dict:
        # prompt injection check — regex blocklist
        # calls self.llm_client.build_prompt(query, chunks, history)
        # calls self.llm_client.generate_response(messages)
        # output guardrail — strips citations not in retrieved chunks
        # returns { answer, citations, follow_up_questions, input_tokens, output_tokens }
```

---

## `spend/`

### `spend/models.py`

```python
class SpendLog(Base):
    id: UUID (PK)
    user_id: UUID (FK → users.id, ON DELETE SET NULL, nullable)
    model: str (not null)               # e.g. 'gpt-4o', 'text-embedding-3-small'
    input_tokens: int (not null, default 0)
    output_tokens: int (not null, default 0)
    estimated_cost_usd: Decimal (not null)
    endpoint: str (nullable)            # e.g. '/api/chat/messages'
    logged_at: datetime (default now)
```

### `spend/dao.py`

```python
class ISpendDAO(ABC):
    @abstractmethod
    def create(self, user_id: str | None, model: str, input_tokens: int, output_tokens: int, estimated_cost_usd: Decimal, endpoint: str | None) -> SpendLog: ...
    @abstractmethod
    def get_total_per_day(self, for_date: date) -> float: ...
    @abstractmethod
    def get_total(self) -> float: ...   # all-time cumulative total

class SpendDAO(ISpendDAO):
    def __init__(self):
        self.db = SessionLocal()
    def __del__(self):
        self.db.close()
```

### `spend/service.py`

```python
class SpendService:
    def __init__(self, spend_dao: ISpendDAO):
        self.spend_dao = spend_dao

    def create_spend(self, user_id: str | None, model: str, input_tokens: int, output_tokens: int, endpoint: str | None) -> SpendLog:
        # calculates estimated_cost_usd using constants.py pricing
        # calls self.spend_dao.create(...)

    def get_total_spend_per_day(self, for_date: date) -> float:
        # calls self.spend_dao.get_total_per_day(for_date)

    def get_total_spend(self) -> float:
        # calls self.spend_dao.get_total() — all-time cumulative

    def spend_email_alert(self, current_cost: Decimal) -> None:
        # calls self.get_total_spend() — all-time cumulative total
        # crossing-point check on cumulative total:
        #   previous_total = all_time_total - float(current_cost)
        #   if previous_total < threshold <= all_time_total → send alert email via smtplib
        # SMTP failures caught and logged silently
```

---

## `documents/`

### `documents/models.py`

```python
class Document(BaseModel):    # Pydantic — API response shape only, not SQLAlchemy
    name: str
    category: str
```

### `documents/dao.py`

```python
class IDocumentDAO(ABC):
    @abstractmethod
    def list(self) -> list[Document]: ...

class DocumentDAO(IDocumentDAO):
    def __init__(self):
        self.client = weaviate_client  # from infra
```

### `documents/service.py`

```python
class DocumentService:
    def __init__(self, document_dao: IDocumentDAO):
        self.document_dao = document_dao

    def list_documents_by_categories(self) -> dict[str, list[str]]:
        # calls self.document_dao.list()
        # groups by category in Python
        # returns { category: [doc_names] }
```

---

## `feedback/`

### `feedback/models.py`

```python
class Feedback(Base):
    id: UUID (PK)
    message_id: UUID (FK → chat_messages.id, ON DELETE CASCADE, unique, not null)
    user_id: UUID (FK → users.id, ON DELETE CASCADE, not null)
    rating: str (not null)    # "up" or "down"
    created_at: datetime (default now)
```

### `feedback/dao.py`

```python
class IFeedbackDAO(ABC):
    @abstractmethod
    def create(self, message_id: str, user_id: str, rating: str) -> Feedback: ...
    @abstractmethod
    def update(self, feedback_id: str, rating: str) -> Feedback: ...
    @abstractmethod
    def delete_by_id(self, feedback_id: str) -> None: ...
    @abstractmethod
    def get_by_id(self, feedback_id: str) -> Feedback | None: ...
    @abstractmethod
    def get_by_message_id(self, message_id: str) -> Feedback | None: ...

class FeedbackDAO(IFeedbackDAO):
    def __init__(self):
        self.db = SessionLocal()
    def __del__(self):
        self.db.close()
```

### `feedback/service.py`

```python
class FeedbackService:
    def __init__(self, feedback_dao: IFeedbackDAO):
        self.feedback_dao = feedback_dao

    def get_by_message_id(self, message_id: str) -> Feedback | None:
        # calls self.feedback_dao.get_by_message_id(message_id)

    def create_feedback(self, message_id: str, user_id: str, rating: str) -> Feedback:
        # calls self.feedback_dao.create(...)

    def update_feedback(self, feedback_id: str, rating: str) -> Feedback:
        # calls self.feedback_dao.update(feedback_id, rating)

    def delete_feedback(self, feedback_id: str) -> None:
        # calls self.feedback_dao.delete_by_id(feedback_id)

    def submit_feedback(self, user_id: str, message_id: str, rating: str | None) -> None:
        # emits Phoenix OTEL span with message_id, user_id, rating
```
