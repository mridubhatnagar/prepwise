# Agent Checkpoints & Approval Gates

## Phase 0 — Design Approval Gate (Do First)

Before any backend/frontend implementation, generate three static HTML mockup files for design review:

### Screen 1: Landing + Sign-In (`mockups/landing.html`)
- Based on existing `design/landing_page.png`
- Left panel: brand badge — **"Revise, Refresh, Recall"** — headline — **"Revise smarter. Not harder."** — tagline + feature list + illustration
- Right panel: Replace email/password form with **Google Sign-In button** (official Google button style — white, rounded, Google logo + "Sign in with Google")
- Color palette: derive from existing mockup (soft blue/white theme)
- On rejection: `/auth/callback` redirects to `/` with an error param; landing page Alpine.js detects this param on init and shows a **flash message** (Bootstrap alert, top-center, auto-dismiss after 5s, manually dismissable)
  - `?error=invite_only` → "This platform allows invite-only access. Please reach out to the Admin."
  - `?error=unverified_email` → "Your Google account email is not verified. Please verify it and try again."
  - `?error=auth_failed` → "Sign in failed. Please try again." (state mismatch or Google API failure)
  - `?error=session_expired` → "Your session has expired. Please sign in again." (set by frontend on 401, not backend)
  - No retry prompt — Sign-In button remains available but message does not invite re-attempt

### Screen 3: Error Page (`mockups/error.html`)
- Full-page centered layout
- Same purple gradient background + decorative circles as landing page
- `static/img/Lost.gif` illustration (Storyset — Woman series)
- Badge showing error code: **"403 · Access Denied"** or **"404 · Page Not Found"**
- Headline: **"Looks like you're lost"**
- Message tailored to error type
- "Go to Home" button → `/`
- Attribution: "Woman illustrations by Storyset"
- Served by FastAPI exception handlers for 403 and 404

### Screen 2: Chat Interface (`mockups/chat.html`)
- Two-panel layout:
  - **Left sidebar** (collapsible): Document list grouped by category (System Design, Database, AI, DSA). Read-only. Toggle button to collapse/expand.
  - **Right panel**: Chat window
    - Top: App bar with logo + user avatar + Sign Out
    - Middle: Scrollable message thread (user bubbles right-aligned, AI bubbles left-aligned with citation chips below)
    - Bottom: Input bar with textarea + Send button
    - Context limit banner: shown when limit is reached — contains "Clear Chat" button
- Color palette: consistent with landing page

**Gate:** User approves all three mockups before agents start implementation.

---

## Manual Verification Checkpoints (per agent)

### After Database Agent
- Connect to PostgreSQL: `psql -U <user> -d prepit` → `\dt` shows all 4 tables: `users`, `chat_messages`, `allowed_users`, `access_attempts`
- Run `scripts/ingest.py` → output shows N docs processed, M chunks created
- Query Weaviate console (`http://localhost:8083/v1/objects`) → KnowledgeChunk objects present with metadata

### After Backend Agent
Curl commands to verify each endpoint:
```bash
# Health check
curl http://localhost:8000/health

# User profile
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/auth/me

# Documents list (with valid JWT)
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/documents

# Ask a question
curl -X POST http://localhost:8000/api/chat/messages \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is CAP theorem?"}'

# Scope guard
curl -X POST http://localhost:8000/api/chat/messages \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is React?"}'

# Clear chat
curl -X DELETE http://localhost:8000/api/chat/messages \
  -H "Authorization: Bearer <token>"
```
Verify: CAP theorem returns answer + citations + follow-ups. React returns "Sorry, this is beyond my current scope".
```bash
# Chat history
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/chat/messages

# Scope guard — docs-only JWT should be rejected
curl -X POST http://localhost:8000/api/chat/messages \
  -H "Authorization: Bearer <docs-only-token>" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is CAP theorem?"}'
# → 403 Forbidden
```
Verify: `GET /chat` with a `docs`-only JWT → 403 error page served (never reaches chat UI).

### After Frontend Agent
- Open `http://localhost:8000` → landing page renders with Google Sign-In button
- Open `http://localhost:8000/chat` without being logged in → redirected to `/`
- After login → redirected to `http://localhost:8000/chat` → chat interface loads with empty state visible (messages array empty, doc list empty — hardcoded data wired in Phase 2)
- Send button visible and clickable; Clear Chat button visible inside context limit banner; sidebar collapse works visually

### After Integration Agent
- Full flow: Google Sign-In → chat loads previous history → ask CAP theorem question → answer with citations appears → Phoenix trace visible at `http://localhost:6006`
- User name and avatar initials populate correctly in app bar from `GET /api/auth/me`
- Ask "What is React?" → "Sorry, this is beyond my current scope" message renders
- Click a suggestion chip → message sent, AI response renders, empty state replaced by messages area
- Click a follow-up pill → message sent, new AI response renders
- Context limit: after 20 messages, banner appears with Clear Chat button
- Click Clear Chat → conversation resets, empty state shown
- Sign in as `docs`-only user → navigate to `/chat` → 403 error page served

### User Data Isolation Test (Manual)
Requires two allowed users: User A and User B.

1. Sign in as User A → ask "What is CAP theorem?" → verify response appears
2. Sign in as User B (different browser/incognito) → ask "What is sharding?" → verify response appears
3. Open DevTools as User A → copy JWT cookie value
4. Use Postman or curl to call `GET /api/chat/messages` with User A's JWT
   → Response must contain only User A's messages (CAP theorem), not User B's
5. Call `POST /api/chat/messages` with User A's JWT but add `user_id: <user_B_id>` in request body
   → Backend must ignore the body's user_id, respond and save under User A only
6. Sign back in as User B → chat history must show only User B's messages (sharding)
   → User A's messages must never appear
