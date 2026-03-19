# Architecture Decisions

## OAuth State Parameter (CSRF Protection)

**Why added:**
- The `/auth/callback` endpoint is public — no cookie, no authentication
- Without a state parameter, an attacker can trick an invited user into visiting `/auth/callback?code=ATTACKER_CODE`, logging them into the attacker's Google account
- CSRF protection prevents an attacker from tricking an invited user into authenticating with the attacker's Google account
- Implementation cost: server-side only — no frontend JS required for state management

**How it works:**
- On Sign-In click: browser navigates to `GET /api/auth/initiate` (window.location.href)
- Backend generates a random nonce, stores it in an HttpOnly cookie (`oauth_state`, SameSite=Lax, max_age=300), embeds it as `state=` param in the Google redirect URL
- Google echoes it back to `GET /auth/callback?code=...&state=...`
- Backend verifies returned `state` matches the `oauth_state` cookie → clears cookie immediately → proceeds with code exchange
- No frontend JS involved in state management — fully server-side

**Rule:** Always include state parameter in OAuth flows regardless of perceived risk level.

---

## JWT in HttpOnly Cookie

**Why HttpOnly cookie over localStorage or sessionStorage:**
- JWT needs to persist across requests for the session duration — without storing it, the user would have to log in on every request
- localStorage and sessionStorage are accessible via JavaScript — XSS attacks could steal the token with a single `localStorage.getItem('jwt')` call
- HttpOnly cookie is invisible to JavaScript entirely — XSS cannot steal what it cannot read
- Cookie is sent automatically by the browser on every request — no manual handling needed in frontend code

**Why GET /api/auth/me:**
- Chat page needs the user's name and avatar to render the app bar

**Data isolation:**
- Every user has their own JWT with their own `user_id` embedded
- Every DB query is scoped to that `user_id` — one user can never access another user's chat history, sessions, or feedback
- The token is the identity boundary between users

**How it works:**
- After successful OAuth, JWT is set as an HttpOnly, SameSite=Lax, Secure cookie named `jwt`
- Token contains only `user_id` and `scopes` — no PII in the token itself
- On protected routes, JWT is read from the cookie server-side, `user_id` extracted, user details fetched from DB
- `/api/auth/me` returns user details (name, email, avatar) to the frontend — protected by `get_current_user()`, so only the authenticated user can fetch their own data
- Expiry is configurable — currently 1 hour

**Rule:** Never store JWT in localStorage or sessionStorage. Always use HttpOnly cookie.

---

## Layered Architecture

**Why:**
- Each layer has a single responsibility — DAOs handle data access, services are wrappers over DAOs, request handlers and orchestrators handle business logic, controllers handle request/response
- Service classes are intentionally kept as thin DAO wrappers — adding business logic to them would increase dependencies between classes, making them harder to test
- Easy to extend — module-wise folder structure means adding a new feature doesn't touch unrelated code
- Testable by design — services accept DAO interfaces, making it straightforward to swap in test implementations later

---

## Weaviate over pgvector

**pgvector advantages:**
- Takes less memory — good fit for small projects
- Lives inside Postgres — no separate service to manage

**pgvector disadvantages:**
- Hybrid search requires manual setup — combining pgvector with Postgres full-text search yourself
- No dedicated Python client — interacted with through SQLAlchemy or psycopg2

**Why Weaviate:**
- Industry uses dedicated vector DBs like Weaviate and Pinecone and expects applicants to know them
- Had done a course on Weaviate and wanted to try hands-on
- Dedicated Python client
- Hybrid and vector search built in out of the box

---

## RAG over Fine-Tuning

**Why RAG:**
- The product doesn't have a huge customer base or niche information — documents are easily accessible and can be updated without touching the model
- Fine-tuning is expensive, time consuming, and requires high quality training data

**When fine-tuning makes sense:**
- When the model's behavior, tone, or response style needs to be changed for a specific brand or domain
- Fine-tuning updates the model's weights on top of an existing model — it is not retraining from scratch

---

## Docker-Based Development

**Why:**
- Ensures every environment gets the exact same versions of Postgres, Weaviate, and Python — no manual installation on the host machine
- Local setup mirrors production exactly, eliminating environment-specific bugs

**docker-compose.override.yml per environment:**
- `.env.local` and `.env.prod` are never pushed to GitHub — each must be picked up automatically without manual changes to the base compose file
- Each environment has its own `docker-compose.override.yml` pointing to the appropriate env file — local uses `.env.local`, production uses `.env.prod`
- `docker-compose.yml` stays untouched regardless of environment

**Rule:** All services run via Docker Compose locally and in production. Never modify `docker-compose.yml` for environment-specific config — all differences go in `docker-compose.override.yml`.

---

## GitHub Actions

**Auto deployment:**
- Saves time and effort of SSHing into EC2 and running commands manually each time
- All production deploys go through the GitHub Actions workflow — no direct SSH deploys

**Gemini PR review:**
- Automated code review on every PR targeting `develop`
- Catches issues before they reach the integration branch

**Release notes:**
- Auto-generated from merged PR titles on every production deploy
- Provides a traceable history of what shipped in each release

---

## AWS for Deployment

**Why:**
- AWS offers a 6-month free tier — no cost for hosting during development and early user testing
- AWS and GCP are the most widely used cloud providers across the industry — good opportunity to get hands-on experience
- EC2 gives full control over the server environment, making it straightforward to run Docker Compose in production
