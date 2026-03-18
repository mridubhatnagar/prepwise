# PrepIt

A RAG-powered technical interview prep assistant. Ask questions about system design, databases, DSA, and AI — get precise answers with citations, suggested follow-ups, and conversational context.

Invite-only. Sign in with Google.

---

## Tech Stack

| Concern | Choice |
|---|---|
| Backend | FastAPI |
| Frontend | Alpine.js + Bootstrap 5 |
| Auth | Google OAuth 2.0 + JWT (HttpOnly cookie) |
| LLM | OpenAI GPT-4o |
| Embeddings | OpenAI text-embedding-3-small |
| Vector DB | Weaviate (self-hosted) |
| Relational DB | PostgreSQL + SQLAlchemy + Alembic |
| Observability | Arize Phoenix (self-hosted) |

---

## Prerequisites

- Docker + Docker Compose
- Python 3.11+
- A Google OAuth 2.0 app (Client ID + Secret)
- An OpenAI API key

---

## Setup

**1. Clone and install dependencies**

```bash
git clone https://github.com/<your-username>/prepwise.git
cd prepwise
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**2. Configure environment**

```bash
cp .env.example .env.local
```

Fill in all values in `.env.local`. See `.env.example` for the full list of required keys.

**3. Run database migrations**

```bash
alembic upgrade head
```

**4. Ingest knowledge base documents**

```bash
python scripts/ingest.py
```

**5. Start the app**

```bash
docker compose up -d
```

Visit `http://localhost:8000`.

---

## Allowlist

Access is invite-only. Add a user's email to the `allowed_users` table before they can sign in.

---

## Observability

Phoenix UI is available at `http://localhost:6006`. All OpenAI calls (embeddings + LLM) are traced automatically.

---

## Environment Variables

See `.env.example` for the full list. Key variables:

| Variable | Description |
|---|---|
| `GOOGLE_CLIENT_ID` | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret |
| `GOOGLE_REDIRECT_URI` | OAuth callback URL |
| `OPENAI_API_KEY` | OpenAI API key |
| `DATABASE_URL` | PostgreSQL connection string |
| `JWT_SECRET` | Secret for signing JWT tokens |
| `SPEND_ALERT_THRESHOLD` | Daily spend limit in USD before email alert |

---

## Project Structure

```
prepwise/
├── app.py              # FastAPI entry point
├── config.py           # Centralised config (reads from .env)
├── constants.py        # Business constants
├── auth/               # Google OAuth, JWT, allowlist
├── chat/               # Sessions, message history, context limits
├── rag/                # Retrieval, confidence check, LLM response
├── spend/              # Cost logging and spend alerts
├── feedback/           # Thumbs up/down on AI responses
├── documents/          # KB document listing
├── infra/              # PostgreSQL + Weaviate client setup
├── scripts/            # ingest.py — one-time KB ingestion
├── docs/               # Raw knowledge base documents (Markdown)
├── templates/          # landing.html, chat.html
└── static/             # Alpine.js, CSS, images
```
