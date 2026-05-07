# ARCHITECTURE.md

Technical architecture of the DzTherapy MVP. The PRD ([algeria_mental_health_saas_prd.md](./algeria_mental_health_saas_prd.md)) is the source of truth for product strategy and business model; this document describes how the code is organized.

## Big picture

DzTherapy is a **single Django 5.x monolith**, server-rendered via Django Templates with HTMX + Alpine.js for dynamic UI. There is no SPA, no separate frontend, no microservices. The PRD's "Why Django (not FastAPI, not Next.js)" rationale ([§13](./algeria_mental_health_saas_prd.md#13-technology-stack--locked)) drives every architectural choice here.

The app has two faces glued by a shared booking model:

- **User-facing funnel** — public landing, therapist directory, public profiles, booking flow. Optimized for trust + speed on slow networks (small JS payload, server-rendered HTML).
- **Therapist dashboard** — profile editor, weekly availability, booking inbox, patient list. This is the surface that becomes monetizable in year 2 — over-invested vs the user side per [PRD §6 / §21](./algeria_mental_health_saas_prd.md#6-product-scope).

Money never flows through the platform ([PRD §9](./algeria_mental_health_saas_prd.md#9-payments--pass-through-model)): the user pays the therapist directly off-platform; we only track payment status.

## Apps

```
config/           Project settings, root URLs, WSGI/ASGI
core/             Public landing, T&Cs/Privacy, PWA manifest+SW, founder dashboard view
accounts/         Custom User model with role (end_user | therapist), allauth integration
therapists/       TherapistProfile, Availability, AvailabilityException, dashboard, public list/detail, slot-generation service
bookings/         Booking model + state machine, booking flow views (create / pay / mark / confirm / session), Daily.co integration
notifications/   Resend-or-console email wrapper + booking lifecycle helpers
```

Each app owns its **models, forms, views, urls, services, admin, tests**. Templates live in the project-wide `templates/<app>/` directory rather than per-app — easier overrides, single source of truth for styling.

## Request flow (booking happy path)

```
Visitor lands on /                                        core.views.home
       │
       ├─ Browses /therapeutes/                           therapists.views.therapist_list
       └─ Opens /therapeutes/<slug>/                      therapists.views.therapist_detail
              │  (slot picker rendered server-side from
              │   therapists.services.get_available_slots)
              ▼
Authenticated user clicks a slot
       │
POST /reservations/nouvelle/<slug>/?slot=ISO              bookings.views.create_booking
       │  Booking(state=PENDING_PAYMENT) created
       │  notifications.email.send_booking_submitted → therapist
       ▼
GET /reservations/<id>/paiement/                          bookings.views.payment_instructions
       │  Shows therapist's payment_instructions verbatim
       ▼
POST /reservations/<id>/marquer-paye/                     bookings.views.mark_paid
       │  bookings.services.mark_user_paid()
       │  state=AWAITING_CONFIRMATION
       │  notifications.email.send_payment_marked → therapist
       ▼
Therapist opens /therapeutes/dashboard/messages/          therapists.views.booking_inbox
POST /therapeutes/dashboard/messages/<id>/confirmer-paiement/  therapists.views.confirm_payment
       │  bookings.services.confirm_payment()
       │  state=CONFIRMED
       │  bookings.services.create_daily_room()  → Daily.co REST (or stub URL)
       │  notifications.email.send_booking_confirmed → both parties
       ▼
GET /reservations/<id>/seance/                            bookings.views.session_room
       │  Renders Daily.co iframe at the configured time
```

Each step is a server-rendered page; HTMX is used inside the therapist inbox to swap a row in place when the therapist confirms payment.

## State machines

### `bookings.models.BookingState`

```
PENDING_PAYMENT ──[mark_user_paid]──▶ AWAITING_CONFIRMATION ──[confirm_payment]──▶ CONFIRMED
       │                                       │                                        │
       │                                       │                                        ▼
       └──[cancel]──▶ CANCELLED ◀──[cancel]────┘                                  COMPLETED / NO_SHOW
                                                                                  (admin-driven)
```

Transitions live in `bookings/services.py`. `ACTIVE_STATES` (defined in `bookings.models`) covers everything that occupies a slot for slot-generation purposes (PENDING_PAYMENT, AWAITING_CONFIRMATION, CONFIRMED, COMPLETED). Cancelled / no-show free the slot up.

### `therapists.models.VerificationStatus`

```
PENDING ──[founder approves]──▶ APPROVED   (visible publicly, can receive bookings)
   │
   └──[founder rejects]──▶ REJECTED        (hidden, cannot receive bookings)
```

Transitions are admin-driven (`TherapistProfileAdmin.approve_selected` / `reject_selected`). No automation at MVP — manual review is intentional ([PRD §22 assumption #9](./algeria_mental_health_saas_prd.md#22-validated-vs-unvalidated-assumptions-appendix)).

## External integrations

| Integration | Where | Behavior with empty key |
|---|---|---|
| **Daily.co** (video) | `bookings.services.create_daily_room` | Returns a deterministic stub URL `https://{DAILY_DOMAIN}.daily.co/dz-dev-<uuid>` — booking flow still works end-to-end in dev/CI. |
| **Resend** (email) | `notifications.email._send_via_resend` | Falls back to Django's email backend (console in dev, configurable in prod). |
| **Sentry** (errors) | `config.settings` | Sentry SDK init is conditional on `SENTRY_DSN` — silent in dev. |
| **PostgreSQL** | `config.settings.DATABASES` from `DATABASE_URL` | Required. Docker Compose locally; platform-managed in prod. |

## Slot generation

`therapists.services.get_available_slots(therapist, days=14)` is the only place where the calendar is computed. It:

1. Iterates `Availability` rows (recurring weekly windows).
2. Subtracts `AvailabilityException` rows (specific blocked dates).
3. Subtracts existing `Booking`s in `ACTIVE_STATES`.
4. Chunks the remaining time into `session_duration_minutes` blocks.
5. Returns `[(aware_start_dt, aware_end_dt), ...]` sorted ascending.

Pure function, easy to test (`therapists/tests/test_services.py`).

## Templates

Project-wide layout in `templates/base.html` provides:
- Tailwind v4 CSS via the standalone CLI (no Node).
- HTMX 2.x + Alpine.js 3.x via CDN.
- PWA manifest link + service worker registration (offline-shell only).
- Auth-aware nav (logged-in/out variants, plus role-specific links for therapist + staff).
- Footer linking T&Cs and Privacy.

allauth templates extend `templates/account/base.html` which itself extends `base.html`, so login/signup/etc. pages get the same chrome.

## i18n

`LANGUAGE_CODE = "fr"` ([config/settings.py](./config/settings.py)) and all source strings are written in French. `LOCALE_PATHS = [BASE_DIR / "locale"]` is configured for future Arabic translations (Phase 2 per [PRD §8](./algeria_mental_health_saas_prd.md#8-localization-requirements)).

Source strings use `{% trans %}` and `gettext_lazy` so when Arabic is added, only `.po` files need to land — no template changes.

## Testing

- `pytest + pytest-django + factory_boy`. Config in `pyproject.toml`.
- `core/factories.py` and `therapists/tests/factories.py` provide `UserFactory`, `TherapistUserFactory`, `TherapistProfileFactory`, `AvailabilityFactory`.
- `bookings/tests/test_flow.py` covers the full booking happy path end-to-end.
- `therapists/tests/test_services.py` covers slot-generation edge cases.
- CI ([.github/workflows/ci.yml](./.github/workflows/ci.yml)) runs lint + test against a real Postgres service container.

## What's deferred

Per [PRD §7](./algeria_mental_health_saas_prd.md#7-features-not-included-in-mvp) — see also [TASKS.md](./TASKS.md) "Phase 2 / Deferred":

- **In-app messaging, voice notes** — would need a queue + WebSockets (see PRD §14 future architecture).
- **Search & filters** — flat list is fine while therapist count is in the dozens.
- **AI features** — explicitly deferred to Phase 2+ per PRD §12.
- **Therapist subscription billing** — Phase 3 per PRD §16 (the only revenue stream when it lands).
- **Mobile native apps** — PWA at MVP and Phase 2; Capacitor / Hotwire Native are the planned wrappers for Phase 3+ ([PRD §13](./algeria_mental_health_saas_prd.md#13-technology-stack--locked)).
- **Arabic UI** — Phase 2; the i18n machinery is wired now to make the addition cheap.

## Operational

- **Local dev**: `make install && make db-up && make migrate && make tailwind && make dev`.
- **Tests**: `make test`.
- **Lint / format**: `make lint` / `make format`. Pre-commit hooks enforce on commit.
- **CI**: GitHub Actions runs the same lint + test on every PR.
- **Founder dashboard**: `/admin/dztherapy/dashboard/` — staff-only view of the metrics in PRD §17 (months 0–6).
- **Emergency procedures**: see [RUNBOOK.md](./RUNBOOK.md).
