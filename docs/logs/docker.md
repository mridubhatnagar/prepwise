# 🐳 Docker — Knowledge Base Logs (Date-wise)

## 📅 2026-01-25
**Status:** Rest day  
- No Docker learning.

---

## 📅 2026-01-26 — Docker Basics & Images
### Concepts Learned
- VM vs Containers
- Purpose of Docker (portability, environment consistency)
- Host port vs Container port
- Docker images vs containers
- Dockerfile fundamentals

### Commands Practiced
- `docker ps`, `docker ps -a`
- `docker pull`, `docker run`
- `docker stop`, `docker rm`, `docker rmi`
- `docker exec`, `docker logs`, `docker inspect`

### Hands-on
- Ran containers with port mapping (`-p`)
- Built custom Docker images
- Analyzed Dockerfile from office codebase
- Completed Docker images lab (KodeKloud)

### Key Takeaways
- Containers are lightweight compared to VMs.
- Port mapping bridges host and container networking.
- Dockerfile layering impacts build speed and image size.

---

## 📅 2026-01-27 — Dockerfile & Flask App Containerization
### Concepts Learned
- CMD vs ENTRYPOINT
- Environment variables in Docker
- Dockerfile optimization (layer caching, slim images)

### Hands-on
- Dockerized a Flask application
- Wrote Dockerfile from scratch
- Completed CMD vs ENTRYPOINT lab

### Key Takeaways
- CMD is overridable; ENTRYPOINT defines container intent.
- Copying `requirements.txt` before source code optimizes builds.

---

## 📅 2026-01-28 — Docker Compose & Multi-container Architecture
### Concepts Learned
- Docker Compose purpose and structure
- Services, networks, and dependencies
- Docker Engine vs Docker CLI
- Multi-container application architecture

### Hands-on
- Completed Docker Compose lab
- Explored `example-voting-app` (multi-language containers)
- Observed .NET worker image build failure

### Key Takeaways
- Compose defines systems, not just containers.
- Service names act as DNS hostnames inside Docker networks.
- Multi-container setups introduce real-world complexity.

---

## 📅 2026-01-29 — Flask + Redis (Docker Compose Project)
### Project Overview
- Built a multi-container system:
  - Flask app (stateless)
  - Redis (stateful)

### Hands-on
- Integrated Redis with Flask
- Debugged Redis connectivity issues:
  - Port exposure (`-p 6379:6379`)
  - Environment variables (`REDIS_HOST`)
- Implemented Docker Compose setup
- Fixed Dockerfile build context issues
- Successfully ran:
  ```bash
  docker compose up --build
  ```
### Key Learnings  
- Container-to-container communication uses service names, not localhost.
- Docker Compose creates a default network automatically.
- Stateless apps + stateful services is a core backend pattern.

## 📅 2026-01-29
### Concepts Learned
- **Docker Compose lifecycle commands:**
  - `up`
  - `stop`
  - `start`
  - `down`
- Container ephemerality
- Redis persistence behavior without volumes
### Hands-on
- Experimented with multi-container Docker Compose setup
- Compared `docker compose stop` vs `docker compose down`
- Observed Redis data reset after container restart
### Key Takeaways

- Containers are ephemeral by default.
- Persistence requires Docker volumes.
- Port exposure is needed only for host-to-container access.

## 2026-01-30

- Completed Docker Engine and Docker Storage from KodeKloud
- Learnt about Volumes. For making data persistent.
- Did the Docker Storage lab.
- NOTE - /opt/data - is present on host machine. Not in container.
- Follow up - Do a project using volume. 

## 📅 2026-01-31 — Docker Volumes & Redis Persistence

### Concepts Learned
- Difference between **container lifecycle** and **data lifecycle**
- Docker volumes vs container filesystem
- Named volumes vs anonymous volumes
- `docker compose down` vs `docker compose down -v`
- Persistence is an **application-level contract**, not just a Docker feature
- Redis data directory (`/data`) and how Redis reloads state on startup

---

### Hands-on
- Configured Redis persistence using a **named Docker volume**
- Mounted Redis data directory (`/data`) to Docker-managed volume
- Validated Docker Compose syntax (`volumes` as list vs mapping)
- Ran controlled experiments:
  - `docker compose up -d`
  - `docker compose down`
  - `docker compose up`
  - `docker compose down -v`
- Verified persistence and data reset behavior experimentally

---

### Observations
- Data persists across `docker compose down → up` when volume exists
- Data resets after `docker compose down -v` due to volume deletion
- Redis persistence is **predictable and intentional** when correctly wired
- Google emulator behavior differs because it does not guarantee state reload even when using Docker volumes

---

### Key Takeaways
- Containers are disposable; **volumes are durable**
- Persistence requires:
  1. Application writing state to disk
  2. Stable data directory
  3. Volume backing that directory
- Docker guarantees byte survival, **not semantic persistence**
- Redis reloads state by design; emulators do not guarantee this

---

## 📅 2026-02-01 — Postgres Persistence, Flask Integration & Docker Networking

### Hands-on
- Added Postgres service to Docker Compose with named volume
- Verified Postgres persistence across:
  - `docker compose up`
  - `docker compose down`
- Connected Flask application to Postgres using service name (`postgres`)
- Successfully executed inserts and reads from Postgres
- Confirmed data persistence behavior using volume lifecycle
---
### Concepts Learned
- Postgres data directory (`/var/lib/postgresql/data`) must be mounted for persistence
- Persistence behavior mirrors Redis when volumes are configured correctly
- Docker Compose `build: .` creates its **own image**
- Images built via `docker build -t` are **not automatically reused** by Docker Compose
- Correct workflow when using `build:` is:
  - `docker compose up --build`
- Looked up documentation for finding volume path, environment variables to be used with postgres
---
### Networking
- Watched Docker networking videos from KodeKloud
- Completed networking lab
- Reinforced concepts:
  - Docker host vs container
  - Service name–based DNS inside Docker networks
  - Internal container communication without port exposure
  - Ports are required only for host access
---
### Key Takeaways
- Database persistence in Docker requires:
  - Correct internal data directory
  - Explicit named volumes
- Redis and Postgres follow the same persistence pattern with different data paths
- Docker Compose owns the image lifecycle when `build:` is used
- Docker networking concepts are clearer after hands-on multi-container setups
---

## 📅 2026-02-02 — Postgres UI Integration (pgAdmin)

### Hands-on
- Added **pgAdmin** as a separate service in Docker Compose
- Exposed pgAdmin UI via host port
- Connected pgAdmin to Postgres using Docker service name (`postgres`)
- Verified visibility of:
  - default `postgres` database
  - application database (`test`)
- Used pgAdmin UI to inspect schemas and tables

---
### Concepts Reinforced
- Database UI tools are **clients**, not databases
- pgAdmin does not auto-discover databases
- Servers must be explicitly registered inside pgAdmin
- Docker service names act as internal DNS hosts
- UI tools should not be treated as application dependencies
---
### Key Takeaways
- pgAdmin runs independently of the application
- Postgres does not need to expose ports for pgAdmin access
- One Postgres instance can host multiple databases
- Docker Compose can include tooling containers without coupling them to the app
---

## 📅 2026-02-03 — Docker Registry & Course Completion

### Hands-on
- Watched Docker registry video on KodeKloud
- Completed Docker registry lab (push / pull images)
- Completed YAML-related lab
- Finished KodeKloud Docker course
- Received course completion certificate
- Added custom network to the application docker compose
---

### Concepts Learned
- Docker registry is a central place to store container images
- Difference between:
  - local images
  - public registries
  - private registries
- Image lifecycle beyond local development
- How CI/CD pipelines rely on registries
    - CI builds the images
    - Servers pull the image
    - Build and run are decoupled
- Registries are often
    - AWS ECR
    - GCP Artifact Registry
---

### Key Takeaways
- Docker registry knowledge is important for **awareness**
- Registry usage is more common in:
  - CI/CD pipelines
  - production deployments
- Local development often relies on `docker compose build` instead of pushed images
---

## 📅 2026-02-06 — Docker Completion & Office Setup Finalization

### Focus
- Finalize multi-environment Docker setup
- Apply learnings to real office project

### Hands-on

- Fixed Datastore emulator persistence by aligning:
  - `--data-dir` path
  - Docker volume mount path
- Verified deterministic persistence across:
  - `docker compose down`
  - `docker compose up -d`
  - `docker compose up --build -d`
- Implemented multi-environment setup using:
  - `--profile`
  - `docker-compose.override.yml`
- Completed office setup for:
  - `SETUP_ENV=regular`
  - `SETUP_ENV=diploma`

### Concepts Mastered

- Container writable layer vs Docker volumes
- Volume mount path alignment
- Why data disappears during container recreation
- Difference between:
  - `up -d`
  - `up --build -d`
  - `down`
  - `down -v`
- Docker Compose profiles
- Compose file layering and override merging

### Key Realizations

- Containers are ephemeral by design.
- Volumes must back the exact directory the application writes to.
- Rebuild deletes container layer, not volumes.
- Multi-environment setups are configuration problems, not infrastructure duplication problems.
- Deterministic persistence eliminates fear of stopping containers.

---
