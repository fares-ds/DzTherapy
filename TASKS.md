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

## Phase 2 / Deferred (post-MVP — do not start)

Each maps to PRD §7 deferrals.

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

- **PWA icons missing.** `manifest.webmanifest` does not include an `icons` array because the brand identity is not yet designed. Lighthouse will report "not installable" until 192×192 and 512×512 PNG icons are committed under `assets/icons/` and referenced from the manifest. Pre-launch followup; blocked on visual identity work.
- **T&Cs / Privacy text is unreviewed.** [templates/core/terms.html](templates/core/terms.html) and [templates/core/privacy.html](templates/core/privacy.html) are placeholders. Replace with lawyer-reviewed copy when A3 lands.
- **Email-template copy for AR/EN.** All transactional templates are FR-only. When Phase 2 brings Arabic, translate `templates/emails/*.{txt,html}` and pick the language from the recipient's preference.
- **Session reminders.** No T-24h or T-1h reminder email yet. Likely needs a periodic worker (Django-Q2 per PRD §13). Phase 2.
- **Booking ICS export.** Not implemented. Patients with poor email habits would benefit from a calendar invite. Defer.
- **Slot collision check is best-effort.** `bookings.views.create_booking` checks for an existing booking at the same `slot_start`, but a near-simultaneous double-submit could race. Acceptable at MVP volume; revisit with `select_for_update` if collisions are observed.

## Research / Ideas

*(empty — once tasks are scoped with acceptance criteria, they're promoted to Backlog)*
