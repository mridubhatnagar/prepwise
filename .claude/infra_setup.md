# Lead Setup Checklist

Complete these before handing off to agents or running the app end-to-end.

---

## One-time Setup

- [x] Buy domain `mridulabs.dev`

---

## Production / Deployment Setup
> **Do this only after local testing has fully passed and you are ready to deploy.**

- [ ] Issue wildcard SSL certificate for `*.mridulabs.dev` via Let's Encrypt (free, portable — not tied to AWS)
  - Use DNS challenge: `certbot certonly --manual --preferred-challenges dns -d "*.mridulabs.dev"`
  - Add the TXT record to your DNS as instructed by Certbot
  - Store the cert + key securely — needed for ALB upload
- [ ] Set up AWS infrastructure:
  - Launch EC2 instance (run Docker Compose on it)
  - Upload Let's Encrypt wildcard cert to ACM (import certificate)
  - Create ALB (Application Load Balancer) — handles HTTPS + SSL termination → forwards to EC2 port 8000
  - Attach imported cert to ALB listener (port 443)
  - Add HTTP → HTTPS redirect on ALB listener (port 80)
- [ ] Point DNS to AWS:
  - Add CNAME record `prepit.mridulabs.dev` → ALB DNS name (in Route 53 or your domain registrar)
- [ ] Update Google Cloud Console — add production redirect URI:
  - `https://prepit.mridulabs.dev/auth/callback`
- [ ] Update `.env` for production:
  - `JWT_COOKIE_SECURE=True`
  - `GOOGLE_REDIRECT_URI=https://prepit.mridulabs.dev/auth/callback`

---

## Do Now (before agents start)

- [x] **Google Cloud Console**
  - Create a new project
  - Enable Google OAuth 2.0
  - Register redirect URIs:
    - `http://localhost:8000/auth/callback`
    - `https://prepit.mridulabs.dev/auth/callback`
  - Copy Client ID + Client Secret

- [x] **API Keys**
  - Get OpenAI API key

- [x] **Fill `.env.local`**
  - Use plan.md Environment Variables section as reference
  - Never commit `.env.local` or `.env.prod` to git

- [x] **Gmail App Password (for spend alerts)**
  - Go to `myaccount.google.com` → Security → App Passwords
  - 2-Step Verification must be enabled
  - Create app password for "Mail" → copy 16-character password
  - Add to `.env.local` as `SMTP_PASSWORD`

- [x] **Create `docker-compose.yml`**
  - 4 services: `postgres`, `weaviate`, `phoenix`, `pgadmin`
  - No vectorizer module on Weaviate (embeddings handled by RetrievalClient)
  - Weaviate on host port 8083, gRPC on 50051
  - env vars loaded via `.env.local` (env_file directive)

---

## Do After Phase 1a (Database Agent) Completes

- [ ] **Seed `allowed_users`**
  - After migrations run, manually insert your email:
    ```sql
    INSERT INTO allowed_users (email, scope) VALUES ('your@email.com', 'app,docs');
    ```
  - `app,docs` scope gives you access to both the chat and Swagger UI

---

## Notes
- Tables are created automatically by the database agent via Alembic migrations — no manual SQL needed
- Docker Compose must be running before the database agent applies migrations
- [ ] V2: Extract SMTP email sending into a dedicated `notifications/` module once more alert types are needed
