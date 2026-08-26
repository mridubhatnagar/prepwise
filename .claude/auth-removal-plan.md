# PrepIt — Auth Removal & Anonymous Access Plan (Draft, for review)

Status: **Draft — not yet merged into `.claude/plan.md`**

This proposes removing Google OAuth login and the invite-only allowlist, replacing per-user identity with a persistent anonymous cookie, adding bot protection to compensate for the accountability login used to provide, and adding a monthly cost-visibility API.

---

## Motivation

- Login (Google OAuth) and `AllowedUser` (invite-only allowlist) add friction for a personal-project tool that no longer needs controlled rollout.
- Removing both means the app becomes a fully open, unauthenticated surface in front of paid OpenAI calls — bot/abuse protection has to replace what login incidentally provided.

---

## Key Decisions

| Decision | Why |
|---|---|
| Replace `user_id` (FK to `users`) with `visitor_id` — a random opaque UUID | Keeps chat history scoping working without real identity. Same shape as today's FK columns, just no `users` table behind it. |
| Persistent cookie, not an ephemeral session cookie | A session-only cookie (expires on browser close) can't restore history across visits — defeats the purpose. Needs `HttpOnly`, `Secure`, `SameSite=Lax`, long `max-age` (~1 year). Survives browser close/reopen; does not survive clearing cookies, incognito, or a different browser/device. |
| Cookie is minted server-side only after a Turnstile check passes | If any request without prior verification could get a cookie, a bot just skips the landing page and calls the API directly. The mint step is the actual gate, not the button. |
| Landing page keeps a **Proceed** button as the verification trigger | Click → invisible Cloudflare Turnstile challenge runs → on success, backend mints `visitor_id` cookie → redirect to `/chat`. Gives the landing page a purpose again instead of collapsing it away. |
| Chat/document/feedback routes require the `visitor_id` cookie to exist | Requests without it (i.e. that skipped the Turnstile flow) get rejected — this is what makes the Proceed-button flow actually enforceable, not just cosmetic. |
| Rate limiting keys off `visitor_id` cookie, falls back to IP | Same mechanism as today's `_get_user_id_key`, just reading a plain cookie instead of decoding a JWT. Weaker than per-authenticated-user (cookie is resettable), so paired with the spend cap below. |
| Hard daily spend cap added to `spend/service.py` | Existing crossing-point email alert is notify-only. A bot that clears cookies/rotates IPs but stays under rate limits can still bleed cost slowly — a hard cap disables `/api/chat/messages` once the daily threshold is crossed, not just alerts. |
| `AllowedUser` and `AccessAttempt` dropped entirely | No invite-only concept remains once there's no real identity to check against. |
| `/docs` gated by HTTP Basic Auth, not JWT | `/docs` (Swagger UI) is a single internal route with no per-person identity need. Basic Auth needs a shared username/password in config, checked via FastAPI's `HTTPBasic` — no token issuance, no expiry/refresh logic, no cookie. JWT would mean rebuilding a mini version of the auth system this plan removes, just for one route. |
| New monthly cost API, gated by the same Basic Auth as `/docs` | Complements the hard spend cap with visibility into spend trends. Read-only and not tied to PII, but left ungated it becomes bait — a visible, real-time cost meter incentivizes cost-based griefing against the chat endpoint. Reuses the existing Basic Auth mechanism rather than adding a second one. |
| Cost API covers LLM + embedding spend only, server cost deferred | App is hosted on a single fixed AWS EC2 t3.small (no auto-scaling), so server cost barely varies month to month. Pulling it in would mean wiring AWS Cost Explorer API (separate IAM credentials, its own per-call cost, hours-to-a-day reporting lag) for a number that's effectively static. Deferred — can be added later (either a manual config constant or Cost Explorer integration) if infra stops being fixed-cost. |

---

## New Flow

```
1. GET /                         → landing page, "Proceed" button, Turnstile widget (invisible)
2. Click Proceed                 → Turnstile solves client-side, token sent to backend
3. POST /api/access/verify       → backend verifies Turnstile token with Cloudflare
                                    on success: mint visitor_id, set HttpOnly cookie, create
                                    zero-row placeholder (or defer to first chat_sessions insert)
4. Redirect → /chat              → chat routes now see the visitor_id cookie
5. POST /api/chat/messages, etc. → reject (401) if visitor_id cookie missing/invalid
                                    rate-limited per visitor_id, falls back to IP if absent
6. Daily spend cap check         → chat endpoint returns 503 if today's spend ≥ cap

Separately:
GET /docs                        → HTTP Basic Auth (shared password via config)
GET /api/spend/monthly           → HTTP Basic Auth (same credentials) — owner-only, unrelated
                                    to the visitor_id flow above
```

---

## New API: Monthly Cost

```
GET /api/spend/monthly
  Auth:    HTTP Basic Auth (same credentials as /docs)
  Returns: {
    "success": true,
    "data": {
      "currency": "USD",
      "note": "LLM and embedding API costs only — excludes server/infra costs.",
      "total": 152.12,
      "monthly_spend": [
        {
          "year": 2026,
          "months": [
            { "month": "March", "cost": 12.45 },
            { "month": "April", "cost": 28.90 },
            { "month": "May", "cost": 19.30 },
            { "month": "June", "cost": 34.60 },
            { "month": "July", "cost": 41.05 },
            { "month": "August", "cost": 15.82 }
          ]
        }
      ]
    },
    "error": null
  }
  Notes:
    - monthly_spend grouped by year (avoids repeating "year" per entry), months in
      chronological order within each year block
    - Series covers all months since the first spend_log row — no bounded window
    - Last entry (chronologically) is the current, still-accumulating month — no
      separate "running total for current month" field; it's just the last item
    - total = sum of cost across the full series (all-time)
    - Scope: LLM + embedding spend only (spend_logs), explicit via the "note" field —
      server/infra cost is a separate, deferred concern (see Key Decisions)
    - Source: new aggregation query in SpendDAO (GROUP BY year, month over
      spend_logs.created_at + estimated_cost_usd) — no new tracking needed, spend_logs
      already has a row per API call
```

---

## Schema Changes

| Table | Change |
|---|---|
| `users` | Dropped |
| `allowed_users` | Dropped |
| `access_attempts` | Dropped |
| `chat_sessions.user_id` | Renamed `visitor_id`, drop FK to `users` (no longer references a table — just an opaque UUID column, indexed) |
| `chat_messages.user_id` | Same — renamed `visitor_id`, FK dropped |
| `feedback.user_id` | Same — renamed `visitor_id`, FK dropped |
| `spend_logs.user_id` | Same — renamed `visitor_id`, FK dropped (was already nullable) |

New Alembic migration required for all of the above — this is a breaking schema change. **Decided: existing chat history is wiped on migration** (single-user app, no need to backfill/preserve `user_id`-scoped history under a real user).

---

## Files Affected

**Removed entirely**
- `auth/models.py` (`User`, `AllowedUser`, `AccessAttempt`)
- `auth/controller.py`, `auth/service.py`, `auth/dao.py`, `auth/utils.py`, `auth/scopes.py`
- `dependencies.py::get_current_user`, `AuthenticatedUser`

**New**
- `access/` module (name TBD) — Turnstile verification endpoint, `visitor_id` cookie minting, `require_visitor` dependency (replaces `require_scope`)
- `docs` gating — `HTTPBasic` dependency guarding the `/docs` route in `app.py`, checked against `config.DOCS_USERNAME` / `config.DOCS_PASSWORD`
- `GET /api/spend/monthly` — new controller endpoint in `spend/controller.py` (new file — spend currently has no controller), gated by the same `HTTPBasic` dependency, backed by a new `SpendDAO` aggregation method (e.g. `get_monthly_totals()`)
- Migration: drop `users`/`allowed_users`/`access_attempts`, rename `user_id` → `visitor_id` on the 4 remaining tables, drop their FKs

**Modified**
- `app.py` — `/chat` route guard switches from `get_current_user` to `require_visitor`; `/docs` route switches from `require_scope(Scope.DOCS)` to `HTTPBasic`
- `chat/controller.py`, `feedback/controller.py`, `documents/controller.py` — swap `require_scope(Scope.APP)` for `require_visitor`
- `chat/controller.py::_get_user_id_key` — read `visitor_id` cookie instead of decoding JWT
- `chat/dao.py`, `chat/models.py`, `chat/service.py`, `chat/request_handler.py` — rename `user_id` params/columns to `visitor_id` throughout
- `feedback/dao.py`, `feedback/service.py`, `feedback/controller.py` — same rename
- `spend/dao.py`, `spend/service.py`, `spend/models.py` — same rename; `spend/service.py` gains a hard-cap check and a monthly-totals method
- `config.py` / `.env*` — drop Google OAuth + JWT secret vars, add `TURNSTILE_SITE_KEY`, `TURNSTILE_SECRET_KEY`, `DAILY_SPEND_CAP_USD`, `DOCS_USERNAME`, `DOCS_PASSWORD`
- `templates/landing.html` — Sign-In button replaced with Proceed button + Turnstile widget script
- `templates/chat.html` — avatar/name/sign-out UI removed (no user identity to show)
- `static/js/main.js` — remove `/api/auth/me`, `/api/auth/logout` calls and `_redirectUnauthorized`'s auth-specific messaging; add Proceed-button handler

---

## Open Questions

1. ~~**Existing chat history** — wipe on migration, or is there a reason to preserve it?~~ Resolved: wipe (single-user app).
2. ~~**Turnstile failure UX** — what does the landing page show if Turnstile fails/times out? Retry button, or silent fallback?~~ Resolved: flash message + widget auto-reset so the user can immediately retry — confirmed adequate during real E2E testing.
3. ~~**Cap behavior** — when the daily spend cap trips, what does the user see (generic error vs. a specific "try again tomorrow" message)? Should mirror the existing context-limit-reached pattern in `chat/request_handler.py`.~~ Resolved: specific 503 message ("we've reached today's usage limit — try again tomorrow") through the existing generic error-banner path, no new frontend UI.

---

## Deferred (not in this pass)

- Guardrails AI / Llama Guard (already deferred to V2 per `guardrails.md`)
- Any notion of per-visitor spend accounting beyond the aggregate daily cap
- Server/infra cost in the monthly cost API (AWS Cost Explorer integration or a manual config constant, if instance sizing ever becomes variable)

---

## Todo List

Not started. Sequenced so nothing downstream depends on a not-yet-built upstream piece. Mark `- [x]` as each is completed and verified locally, per `CLAUDE.md` todo tracking rules.

### 1. Schema & migration
- [x] Write Alembic migration: drop `users`, `allowed_users`, `access_attempts` tables — `migrations/versions/d4f7c1a9b6e3_remove_auth_use_visitor_id.py`
- [x] Migration: rename `user_id` → `visitor_id` on `chat_sessions`, `chat_messages`, `feedback`, `spend_logs`; drop their FKs to `users` — same file
- [x] Migration wipes existing `chat_sessions`/`chat_messages`/`feedback` rows (decided: single-user app, no backfill needed) — same file, `TRUNCATE ... CASCADE`
- [ ] Run `alembic upgrade head` — **hold until Section 3/4 land** (ORM models still reference `user_id`/`users`; applying now breaks the running app)

### 2. Anonymous access (`access/` module) — done on branch `feat-anonymous-access` (pushed, not merged)
- [x] Add `TURNSTILE_SITE_KEY`, `TURNSTILE_SECRET_KEY` to `config.py` / `.env.example` (blank — real Cloudflare keys still needed)
- [x] Create `access/` module: Turnstile server-side verification call (`access/service.py::AccessService`, via `httpx`)
- [x] `POST /api/access/verify` endpoint — verify Turnstile token, mint `visitor_id`, set `HttpOnly`/`Secure`/`SameSite=Lax` cookie (~1yr `max-age`) — `access/controller.py`, rate-limited via `AUTH_RATE_LIMIT`
- [x] `require_visitor` dependency (replaces `require_scope`) — `access/dependencies.py`; built but **not yet wired into any route** (that's Section 3, stacked on this branch)
- [x] `templates/landing.html` — replace Sign-In button with Proceed button + Turnstile widget. Open Question 2 (failure UX) still not explicitly resolved — worth checking the implementation's error-callback behavior before merging
- [x] `static/js/main.js` — Proceed-button handler calling `/api/access/verify`, redirect to `/chat` on success

Section 1's migration (`d4f7c1a9b6e3_remove_auth_use_visitor_id.py`) was committed on this branch too, still unapplied. Known gap: subagent couldn't fully boot the app to verify (`jinja2` not installed in its shell despite being in `requirements.txt`) — worth a real boot-test before merging.

**Real end-to-end test performed 2026-08-25** (`docker compose` locally on the `feat-bot-protection` stack, which has Sections 1+2+3+4+5 together): found and fixed a real bug — `_renderTurnstile()` ran immediately on Alpine `init()`, racing the `async` Cloudflare script; `window.turnstile` was almost always still undefined, so the widget silently never rendered and clicking Proceed always failed client-side (never even reached `/api/access/verify`). Fixed using Cloudflare's documented `onload` callback pattern (`window._turnstileReady` promise, awaited in `init()` before rendering). Fix committed on `feat-bot-protection` (`cb863ff`) and cherry-picked onto `feat-anonymous-access` (`6ed1acf`) and `feat-remove-auth` (`45b7a48`) — all three pushed. This also resolves **Open Question 2**: the existing error-callback path (flash message "Verification failed. Please try again." + `turnstile.reset()` so the user can retry) is adequate now that the widget actually renders.

Full flow verified working: Proceed → Turnstile → cookie minted (`HttpOnly`, 1yr expiry, `Secure` correctly off on local plain-HTTP) → `/chat` → sidebar document list loads → real chat message round-trip confirmed by the user in-browser.

### 3. Remove auth module & rewire routes — done on branch `feat-remove-auth` (pushed, not merged)
- [x] Delete `auth/models.py`, `auth/controller.py`, `auth/service.py`, `auth/dao.py`, `auth/utils.py`, `auth/scopes.py`
- [x] Remove `dependencies.py::get_current_user`, `AuthenticatedUser`
- [x] `app.py` — `/chat` route: `get_current_user` → `require_visitor`
- [x] `chat/controller.py`, `feedback/controller.py`, `documents/controller.py` — swap `require_scope(Scope.APP)` for `require_visitor`
- [x] `chat/controller.py::_get_user_id_key` — renamed `_get_visitor_id_key`, reads `visitor_id` cookie directly instead of decoding JWT
- [x] `static/js/main.js` — removed `/api/auth/me`, `/api/auth/logout` calls, sign-out/avatar UI, dead OAuth flash messages
- [x] `templates/chat.html` — avatar/name/sign-out UI removed
- [x] `config.py` / `.env*` — dropped Google OAuth + JWT secret vars

Also had to apply the minimal `/docs` HTTP Basic Auth swap here too (since deleting `get_current_user` would otherwise break `/docs`) — duplicates a small piece of `feat-docs-cost-api`'s work. **Expected small merge conflict** on `app.py`/`dependencies.py`/`config.py` when both branches land on `develop` — not a bug, trivially resolvable (same change made independently on both branches).

### 4. Rename `user_id` → `visitor_id` across remaining modules — done on branch `feat-remove-auth` (same branch/commits as Section 3)
- [x] `chat/models.py`, `chat/dao.py`, `chat/service.py`, `chat/request_handler.py`
- [x] `feedback/models.py`, `feedback/dao.py`, `feedback/service.py`, `feedback/controller.py`
- [x] `spend/models.py`, `spend/dao.py`, `spend/service.py`

Verified: booted `app.py` under `TestClient` — `/docs` 401s without/wrong Basic Auth creds, 200s with correct ones; `/chat` 302-redirects without a `visitor_id` cookie; `/api/chat/messages`, `/api/chat/sessions`, `/api/feedback` all 401 without the cookie, reach the DB layer correctly with one present. Diffed `Base.metadata` against the migration file — exact column/index match, no leftover FKs.

### 5. Bot/abuse protection hardening — done on branch `feat-bot-protection` (pushed, not merged)
- [x] `spend/service.py` — `is_daily_cap_exceeded()`; `chat/request_handler.py` raises `SpendCapExceededError`, `chat/controller.py` returns 503 with a specific "reached today's usage limit, try again tomorrow" message. `GET /api/chat/messages` unaffected — history stays readable.
- [x] Add `DAILY_SPEND_CAP_USD` to `config.py` / `.env.example` (unset by default — never blocks chat until configured)
- [x] Confirm rate limiter (`limiter.py`) keys off `visitor_id` with IP fallback — verified already correct from Section 3's rename (`_get_visitor_id_key`), no changes needed. `/api/access/verify` correctly stays IP-keyed (necessarily pre-cookie).

Open Question 3 resolved: reused the existing generic 503 error-banner path in `static/js/main.js` (already shows `detail`) with a specific message string, rather than building a bespoke banner — kept this branch backend-only.

### 6. `/docs` + monthly cost API (Basic Auth) — done on branch `feat-docs-cost-api` (pushed, not merged)
- [x] Add `DOCS_USERNAME`, `DOCS_PASSWORD` to `config.py` / `.env.example` (blank — real credentials still needed)
- [x] `app.py` — gate `/docs` with `HTTPBasic`, checked against config (via `dependencies.py::verify_docs_credentials`, `secrets.compare_digest`)
- [x] `SpendDAO` — add `get_monthly_totals()` aggregation (GROUP BY year, month over `spend_logs.logged_at` + `estimated_cost_usd`)
- [x] `spend/service.py` — add `get_monthly_spend_summary()` shaping monthly totals into the finalized response format
- [x] Create `spend/controller.py` (new file) — `GET /api/spend/monthly`, gated by the same `HTTPBasic` dependency

### 7. Deployment
- [x] Update `.env.prod` on EC2 with new vars (`TURNSTILE_*`, `DAILY_SPEND_CAP_USD`, `DOCS_USERNAME`, `DOCS_PASSWORD`); remove Google OAuth + JWT vars
- [x] Update Cloudflare DNS/Turnstile site config for `prepit.mridulabs.dev` domain — registered as Invisible mode; required adding a privacy policy page (`GET /privacy`, branch `feat-privacy-policy`, off `develop`) referencing Cloudflare's Turnstile Privacy Addendum, per Cloudflare's own condition for Invisible mode
- [x] Run migration on production DB — applied 2026-08-26 (`d4f7c1a9b6e3`, confirmed at head), backup taken first (`prepwise_prod_backup_20260826_063727.sql`)
- [ ] Update `.claude/deployment_checklist.md` smoke-test steps (drop "Google Sign In works", "Sign out works"; add "Proceed button + Turnstile works", "Basic Auth on /docs works", "/privacy loads")

**Deploy notes (2026-08-26):** EC2 instance (t3.small, 1.9GB RAM, no swap configured) OOM'd during `docker compose build` — `pip install` on this dependency set (`arize-phoenix` pulls in `pandas`/`scipy`/`pyarrow`/`scikit-learn`) spiked memory past what was free, which also made SSH itself unresponsive mid-build. Fixed by adding a 2GB swapfile (`/swapfile`, persisted via `/etc/fstab`). Rebuild succeeded afterward (wall-clock still slow — instance also has poor network throughput, unrelated root cause). Considered resizing to t3.medium instead/also; deferred as a deliberate follow-up decision (cost + Elastic IP/DNS check first) rather than doing it live mid-incident. Full flow verified working in prod: landing page, Turnstile Proceed flow, chat round-trip, `/docs` Basic Auth, `/privacy`.

### 8. Merge into main plan
- [ ] Once implemented and verified, merge relevant sections of this draft into `.claude/plan.md` (ask-first, one step at a time per standing rule)
