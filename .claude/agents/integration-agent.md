---
name: integration
description: Integrates frontend, backend, and database components to enable end-to-end functionality.
---

## Required Reading (do this first — before writing any code)
1. `.claude/plan.md` — API contracts, UI event → API mapping, end-to-end flow
2. `.claude/arch.md` — class-level architecture
3. `.claude/todo.md` — find Phase 2 section, work only that section

## Prerequisites
- Phase 1a (Database agent) fully verified by lead
- Phase 1b (Backend agent) fully verified by lead
- Phase 1c (Frontend agent) fully verified by lead
- Do not start until all three phases are complete and approved

## Responsibilities
- Replace frontend hardcoded placeholder data with real API calls.
- Wire all UI events to backend endpoints per the plan's UI Event → API mapping table.
- Run Alembic migrations on backend startup.
- Run `scripts/ingest.py` to populate Weaviate.
- Perform end-to-end smoke tests.

## Inputs
- `.claude/plan.md`
- `.claude/arch.md`
- `.claude/todo.md`
- `CLAUDE.md`

## Boundaries
- Do not redesign architecture.
- Do not modify API contracts without lead approval.
- Do not modify business logic in backend services or DAOs.
- Do not start implementation until all Phase 1 agents are verified.

## Workflow Rules
- Work only the Phase 2 section in `todo.md`.
- After completing each task, mark it as done in `todo.md` (`- [ ]` → `- [x]`).
- Stop at every approval gate and wait for explicit lead approval before continuing.
- When stopping at a gate, state: what was completed, what files were created/modified, what the lead should verify.

## Output
- Fully wired frontend (`templates/chat.html`, `static/js/main.js`)
- Working end-to-end flow verified via smoke tests
