# V2 Features

## ✅ Proper Deployment Flow
- EC2 should pull from `production` branch only
- Code goes: `develop` → PR → merge to `production` → deploy
- Update deploy command on EC2: `git pull origin production` instead of `git pull origin develop`
- GitHub Actions to automate deploy on merge to `production` (workflow file already created at `.github/workflows/deploy.yml`)
- Needs three GitHub Secrets: `EC2_HOST`, `EC2_USER`, `EC2_SSH_KEY`

## API Versioning
- Add `/v1/` prefix to all API endpoints (e.g. `/api/chat/messages` → `/api/v1/chat/messages`)
- Update all frontend fetch calls to use versioned paths
- Allows breaking changes in future without affecting existing clients

## Dynamic Suggestion Chips
- Maintain a large pool of questions in `constants.py` covering all KB categories (system design, databases, DSA, AI)
- Backend picks N random questions from the pool on page load — no duplicates
- Expose via API endpoint
- Frontend loads dynamically instead of hardcoded array
- Saves LLM cost compared to generating suggestions via LLM
