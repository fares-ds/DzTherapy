# DzTherapy

Therapy / mental wellness SaaS for the Algerian market.

Free for users and therapists in years 1–2; therapist monthly subscription only from year 2 (no per-session commission, ever).

## Status

**MVP functional.** The full booking flow works end-to-end: therapist signup → manual verification → public profile → user signup → slot picking → "pay therapist directly" instructions → "I have paid" → therapist confirms → Daily.co video link delivered by email → session room. French throughout.

What's wired:
- Custom email-first auth via `django-allauth`, with `User.role` distinguishing end users from therapists.
- Public therapist directory + per-therapist profile page with embedded slot picker.
- Therapist dashboard (profile editor, weekly availability, booking inbox, patient list).
- Booking lifecycle (`pending_payment → awaiting_confirmation → confirmed → completed/no_show`) with HTMX-driven inbox updates.
- Pass-through payment flow — the platform never holds money; the booking records "I paid" / "received" markers only.
- Daily.co integration with stub URLs in dev (no API key required) and real REST calls when `DAILY_API_KEY` is set.
- Resend email integration with HTML + plain-text French templates for every lifecycle event; falls back to Django's console backend when `RESEND_API_KEY` is empty.
- Founder admin dashboard at `/admin/dztherapy/dashboard/` with weekly bookings, active therapists, completion rate.
- Sentry integration (silent unless `SENTRY_DSN` is set).
- T&Cs / Privacy stubs (lawyer review still pending — PRD §11) and a `RUNBOOK.md` for emergency procedures.

What's deferred (see [TASKS.md](./TASKS.md) and [PRD §7](./algeria_mental_health_saas_prd.md#7-features-not-included-in-mvp)): in-app messaging, voice notes, search/filters, anonymous mode, EMR-lite session notes, ratings, wallet/recharge, AI features, Arabic UI, mobile-native wrappers, therapist subscription billing.

## Local development

Prerequisites: **Python 3.12**, **Docker**.

```bash
git clone <repo-url> dztherapy && cd dztherapy
python -m venv .venv && source .venv/bin/activate
make install
cp .env.example .env

make db-up                    # Postgres in Docker
make migrate                  # apply schema
.venv/bin/python manage.py createsuperuser   # founder admin account
make tailwind                 # in another terminal — keeps watching
make dev                      # http://localhost:8000
```

Other targets:
```bash
make test          # pytest (10 tests, ~1.5s)
make lint          # ruff + black, no changes
make format        # auto-fix lint + format
make help          # full target list
```

## Key URLs

| URL | Purpose |
|---|---|
| `/` | Public landing |
| `/therapeutes/` | Curated therapist directory |
| `/therapeutes/<slug>/` | Public therapist profile + slot picker |
| `/therapeutes/inscription/` | Therapist signup |
| `/therapeutes/dashboard/profil/` | Therapist's own profile editor |
| `/therapeutes/dashboard/disponibilites/` | Weekly availability + blocked dates |
| `/therapeutes/dashboard/messages/` | Booking inbox |
| `/therapeutes/dashboard/patients/` | Patient list |
| `/reservations/<uuid>/paiement/` | Payment instructions |
| `/reservations/<uuid>/seance/` | Daily.co session room |
| `/admin/` | Django admin (verify therapists, moderate bookings) |
| `/admin/dztherapy/dashboard/` | Founder operational metrics |
| `/conditions/` · `/confidentialite/` | T&Cs / Privacy (placeholders pending lawyer review) |

## Where to look

- **Product strategy and scope**: [algeria_mental_health_saas_prd.md](./algeria_mental_health_saas_prd.md) — the source of truth.
- **Working guidelines for contributors / AI assistants**: [CLAUDE.md](./CLAUDE.md) — project guards in §7, dev workflow in §9, conventions in §11, env vars in §13.
- **Code architecture**: [ARCHITECTURE.md](./ARCHITECTURE.md).
- **In-flight and queued work**: [TASKS.md](./TASKS.md).
- **Emergency procedures (founder ops)**: [RUNBOOK.md](./RUNBOOK.md).
