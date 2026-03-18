# API Contracts

### Scopes

```python
# enums.py
class Scope(str, Enum):
    APP = "app"    # access to chat + documents APIs
    DOCS = "docs"  # access to /docs (Swagger UI)

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
```

Scopes are stored in `allowed_users.scope` as a comma-separated string and included as a list in the JWT payload:
```json
{ "user_id": "...", "scopes": ["app"] }
{ "user_id": "...", "scopes": ["app", "docs"] }
```

Access is enforced via a `require_scope(Scope)` dependency defined in `auth/scopes.py`, which imports `get_current_user` from `dependencies.py`:
```python
# auth/scopes.py
from dependencies import get_current_user

def require_scope(scope: Scope):
    def dependency(user = Depends(get_current_user)):
        if scope not in user.scopes:
            raise HTTPException(status_code=403)
        return user
    return dependency
```

- All chat + document API routes → `Depends(require_scope(Scope.APP))`
- `/docs` → `Depends(require_scope(Scope.DOCS))`

### Auth convention
- `auth/utils.py` — `generate_jwt_token(user_id, scopes)`: JWT generation only; called by `auth/service.py` after successful OAuth
- `dependencies.py` — `get_current_user`: JWT decode + validation + DB lookup; called on every protected request:
  1. Reads JWT from `jwt` HttpOnly cookie in browser requests; reads from `Authorization: Bearer` header in curl/testing requests
  2. Decodes and verifies JWT signature + expiry
  3. Confirms `user_id` exists in `users` table
  4. Returns 401 if any check fails

### Pages
```
GET /
  Auth:    None (public)
  Returns: landing page HTML

GET /chat
  Auth:    require_scope(Scope.APP) → JWT valid + user exists + has APP scope → serve chat page HTML
           JWT missing, invalid, or user not found → redirect to /
           User exists but lacks APP scope → 403 error page
```

### Standard Response Structure
All API endpoints return a consistent envelope:
```json
// Success
{
  "success": true,
  "data": { ... },
  "error": null
}

// Error
{
  "success": false,
  "data": null,
  "error": "Human-readable error message"
}
```
- `data` is always a nested object keyed by resource name (e.g. `{ "user": { ... } }`, `{ "messages": [...] }`)
- Page routes (GET `/`, GET `/chat`) and redirect routes (GET `/auth/callback`, GET `/api/auth/initiate`) are exempt — they return HTML or 302 redirects, not JSON

### Health
```
GET /health
  Auth:    None (public)
  Returns: { "success": true, "data": { "status": "ok" }, "error": null }
```

### Auth
```
GET /auth/callback
  Auth:    None (public)
  Returns: No page rendered — fully server-side handled
           Backend reads ?code= and ?state= from query params
           → verifies state against HttpOnly oauth_state cookie
           → clears oauth_state cookie
           → exchanges code with Google
           → on success: set JWT cookie, redirect to /chat
           → on invite-only rejection: redirect to /?error=invite_only

GET /api/auth/initiate
  Auth:    None (pre-login)
  Returns: 302 RedirectResponse → Google consent URL (with state param embedded)
           Sets HttpOnly cookie: oauth_state (SameSite=Lax, max_age=300)

GET /api/auth/me
  Auth:    get_current_user
  Returns: {
    "success": true,
    "data": {
      "user": { "id": int, "name": string, "email": string, "avatar_url": string }
    },
    "error": null
  }
  Note:    Called by chat page on init to populate user state (name, avatar initials).
           No data stored client-side — avoids XSS exposure of PII.

POST /api/auth/logout
  Auth:    get_current_user
  Returns: { "success": true, "data": null, "error": null }
           Clears JWT cookie
```

### Chat
```
POST /api/chat/messages
  Auth:      require_scope(Scope.APP)
  Isolation: user_id always extracted from JWT payload — never from request body
  Body:    { "data": { "message": string, "session_id": string } }
  Validation:
    - data: required
    - data.message: required, non-empty, max 2000 chars
    - Validation errors return: { "success": false, "data": null, "error": "<reason>" }
  Returns: {
    "success": true,
    "data": {
      "message": {
        "answer": string,
        "assistant_message_id": string,
        "citations": [{ "doc_name": string, "section_title": string, "category": string }],
        "follow_up_questions": [string],
        "context_status": {
          "message_count": int,
          "token_count": int,
          "limit_reached": bool
        }
      }
    },
    "error": null
  }

GET /api/chat/messages
  Auth:      require_scope(Scope.APP)
  Isolation: user_id always extracted from JWT payload — returns only the requesting user's messages
  Returns messages for the active session only.
  Returns: {
    "success": true,
    "data": {
      "session_id": string,
      "messages": [
        {
          "id": string,
          "role": "user",
          "content": string,
          "created_at": string
        },
        {
          "id": string,
          "role": "assistant",
          "content": string,
          "citations": [{ "doc_name": string, "section_title": string, "category": string }],
          "follow_up_questions": [string],
          "created_at": string
        }
      ]
    },
    "error": null
  }

POST /api/chat/sessions
  Auth:      require_scope(Scope.APP)
  Isolation: user_id always extracted from JWT payload
  Sets previous active session is_active = false, creates new session.
  Returns: { "success": true, "data": { "session_id": string }, "error": null }
```

### Feedback
```
POST /api/feedback
  Auth:      require_scope(Scope.APP)
  Isolation: user_id always extracted from JWT payload
  Body:    { "data": { "message_id": string, "rating": "up" | "down" | null } }
           rating null = remove feedback (deselect)
  Validation:
    - message_id must belong to the authenticated user → 404 if not found
  Returns: { "success": true, "data": null, "error": null }
```

### Documents
```
GET /api/documents
  Auth:    require_scope(Scope.APP)
  Returns: {
    "success": true,
    "data": {
      "documents": { "category": ["doc_names"] }
    },
    "error": null
  }
  e.g. { "success": true, "data": { "documents": { "system_design": ["cap_theorem.md"], "database": ["indexing.md"] } }, "error": null }
  Source:  document_controller → document_service.list_documents_by_categories → document_dao.list
           Queries Weaviate for all KnowledgeChunk metadata, deduplicates in Python, groups by category
           Note: Weaviate has no native DISTINCT — fetch all chunk metadata and deduplicate in Python (acceptable for ~45 docs)
```
