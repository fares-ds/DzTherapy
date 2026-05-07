# TASKS.md

> Single source of truth for in-flight and queued work on DzTherapy.
> Lifecycle: **Research / Ideas → Backlog → In Progress (cap 2) → Done**.
> Newly discovered issues land in **Issues / Technical Debt** before context-switching.

## In Progress (cap 2)

*(none — MVP scope shipped; pre-launch work waits on Track A)*

## Backlog

> The MVP code (Tracks B–G + most of H) shipped in one autonomous build pass. The remaining backlog is dominated by **Track A** — founder validation work that gates the legitimacy of what was built — plus deploy-time hardening (H4–H6).

### Track A — Pre-build validation (founder work, non-coding)

Maps 1:1 to PRD §22. Findings here can change the product/business model.

- **A1 — 10 therapist interviews on willingness to pay (highest leverage).** *acceptance: ≥10 conversations completed; notes saved per-interview in `validation/therapist-interviews/`; quantified result on "would you pay 5,000 DZD/mo for this in 18 months?"; `SUMMARY.md` with go/no-go recommendation. If <40% yes, model needs rethink before further D-track work.*
- **A2 — 10 user interviews (urban professional women 25–35, French-speaking).** *acceptance: ≥10 conversations completed; notes in `validation/user-interviews/`; quantified result on willingness to book + tolerance for "pay therapist directly" friction; `SUMMARY.md`.*
- **A3 — Lawyer engagement on PRD §11 questions #1, #3, #5, #6.** *acceptance: written lawyer response to each of the four questions saved in `validation/legal/`; clear go/no-go for the pass-through payment model.*
- **A4 — Daily.co reliability test on Algerian mobile networks.** *acceptance: 2 sessions × 2 cities (Algiers, Oran) × 2 times of day; results documented (latency, drop rate, audio/video quality on 3G + 4G); decision to proceed with Daily.co or evaluate LiveKit.*
- **A5 — Founder runway commitment in writing.** *acceptance: written commitment of months-of-personal-funds available; stored in `validation/founder-runway.md`.*

### Track H — Pre-launch hardening (remaining)

H1 / H2 / H3 already shipped (T&Cs/Privacy stubs, booking-time disclaimer, RUNBOOK).

- **H1-followup — Replace placeholder T&Cs/Privacy with lawyer-reviewed copy.** *blocked on A3.*
- **H4 — Production hosting decision + setup.** *acceptance: hosting platform locked (Railway / Fly.io / VPS); deploy config committed; first deploy succeeds at a staging URL.*
- **H5 — Domain + production email setup.** *acceptance: production domain live; Resend domain DNS configured (SPF / DKIM / return-path); transactional emails deliver to Gmail and Outlook inboxes (not spam).*
- **H6 — Sentry alerts wired.** *acceptance: Sentry rules configured for unhandled exceptions on `prod` environment; alert delivery (email / Slack) works end-to-end.*

### Track I — Closed beta launch

Depends on Track A completion + H4/H5/H6.

- **I1 — Onboard first 10 anchor therapists.** *acceptance: 10 verified `TherapistProfile` records, all live, all with availability set for the next 4 weeks; founder has spoken to each at least once during onboarding.*
- **I2 — End-to-end smoke test on real Algerian network.** *acceptance: signup → browse → book → pay → therapist confirms → session video link works on mobile + desktop, on 3G/4G in-country.*
- **I3 — Soft launch — invite-only signups.** *acceptance: signup form gated by invite code; invite codes generated for therapists' existing patients; first 20 invitations sent.*
- **I4 — Feedback loop set up.** *acceptance: post-session feedback form (email + in-app form); founder reviews weekly; issues land in Issues / Technical Debt below.*

## Phase 2 — Engagement (in flight)

Per [PRD §20](algeria_mental_health_saas_prd.md). Passes 1 + 2 shipped 2026-05-07 — see Done. Remaining passes:

- **Voice notes** (depends on messaging — extends `Message` with an audio file field)
- **Session notes / EMR-lite** for therapists — strengthens year-2 monetization hook
- **Reviews and ratings** (cautiously — gameable at low volume)
- **Arabic localization** (UI gettext + RTL)
- **AI intake assistant** (optional per PRD §12)
- **Real-time messaging** (Redis + WebSockets to replace 5s HTMX polling — PRD §14; defer until polling pressure justifies it)

## Phase 3+ deferred

- Wallet / recharge
- Mobile app wrapper (Capacitor / Hotwire Native — PRD §13)
- Therapist subscription billing (Phase 3 monetization, PRD §16)

## Done

- **2026-05-07** — **Phase 2 Pass 2 — In-app messaging (HTMX-poll, no Redis yet)**. New `messaging` app with `Conversation` (1:1 patient ↔ therapist, unique constraint) and `Message` (sender, body, created_at, notified_at) models. Patients can start a conversation from a therapist's public profile (`/messages/nouvelle/<slug>/`); therapists can only initiate with users who have an existing booking. Thread page at `/messages/<uuid>/` polls `_messages_partial.html` every 5 s via HTMX; sending a message HTMX-swaps the new list back into the thread without full reload. Email notifications throttled — recipients online inside the last 30 min skip the email since they'll see the message in-app. New `notifications.email.send_new_message` + FR `emails/new_message.{txt,html}` (uses the brand `_header.html`). Header nav grows a "Messages" link with an unread badge driven by a new `messaging.context_processors.unread_messages`. "Envoyer un message" CTA on therapist detail page (logged-in non-therapist users only). Admin gets `Conversation` + `Message` registered with read-only inline. Tests: 59 passing (up from 42) — covers role-gated initiation, third-party rejection, throttle behavior, unread counting, mark-seen, view-level isolation. Real-time WebSocket upgrade per PRD §14 stays deferred until polling pressure justifies adding Redis.
- **2026-05-07** — **Visual asset wiring + brand system pinned**. Tailwind theme extended with `accent-{100,500,700}` (`#5b8a8a` muted teal — outside the candle/sage/terracotta wellness cliché per PRD positioning). [base.html](templates/base.html) now serves a real `<img>` wordmark in the header, declares `apple-touch-icon` + `favicon-32` links, and emits a full OG/Twitter meta block (`og:image` built via `request.scheme://request.get_host` + `{% static %}`). [manifest.webmanifest](templates/manifest.webmanifest) gained the `icons` array (192, 512, 512-maskable, apple-touch). Landing page rebuilt as a 2-column hero + "Comment ça marche" 3-step section. Therapist directory and detail page swap the initial-letter slate box for `default-avatar.svg` and render `badge-verified.svg` next to approved therapists. Empty-state illustrations wired to all five `{% empty %}` blocks (directory / inbox / availability / patient list / my_bookings). 403/404/500 each render their error illustration (500 stays self-contained — references the SVG via `{% static %}` served by WhiteNoise). Six transactional emails now `{% include "emails/_header.html" %}` for a logo header; new `SITE_URL` setting (env-driven, default `http://localhost:8000`) is injected into every email context by `notifications.email.send()` so absolute URLs work without `request`. Asset list saved at `~/.claude/plans/collect-all-the-requirement-rippling-catmull.md` for handoff to Claude Design.
- **2026-05-07** — **Phase 2 Pass 1 — search, filters, anonymous mode, account settings, my-bookings**. Public therapist directory at `/therapeutes/` now has a sticky filter sidebar (search box, gender, language, max price) with HTMX-driven swap of just the result grid (no full reload). New `Gender` enum on `TherapistProfile` (PRD §8 cultural-adaptation gap closed) — both signup form and profile editor expose it. New `User.display_name` (optional, max 64) + `User.public_name` property; therapist booking inbox + patient list now show `public_name` with email below as secondary contact when display_name is set. New `/mon-compte/` page (`accounts.views.account_settings`) for end users to edit display name, with links to allauth's password-change and email-management views. New `/reservations/` page (`bookings.views.my_bookings`) listing upcoming + past bookings with state badges and contextual CTAs (join session / payment instructions). Header nav grows "Mes réservations" + "Mon compte" links for end users. Tests: 42 passing (up from 31) — covers search across all 4 filters, HTMX partial response, display_name persistence + public_name fallback, my_bookings past/upcoming split.
- **2026-05-07** — **Security & production-readiness pass**. `django-ratelimit` decorators on `therapist_signup` (5/h per IP), `create_booking` / `mark_paid` / `cancel_booking` (20–30/h per user), plus allauth's built-in rate limits on login_failed / signup / send_email. WhiteNoise wired into MIDDLEWARE with `CompressedManifestStaticFilesStorage` in prod (gzip + brotli + content-hashed names) and `WHITENOISE_USE_FINDERS` in dev (no `collectstatic` needed). `ACCOUNT_EMAIL_VERIFICATION` is now env-driven, defaults to `optional` in DEBUG and `mandatory` in prod. Allauth templates (login, signup, logout, password_reset, password_reset_done, email_confirm) overridden with FR-styled cards extending `account/base.html`. Cross-user isolation tests added (therapist B cannot confirm/decline therapist A's bookings; end-user gets 403 on therapist dashboard; third-party gets 400 on session room). SVG favicon. New [DEPLOYMENT.md](DEPLOYMENT.md) covering hosting candidates, env-var matrix, build steps, periodic-job scheduling for `send_reminders` + `finalize_bookings`, Resend domain auth, Sentry verification, and a pre-launch checklist. Tests: 31 passing (up from 25).
- **2026-05-07** — **Robustness pass — decline / cancel / reminders / finalize / receipt validation / slot-collision**. Therapist can now decline a booking from the inbox (HTMX swap) → patient gets a French email. User can self-cancel from the payment-instructions page while in `pending_payment` or `awaiting_confirmation` → therapist gets notified. Slot collisions are now blocked at the DB layer via a partial unique constraint (`unique_active_booking_slot`) and at the application layer via `select_for_update` inside an atomic block. Receipt uploads validate file type (JPG/PNG/GIF/WEBP/PDF) and size (≤5 MB) at form level. Two new periodic management commands: `python manage.py send_reminders` (T-24h, idempotent via `Booking.reminder_sent_at`) and `python manage.py finalize_bookings` (CONFIRMED → COMPLETED after `slot_end + grace`). 404/403 templates extend `base.html`; 500 is self-contained for safety. New `python manage.py seed_demo` creates 3 approved therapists + 1 patient so fresh installs aren't empty. Tests: 25 passing (up from 10) — covers all new transitions, validation rejection paths, slot-collision constraint at DB layer, and reminder idempotency.
- **2026-05-07** — **Track G (admin/ops) + H1/H2/H3 (hardening)**. Therapist verification queue + booking moderation in Django admin (with bulk approve/reject and state actions). Founder dashboard view at `/admin/dztherapy/dashboard/` with weekly bookings, active therapists, completion rate, by-state breakdown. T&Cs (`/conditions/`) and Privacy (`/confidentialite/`) placeholder pages — flagged as not yet lawyer-reviewed. Booking-time disclaimer enforced via `BookingNotesForm.accept_disclaimer` (required checkbox). [RUNBOOK.md](RUNBOOK.md) with crisis-line numbers, verification incidents, payment disputes, Daily.co outage procedure, backup/restore notes.
- **2026-05-07** — **Tracks D + E + F (booking flow + notifications)**. Therapist signup with role-gated dashboard (profile editor, weekly availability with exceptions, booking inbox with HTMX live updates, patient list). Public therapist list + per-therapist profile with embedded slot picker (server-rendered from `therapists.services.get_available_slots`). Booking lifecycle (`pending_payment → awaiting_confirmation → confirmed → completed/no_show/cancelled`), pass-through payment screen (no money flows through platform), receipt upload, Daily.co room creation with stub-fallback in dev, session room with embedded iframe. Resend HTTP API integration with Django-console fallback; French HTML+text email templates for `booking_submitted`, `payment_marked`, `booking_confirmed`. Tests: 10 passing covering signup, slot generation (incl. blocked dates and pending-status filter), and full booking flow end-to-end.
- **2026-05-07** — **Track C — Auth + custom User + TherapistProfile + allauth + French + base nav.** `accounts.User` with `email` as `USERNAME_FIELD` and `role` field. `therapists.TherapistProfile` 1:1. `django-allauth` v65 wired with email-only auth. Default locale set to `fr`, `LOCALE_PATHS` configured. Base template with auth-aware nav (logged-in/out, therapist-only and staff-only links), footer linking T&Cs and Privacy. AUTH_USER_MODEL change required a fresh DB; migrations regenerated.
- **2026-05-07** — **B10 — PWA basics.**
- **2026-05-07** — **B9 — Sentry SDK.**
- **2026-05-07** — **B8 — env hygiene.**
- **2026-05-07** — **B7 — GitHub Actions CI.**
- **2026-05-07** — **B6 — Lint + format tooling.**
- **2026-05-07** — **B1–B5 — Repo skeleton scaffolded.**
- **2026-05-07** — Locked the technical stack: Django 5.x monolith + Templates + HTMX + Alpine + Tailwind (standalone CLI) + PostgreSQL + Daily.co + Resend + Sentry. Canonical details in [PRD §13](algeria_mental_health_saas_prd.md).

## Issues / Technical Debt

- **Visual asset files pending.** Templates now reference 25 static assets across `assets/{brand,icons,social,landing,avatars,empty,badges,errors,email}/` (logo, favicon-32, apple-touch-icon, PWA icons 192/512/maskable, og-default, hero, 3-step icons, default avatar, 5 empty-states, verified badge, 3 error illustrations, email-logo). Plan + dimensions in `~/.claude/plans/collect-all-the-requirement-rippling-catmull.md`. Until Claude Design generates them, broken-image icons render in dev — this is expected, not a regression. Lighthouse PWA installability stays red until the 192/512/maskable PNGs land.
- **T&Cs / Privacy text is unreviewed.** [templates/core/terms.html](templates/core/terms.html) and [templates/core/privacy.html](templates/core/privacy.html) are placeholders. Replace with lawyer-reviewed copy when A3 lands.
- **Email-template copy for AR/EN.** All transactional templates are FR-only. When Phase 2 brings Arabic, translate `templates/emails/*.{txt,html}` and pick the language from the recipient's preference.
- **Session reminders.** No T-24h or T-1h reminder email yet. Likely needs a periodic worker (Django-Q2 per PRD §13). Phase 2.
- **Booking ICS export.** Not implemented. Patients with poor email habits would benefit from a calendar invite. Defer.
- **Slot collision check is best-effort.** `bookings.views.create_booking` checks for an existing booking at the same `slot_start`, but a near-simultaneous double-submit could race. Acceptable at MVP volume; revisit with `select_for_update` if collisions are observed.

## Research / Ideas

*(empty — once tasks are scoped with acceptance criteria, they're promoted to Backlog)*
