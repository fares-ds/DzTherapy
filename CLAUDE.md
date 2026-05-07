# CLAUDE.md

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- **Research → Plan → Implement, in that order.** Every task starts with reading the relevant code and writing a brief plan. No direct implementation without understanding the problem first. The output of research and planning lands in [TASKS.md](TASKS.md) — see "Task Discipline" below.
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

## 5. Task Discipline

**Track work in [TASKS.md](TASKS.md). Lifecycle: Research → Planned → In-Progress → Done.**

- TASKS.md is the single source of truth for in-flight and queued work. Open it at the start of every session; close out work in the same commit that ships the code.
- When you discover an issue, limitation, or gap mid-task, log it in TASKS.md ("Issues / Technical Debt") **before context-switching**. Don't trust memory.
- Speculative ideas go to "Research / Ideas". Promote to "Backlog" only after a brief research pass clarifies scope and acceptance criteria.
- Cap "In Progress" at 2. More than that means you're not finishing things.
- Challenge existing implementations when you touch them — note debt or improvement candidates in TASKS.md instead of silently rewriting.

## 6. Documentation & Tracking Consistency

**Documentation is part of the feature. Ship it in the same commit as the code.**

After any **major change**, review and update — in the same commit as the code change:

- [CLAUDE.md](CLAUDE.md) — when workflows, conventions, architecture, or runtime behavior change.
- [README.md](README.md) — when setup, usage, public-facing features, env vars, or endpoints change.
- [TASKS.md](TASKS.md) — move the completed task to "Completed", log newly discovered issues to "Issues / Technical Debt", and queue follow-ups to "Backlog".

**What counts as a major change:**
- New feature or endpoint.
- Architecture or pipeline modification.
- New integration (service, library, external dependency).
- Refactor that moves code across modules or changes a public contract.
- Any change in observable system behavior, performance characteristics, or operational defaults.

**Enforcement:**
- If a file does not need an update, state explicitly which files you reviewed and why no change was required. Silent skips are not acceptable.
- The three files must stay consistent with each other: a fact stated in one must not contradict another.
- A change that ships code without the matching doc update is incomplete. Treat the doc lines as part of the diff, not an afterthought.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

---

## Workflow

- For commands that take a long time to run (build steps, ingestion scripts, docker builds, etc.), tell the user what to run instead of executing them directly. The user will run them manually.
- After each implementation, test what has been done (run relevant tests, hit the endpoint, verify the behavior).
- For documentation/tracking updates after a change, follow section 6 ("Documentation & Tracking Consistency").

## 7. Project Guards (DzTherapy-specific, locked invariants)

These are non-negotiable for DzTherapy. Every suggestion must respect them.

1. **No per-session commission, ever.** Locked by business model. Even small "convenience fees" are off the table — breaking the "we never take a cut of your sessions" promise to therapists destroys trust and the company.
2. **Therapist-first filter.** Every product/feature suggestion must pass: *"does this make therapists more likely to subscribe in year 2?"* If a feature only helps users without strengthening therapist stickiness, it's a luxury this bootstrapped runway can't afford.
3. **Pass-through payments only at MVP.** The platform never holds or processes user→therapist money. Therapists publish their own payment instructions (CCP/RIB/Edahabia); users pay them directly off-platform. This avoids SATIM merchant onboarding, PSP licensing, KYC and fraud liability.
4. **Bootstrap constraints are real.** Default to free hosting/email/video tiers, no paid tools, no salaries. Years 1–2 have zero revenue by design — every avoidable cost shortens the path to dying.
5. **French-only UI at MVP.** Arabic in Phase 2, English Phase 3+. Don't proactively suggest multi-language work for v1.
6. **Server-rendered Django + HTMX is the chosen stack.** Don't propose React / Next.js / SPA work for v1. The stack decision is locked — see PRD §13 for canonical details.

## 8. Project State and Source of Truth

- **Skeleton scaffolded 2026-05-07.** Django project + Postgres via Docker + HTMX + Alpine + Tailwind + pytest are wired up; application code (custom User, therapist/booking models, allauth) is not yet written. Folder contents: this `CLAUDE.md`, the PRD ([algeria_mental_health_saas_prd.md](algeria_mental_health_saas_prd.md)), [TASKS.md](TASKS.md), [README.md](README.md), Django skeleton (`config/`, `core/`, `templates/`, `tailwind/`), `manage.py`, `pyproject.toml`, `Makefile`, `docker-compose.yml`, `.env.example`.
- **The PRD is the source of truth** for product strategy, business model, MVP scope, roadmap, risks, and validated/unvalidated assumptions. Read it before suggesting features or making architectural decisions.
- **Tech stack — locked** (canonical details in [PRD §13](algeria_mental_health_saas_prd.md)):
  - **Web framework:** Django 5.x (single monolith) + Django Templates + HTMX + Alpine.js + Tailwind CSS (standalone CLI, no Node).
  - **Database:** PostgreSQL (Docker locally; production hosting deferred).
  - **Auth:** `django.contrib.auth` + `django-allauth` (allauth lands in C3 — not yet wired).
  - **External:** Daily.co (video), Resend (email), Cloudflare R2 (prod receipt storage) — not yet wired; land in Tracks E / F / H.
  - **Tooling:** pytest + pytest-django + factory_boy, ruff + black (B6), GitHub Actions (B7), Sentry free tier (B9).
  - **Not in v1:** React / Next.js / SPA, FastAPI, Redis, WebSockets, Celery, Kubernetes, React Native.

## 9. Running

Prerequisites: Python 3.12, Docker.

```bash
# One-time setup
python -m venv .venv && source .venv/bin/activate
make install              # pip install -e ".[dev]"
cp .env.example .env

# Daily dev (two terminals)
make db-up                # start Postgres in Docker
make migrate              # run Django migrations
make tailwind             # terminal 1: Tailwind in watch mode
make dev                  # terminal 2: Django on :8000
make test                 # run pytest
make lint                 # ruff check + black --check (no changes)
make format               # ruff --fix + black (auto-fix)
```

`make help` lists all targets. The Tailwind binary auto-downloads on the first `make tailwind` run via `django-tailwind-cli`.

## 10. Architecture

Current state of the codebase (skeleton only — domain models land in Tracks C onward):

- **`config/`** — project package: `settings.py` (single file, env-driven via `django-environ`), `urls.py` (mounts `core.urls` at `/`), `wsgi.py`, `asgi.py`.
- **`core/`** — smoke-test app with a home view and an HTMX demo partial. Disposable / can grow into a public-pages app.
- **`templates/`** — project-wide templates. `base.html` carries the Tailwind CSS link, HTMX, and Alpine includes. App templates live under `templates/<app>/`.
- **`tailwind/input.css`** — Tailwind v4 source; `@source` directives scan `templates/` and `core/`.
- **External in MVP:** PostgreSQL only (via `docker-compose.yml`). Daily.co, Resend, R2 are not yet wired.
- **PWA assets** served by `core` views: `/manifest.webmanifest` and `/sw.js`. The service worker is intentionally root-scoped (`/`) so it can intercept all navigations; templates live at `templates/manifest.webmanifest` and `templates/sw.js`.

## 11. Conventions

- **Server-rendered first.** Every page is a Django view returning rendered HTML. HTMX swaps in partials when needed.
- **HTMX partial templates** are named with a leading underscore: `templates/<app>/_<name>_partial.html`. Views returning partials use `render(request, "...")` exactly like full pages — HTMX sees the inner HTML and swaps it.
- **Tailwind utilities only** — no custom CSS file beyond `tailwind/input.css`. Custom design tokens, when needed, go in `input.css` via `@theme` (Tailwind v4) — not a separate stylesheet.
- **URL references** always use the `{% url 'app:name' %}` tag (or `reverse('app:name')` in Python). Never hardcode paths.
- **Alpine** is for tiny, ephemeral client interactions (toggles, dropdowns, counters). Anything that touches the database or persists state goes through HTMX → Django.
- **Tests live in `<app>/tests/`** as a package, not `tests.py`. Pytest config in `pyproject.toml` discovers `test_*.py` files.
- **Factories live in `<app>/factories.py`** and use `factory_boy`'s `DjangoModelFactory`. Use `get_user_model()` so factories survive the C1 swap to a custom User.
- **Lint passes before commit.** Pre-commit runs ruff + black on staged files; run `make format` to auto-fix locally. CI enforces the same checks remotely (see §12).

## 12. CI

[.github/workflows/ci.yml](.github/workflows/ci.yml) runs on every push to `main` and every pull request. Two parallel jobs:

- **`lint`** — runs `pre-commit run --all-files`. Same ruff + black + pre-commit-hooks set as local. If a push fails CI on lint, run `make format` locally and re-push.
- **`test`** — installs deps, spins up a Postgres 16 service container, runs `pytest`.

Both jobs cache pip downloads (keyed on `pyproject.toml`); the lint job additionally caches `~/.cache/pre-commit` (keyed on `.pre-commit-config.yaml`). A warm run is under a minute.

**Branch protection is a one-time GitHub UI setup, not part of the workflow file.** The workflow file makes the run pass or fail; the *enforcement* (red check blocks merge) requires GitHub repo settings: Settings → Branches → Branch protection rules → require status checks → select `lint` and `test`. Configure this once when the repo is pushed to GitHub.

`SENTRY_DSN` is not set in CI, so Sentry is disabled during test runs (the conditional in §13 short-circuits).

## 13. Environment & secrets

All runtime config flows through env vars read in [config/settings.py](config/settings.py) via `django-environ`. Local dev reads `.env` (gitignored); production reads from the platform's env var store.

### Required (dev + prod)

| Variable | Dev default (in `.env.example`) | Production |
|---|---|---|
| `DEBUG` | `True` | **`False`** |
| `SECRET_KEY` | `change-me-in-production` (placeholder) | strong random secret, never committed |
| `DATABASE_URL` | `postgres://dz:dz@localhost:5434/dztherapy` (Docker compose) | platform-issued Postgres URL |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | real domain(s) |

### Optional

| Variable | Dev default | Production |
|---|---|---|
| `SENTRY_DSN` | empty (Sentry disabled) | populated |

### Production-mode behavior

When `DEBUG=False`, [config/settings.py](config/settings.py) enables a small set of security headers (`SECURE_HSTS_*`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_PROXY_SSL_HEADER`). `SECURE_SSL_REDIRECT` is **deliberately not set** — HTTPS redirect is the hosting platform's responsibility (Railway / Fly.io / nginx all handle it at the edge), and setting it in Django creates redirect loops if `SECURE_PROXY_SSL_HEADER` isn't perfectly aligned with the proxy.

### Sentry verification (one-time)

After deploying with `SENTRY_DSN` populated, trigger a deliberate exception (e.g. a `manage.py shell` session running `1/0`, or temporarily adding `raise Exception("test")` in a debug view) and confirm it appears in the Sentry dashboard under the `prod` environment. Remove any temporary debug view afterward.
