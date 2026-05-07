# TASKS.md

> Single source of truth for in-flight and queued work on DzTherapy.
> Lifecycle: **Research / Ideas → Backlog → In Progress (cap 2) → Done**.
> Newly discovered issues land in **Issues / Technical Debt** before context-switching.

## In Progress (cap 2)

*(none — no work has started yet)*

## Backlog

> Tracks A and B run in parallel from day 1. Track A is founder work (interviews, lawyer, network testing) — clock time is mostly waiting. Track B is domain-agnostic scaffolding — useful regardless of A's outcome. Domain-bearing tracks (D onward) wait on validation only where the model could change.
>
> **Critical path:** A1 → D1 → D2 → D3 → D4 → E4 → E5 → E6 → E7 → E8 → I1 → I2 → I3.

### Track A — Pre-build validation (founder work, non-coding)

Maps 1:1 to PRD §22 validation actions. Findings here can change the product/business model.

- **A1 — 10 therapist interviews on willingness to pay (highest leverage).** *acceptance: ≥10 conversations completed; notes saved per-interview in `validation/therapist-interviews/`; quantified result on "would you pay 5,000 DZD/mo for this in 18 months?"; `SUMMARY.md` with go/no-go recommendation. If <40% yes, model needs rethink before D begins.*
- **A2 — 10 user interviews (urban professional women 25–35, French-speaking).** *acceptance: ≥10 conversations completed; notes in `validation/user-interviews/`; quantified result on willingness to book + tolerance for "pay therapist directly" friction; `SUMMARY.md`.*
- **A3 — Lawyer engagement on PRD §11 questions #1, #3, #5, #6.** *acceptance: written lawyer response to each of the four questions saved in `validation/legal/`; clear go/no-go for the pass-through payment model.*
- **A4 — Daily.co reliability test on Algerian mobile networks.** *acceptance: 2 sessions × 2 cities (Algiers, Oran) × 2 times of day; results documented (latency, drop rate, audio/video quality on 3G + 4G); decision to proceed with Daily.co or evaluate LiveKit.*
- **A5 — Founder runway commitment in writing.** *acceptance: written commitment of months-of-personal-funds available; stored in `validation/founder-runway.md`.*

### Track B — Repo skeleton + dev environment

**Track B complete.** All scaffolding tasks (B1–B10) shipped. See Done below.

### Track C — Auth + user model + i18n

Domain-light. Starts once B1–B5 are done; no dependency on validation.

- **C1 — Custom `User` model with `role` field (`end_user` | `therapist`).** *acceptance: `accounts/models.py` defines `User` with `role`; `settings.AUTH_USER_MODEL` updated; migration runs cleanly on a fresh database.*
- **C2 — Skeletal `TherapistProfile` 1:1 model.** *acceptance: `therapists/models.py` defines `TherapistProfile` with FK to `User`; admin registration works; migration runs.*
- **C3 — `django-allauth` configured for email auth.** *acceptance: signup, login, logout, email verification, password reset all work via allauth's stock URLs; pages styled with project base template.*
- **C4 — French as default locale + gettext setup.** *acceptance: `LANGUAGE_CODE='fr'`; `LOCALE_PATHS` configured; `manage.py makemessages -l fr` runs; example `{% trans %}` tag renders the French translation.*
- **C5 — Base templates (header, footer, nav).** *acceptance: `base.html` renders consistent layout; nav handles auth state (logged in/out); follows trust-oriented copy guideline (PRD §8).*

### Track D — Therapist-facing surface (the future revenue product)

Maps 1:1 to PRD §6 therapist features. Starts after C1–C2 land **and** A1 reports green.

- **D1 — Therapist signup flow.** *acceptance: a logged-out user can submit name + email + credentials + photo + bio + languages + specialties; on submit, creates a `User(role=therapist)` + unverified `TherapistProfile`; record lands in admin verification queue.*
- **D2 — Manual verification in Django admin.** *acceptance: admin sees pending `TherapistProfile`s; can approve or reject with a reason; approval triggers a confirmation email via Resend.*
- **D3 — Profile editor for approved therapists.** *acceptance: an approved therapist can edit bio, photo, specialties, languages, payment instructions (CCP / RIB / Edahabia), session price; HTMX-based partial saves work; changes persist.*
- **D4 — Weekly availability calendar editor.** *acceptance: an approved therapist can set recurring weekly availability (e.g. Mon 9–12, Wed 14–18); persists as `Availability` model entries; can block specific dates as exceptions.*
- **D5 — Booking inbox view.** *acceptance: incoming booking requests listed; therapist can accept/decline; accepted bookings show payment status; HTMX live updates without full page reload.*
- **D6 — Patient list view.** *acceptance: list of users who've booked at least once with this therapist; shows name, contact, total session count, last session date; sortable.*

### Track E — User-facing surface (kept minimal — funnel)

Maps to PRD §6 user features. Depends on D1–D4 being roughly working.

- **E1 — Email signup (uses C3 allauth).** *acceptance: a visitor can sign up with email + password; email verification works; lands on the therapist list.*
- **E2 — Therapist list page.** *acceptance: hand-curated list of approved therapists rendered as cards; each card shows photo, name, languages, specialties, session price; click → profile page. No search, no filters in v1.*
- **E3 — Therapist public profile page.** *acceptance: full bio, credentials, languages, specialties, price, available slots (next 14 days); CTA to book.*
- **E4 — Calendar slot picker (booking start).** *acceptance: shows available slots derived from D4 minus existing bookings; user clicks a slot → booking form (preferred contact, optional notes).*
- **E5 — "Pay therapist directly" instructions screen.** *acceptance: after booking submit, user sees the therapist's payment instructions (from D3); booking is created in `pending_payment` state.*
- **E6 — "I have paid" confirmation + receipt upload.** *acceptance: user can mark as paid + optionally upload a receipt image; booking moves to `awaiting_confirmation` state; therapist gets an email + inbox notification.*
- **E7 — Therapist confirms payment received.** *acceptance: therapist clicks "confirmed" in inbox → booking moves to `confirmed`; both parties get the room link by email.*
- **E8 — Daily.co room creation + session page.** *acceptance: at booking confirmation, server-side call creates a Daily.co room; both parties receive an email with the link; session page embeds the room JS SDK; works on mobile + desktop.*

### Track F — Notifications

Starts as soon as B8 (.env) lands; most templates depend on D and E flows existing.

- **F1 — Resend integration wrapper.** *acceptance: `notifications/email.py` exposes `send(to, subject, template, context)`; Resend API key from env; failing sends logged but never block requests.*
- **F2 — Booking lifecycle emails.** *acceptance: emails sent on booking submitted (→ therapist), payment marked (→ therapist), payment confirmed (→ user), session confirmed with Daily.co link (→ both).*
- **F3 — All email templates in French.** *acceptance: every template (subject + body) is French; plain-text alternative included; tested with a real Resend test send.*

### Track G — Founder admin/ops customizations

Lean on Django admin. Customize only where it pays off.

- **G1 — Therapist verification queue list view.** *acceptance: admin URL filters `TherapistProfile` by `verification_status=pending`; bulk approve/reject actions; sortable by submission date.*
- **G2 — Booking moderation list.** *acceptance: bookings list filterable by state (`pending_payment`, `awaiting_confirmation`, `confirmed`, `completed`, `no_show`, `cancelled`); searchable by user/therapist email.*
- **G3 — Founder dashboard view.** *acceptance: a single admin page showing bookings/week, active therapists this week, completion rate; refreshes on page load (no JS).*

### Track H — Pre-launch hardening

Depends on A3 (lawyer) for legal content; rest is parallelizable.

- **H1 — T&Cs and Privacy Policy pages.** *acceptance: `/legal/terms` and `/legal/privacy` render; content is lawyer-reviewed (depends on A3); linked from footer on every page.*
- **H2 — Disclaimer at booking time.** *acceptance: visible on the booking submit screen ("DzTherapy is not a healthcare provider, ..."); user must explicitly acknowledge before submit succeeds.*
- **H3 — Emergency escalation procedure documented.** *acceptance: `RUNBOOK.md` in repo with step-by-step what to do if a user signals self-harm; Algerian crisis-line phone numbers included; reviewed against A3 legal advice.*
- **H4 — Production hosting decision + setup.** *acceptance: hosting platform locked (Railway / Fly.io / VPS); deploy config committed; first deploy succeeds at a staging URL.*
- **H5 — Domain + production email setup.** *acceptance: production domain live; Resend domain DNS configured (SPF / DKIM / return-path); transactional emails deliver to Gmail and Outlook inboxes (not spam).*
- **H6 — Sentry alerts wired.** *acceptance: Sentry rules configured for unhandled exceptions on `prod` environment; alert delivery (email / Slack / etc.) works end-to-end.*

### Track I — Closed beta launch

The actual launch milestone. Depends on D, E, F, G, H all being green and A1 being green.

- **I1 — Onboard first 10 anchor therapists.** *acceptance: 10 verified `TherapistProfile` records, all live, all with availability set for the next 4 weeks; founder has spoken to each at least once during onboarding.*
- **I2 — End-to-end smoke test of the full booking flow.** *acceptance: signup → browse → book → pay → therapist confirms → session video link works. Tested from two devices (mobile + desktop) on a real Algerian network connection.*
- **I3 — Soft launch — invite-only signups.** *acceptance: signup form gated by invite code; invite codes generated for therapists' existing patients; first 20 invitations sent.*
- **I4 — Feedback loop set up.** *acceptance: post-session feedback form (email + in-app form); founder reviews weekly; issues land in Issues / Technical Debt below.*

## Phase 2 / Deferred (post-MVP — do not start)

Parked here so they're visible but flagged. Each maps to PRD §7 deferrals.

- In-app messaging
- Voice notes
- Search and filters (therapist directory)
- Anonymous display name
- Session notes / EMR-lite
- Reviews and ratings
- Wallet / recharge
- AI intake assistant
- Mobile app wrapper (Capacitor or Hotwire Native — see PRD §13)
- Arabic localization
- Therapist subscription billing (Phase 3 monetization)

## Done

- **2026-05-07** — **B10 — PWA basics.** `/manifest.webmanifest` and `/sw.js` served by [core/views.py](core/views.py) at root scope; templates at [templates/manifest.webmanifest](templates/manifest.webmanifest) and [templates/sw.js](templates/sw.js). Service worker is offline-shell only (network-first for navigations, cache fallback to `/`). [templates/base.html](templates/base.html) registers the SW and links the manifest. Smoke test added for `/manifest.webmanifest`. **Known limitation:** PWA installability requires icons, which are not yet committed (see Issues / Technical Debt).
- **2026-05-07** — **B9 — Sentry SDK.** `sentry-sdk[django]>=2.18` added; init in [config/settings.py](config/settings.py) is conditional on a non-empty `SENTRY_DSN` (silent in dev / CI). `environment` derived from `DEBUG`; `traces_sample_rate=0.0`; `send_default_pii=False`. Verification path documented in [CLAUDE.md §13](CLAUDE.md).
- **2026-05-07** — **B8 — env hygiene.** [config/settings.py](config/settings.py) reads via `django-environ`; `DEBUG`-gated security headers added (HSTS, secure cookies, proxy-ssl header — `SECURE_SSL_REDIRECT` deliberately deferred to the hosting platform). [.env.example](.env.example) polished with grouped sections + production-only commented vars. Production-vs-dev env-var matrix documented in [CLAUDE.md §13](CLAUDE.md).
- **2026-05-07** — **B7 — GitHub Actions CI.** [.github/workflows/ci.yml](.github/workflows/ci.yml) with parallel `lint` and `test` jobs on push to `main` + every pull request. `lint` runs `pre-commit run --all-files`; `test` runs `pytest` against a Postgres 16 service container. pip + pre-commit caches keyed on `pyproject.toml` and `.pre-commit-config.yaml` hashes. Workflow detail in [CLAUDE.md §12](CLAUDE.md). **Follow-up (one-time, GitHub UI when repo is created):** configure branch protection on `main` to require `lint` and `test` checks before merge — the workflow file alone does not block merge.
- **2026-05-07** — **B6 — Lint + format tooling.** Added `ruff>=0.6`, `black>=24.0`, `pre-commit>=3.7` to dev deps. `[tool.ruff]` config (line 88, target py312, rules `E F I B UP DJ`, ignore `E501`) and `[tool.black]` config in `pyproject.toml`. `.pre-commit-config.yaml` with pre-commit-hooks basics + ruff (`--fix`) + black. `make lint` and `make format` targets in Makefile. `make test` still passes (no formatting regressions).
- **2026-05-07** — **B1–B5 — Repo skeleton scaffolded.** Django 5.x project (`config/`, `core/`) + `pyproject.toml` deps + `Makefile` + `docker-compose.yml` (Postgres 16) + `tailwind/input.css` (v4 source) + `templates/base.html` with `{% tailwind_css %}`/HTMX 2.x/Alpine 3.x via CDN + smoke-test home page demonstrating HTMX swap + Alpine counter + `pytest` config in `pyproject.toml` + `core/factories.py::UserFactory` + 2 passing smoke tests. Setup steps documented in [CLAUDE.md §9](CLAUDE.md) and [README.md](README.md#local-development).
- **2026-05-07** — Locked the technical stack: Django 5.x monolith + Templates + HTMX + Alpine + Tailwind (standalone CLI) + PostgreSQL + Daily.co + Resend + Sentry. Canonical details in [PRD §13](algeria_mental_health_saas_prd.md).

## Issues / Technical Debt

- **PWA icons missing.** `manifest.webmanifest` does not include an `icons` array because the brand identity is not yet designed. Lighthouse will report "not installable" until 192×192 and 512×512 PNG icons (and ideally a maskable variant) are committed under `assets/icons/` and referenced from the manifest. Pre-launch followup; blocked on visual identity work.

## Research / Ideas

*(empty — once tasks are scoped with acceptance criteria, they're promoted to Backlog)*
