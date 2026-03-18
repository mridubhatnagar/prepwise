# Architecture Decisions

## GET /api/auth/me

**Why added:**
- Chat page needs user profile (name, avatar) to populate the app bar
- Alpine.js state does not persist across page refreshes — hardcoded values would reappear
- Considered alternatives:
  - Jinja2 template injection — old-school, mixes server-side rendering with client-side state
  - `sessionStorage` — stores PII (email) client-side, vulnerable to XSS exfiltration
  - `window.__user` script tag — same XSS risk as sessionStorage
- `GET /api/auth/me` is the cleanest solution — no PII stored client-side, protected by `get_current_user`, trivial to implement

**Rule:** No user PII stored in sessionStorage, localStorage, or injected into the DOM. Fetch from API on init instead.

---

## OAuth State Parameter (CSRF Protection)

**Why added:**
- The `/auth/callback` endpoint is public — no cookie, no authentication
- Without a state parameter, an attacker can trick an invited user into visiting `/auth/callback?code=ATTACKER_CODE`, logging them into the attacker's Google account
- The `allowed_users` whitelist reduces practical risk (attacker must also be an invited user) but does not eliminate the attack vector
- CSRF protection is standard practice in all major frameworks (Django, Flask-WTF, Rails) — skipping it for low-risk scenarios sets a bad precedent
- Implementation cost: server-side only — no frontend JS required for state management

**How it works:**
- On Sign-In click: browser navigates to `GET /api/auth/initiate` (window.location.href)
- Backend generates a random nonce, stores it in an HttpOnly cookie (`oauth_state`, SameSite=Lax, max_age=300), embeds it as `state=` param in the Google redirect URL
- Google echoes it back to `GET /auth/callback?code=...&state=...`
- Backend verifies returned `state` matches the `oauth_state` cookie → clears cookie immediately → proceeds with code exchange
- No frontend JS involved in state management — fully server-side

**Rule:** Always include state parameter in OAuth flows regardless of perceived risk level.

---

## Send Button Cooldown — 503 (5 seconds)

**Why:**
- On service errors (OpenAI, Weaviate, DB down), an immediate retry will just fail again — the upstream service needs time to recover
- 5 seconds is enough to discourage a knee-jerk retry without being frustrating
- No retry button shown — user retries manually when ready

**Rule:** Disable Send button for 5 seconds after any 503 response. Display the `detail` field from the response as the error message.

---

## Send Button Cooldown — 429 (60 seconds with countdown)

**Why:**
- Rate limit is `CHAT_RATE_LIMIT` requests per minute (default 5/min) — keyed by `user_id`
- Unlike 503 (service failure), 429 means the server is actively rejecting the request — retrying sooner than the rate limit window resets is pointless
- A countdown timer gives the user clear, honest feedback on when they can retry, rather than a vague "wait a moment" message
- Considered 5 seconds (same as 503) — rejected because it doesn't reflect the actual rate limit window and the user would just hit 429 again immediately

**Rule:** On 429, disable Send button for 60 seconds with a visible countdown timer. Display `"You're sending messages too fast. Please wait a moment."`
