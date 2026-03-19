# AWS Deployment Checklist (EC2 t3.small + Docker Compose)

## 1. AWS Account Setup
- [x] Create AWS account at aws.amazon.com
- [x] Enable MFA on root account
- [x] Create IAM user with EC2 access (avoid using root account)

## 2. Launch EC2 Instance
- [x] Go to EC2 → Launch Instance
- [x] Choose **Ubuntu 22.04 LTS**
- [x] Instance type: **t3.small**
- [x] Create a key pair (.pem file) — save it, you can't download it again
- [x] Configure storage: **30GB gp2**
- [x] Launch instance
- [ ] Assign an **Elastic IP** to the instance (so IP doesn't change on restart)

## 3. Security Group (Firewall Rules)
- [x] Allow **SSH** (port 22) — your IP only
- [x] Allow **HTTP** (port 80) — anywhere
- [x] Allow **HTTPS** (port 443) — anywhere
- [x] Block all other ports from public access (8000, 5432, 8083, 6006, 5050)

## 4. Connect to EC2
```bash
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@<elastic-ip>
```
- [x] Successfully connected to EC2

## 5. Install Dependencies on EC2
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y docker.io docker-compose-v2 git nginx certbot python3-certbot-nginx
sudo usermod -aG docker ubuntu
# Log out and back in for docker group to take effect
```
- [x] All dependencies installed
- [x] Docker working without sudo

## 6. Clone Repo
```bash
git clone https://github.com/mridubhatnagar/prepwise.git
cd prepwise
git checkout production
```
- [x] Repo cloned and on production branch

## 7. Configure Environment
```bash
cp .env.example .env.prod
nano .env.prod
```
- [x] Set `SETUP_ENV=prod`
- [x] Set `JWT_COOKIE_SECURE=true`
- [x] Set `GOOGLE_REDIRECT_URI` to `https://prepit.mridulabs.dev/auth/callback`
- [x] Fill in all other keys (OpenAI, Google OAuth, DB credentials, JWT secret etc.)

## 8. Configure docker-compose.override.yml for Production
- [x] Create `docker-compose.override.yml` pointing all services to `.env.prod`
- [x] Never modify `docker-compose.yml` directly

> pgadmin is kept but port 5050 is blocked in the security group.
> Access it locally via SSH tunnel when needed:
> `ssh -i your-key.pem -L 5050:localhost:5050 ubuntu@<elastic-ip>`

## 9. Domain Setup (Cloudflare — mridulabs.dev)
- [x] Go to Cloudflare DNS for mridulabs.dev
- [x] Add A record: **Name** `prepit`, **Content** `<elastic-ip>`, **Proxy** DNS only (grey cloud)
- [x] Wait for DNS to propagate (usually a few minutes on Cloudflare)

## 10. Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/prepwise
```
Add:
```nginx
server {
    listen 80;
    server_name prepit.mridulabs.dev;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```
```bash
sudo ln -s /etc/nginx/sites-available/prepwise /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```
- [x] Nginx configured and running

## 11. SSL with Certbot
```bash
sudo certbot --nginx -d prepit.mridulabs.dev
```
- [x] SSL configured
- [x] Auto-renewal is set up by certbot automatically

## 12. Start All Services
```bash
docker compose up -d
```
- [x] All 5 services running

## 13. Run Migrations
```bash
docker compose exec app alembic upgrade head
```
- [x] Migrations applied

## 14. Ingest Knowledge Base
```bash
docker compose exec app python scripts/ingest.py
```
- [x] 29 docs, 127 chunks ingested

## 15. Update Google OAuth Console
- [x] Add `https://prepit.mridulabs.dev` to **Authorised JavaScript origins**
- [x] Add `https://prepit.mridulabs.dev/auth/callback` to **Authorised redirect URIs**

## 16. Add Yourself to Allowlist
- [x] Insert your email into the `allowed_users` table in PostgreSQL

## 17. Smoke Test
- [x] Landing page loads at `https://prepit.mridulabs.dev`
- [x] Google Sign In works
- [x] Chat works end to end
- [x] Citations appear
- [x] Follow-up questions appear
- [x] Context limit banner works
- [x] Feedback buttons work
- [x] Sign out works

---

## Deploying New Code (after initial setup)
- Merge `develop → production` via PR on GitHub
- GitHub Actions will trigger automatically — approve the deployment in the Actions tab
- Deploy runs on EC2 automatically: pulls latest, rebuilds app, runs migrations

## Upgrading Instance (if t3.small struggles)
1. Stop EC2 instance
2. Change instance type to **t3.medium**
3. Start instance
4. Everything resumes automatically
