# DzTherapy

Therapy / mental wellness SaaS for the Algerian market.

Free for users and therapists in years 1–2; therapist monthly subscription only from year 2 (no per-session commission, ever).

## Status

**Repo skeleton scaffolded** (Django + Postgres + HTMX + Alpine + Tailwind + pytest). Application code (auth, therapists, bookings) lands in Track C onward — see [TASKS.md](./TASKS.md). Strategy is locked; pre-build validation is in flight in parallel.

## Local development

Prerequisites: **Python 3.12**, **Docker**.

```bash
git clone <repo-url> dztherapy && cd dztherapy
python -m venv .venv && source .venv/bin/activate
make install
cp .env.example .env
make db-up
make migrate
make tailwind   # run in a separate terminal — keeps watching
make dev        # http://localhost:8000
make test
```

`make help` lists all available targets.

## Where to look

- **Product strategy and scope:** [algeria_mental_health_saas_prd.md](./algeria_mental_health_saas_prd.md) — the source of truth.
- **Working guidelines for contributors / AI assistants:** [CLAUDE.md](./CLAUDE.md) — project guards in §7, dev workflow in §9, conventions in §11.
- **In-flight and queued work:** [TASKS.md](./TASKS.md).
