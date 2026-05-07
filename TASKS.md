# TASKS.md

> Single source of truth for in-flight and queued work on DzTherapy.
> Lifecycle: **Research / Ideas → Backlog → In Progress (cap 2) → Done**.
> Newly discovered issues land in **Issues / Technical Debt** before context-switching.

## In Progress

*(none — project is pre-code)*

## Backlog

*(empty until pre-build validation findings come in — see Research / Ideas)*

## Research / Ideas

### Pre-build validation (driven by PRD §22 — do these *before* writing code)

- **[Highest leverage]** Interview ~10 psychologists in Algiers / Oran on willingness to pay 5,000 DZD/month for tools + leads in 18 months. If <40% say yes, the year-2 monetization model needs a rethink before we build anything.
- Interview ~10 potential users (urban professional women 25–35, French-speaking) on the "pay therapist directly" friction and willingness to book.
- Get an Algerian lawyer to answer PRD §11 questions:
  - #1 — Can a licensed psychologist legally conduct paid sessions via video?
  - #3 — Platform liability if a user self-harms after a session.
  - #5 — Required disclaimers and Terms of Service to limit liability.
  - #6 — Does the pass-through payment model trigger PSP regulation in Algeria?
- Test Daily.co reliability on Algerian 3G/4G networks (Algiers + Oran, two times of day each). If video doesn't work, the product doesn't work.
- Lock in founder runway commitment in writing: months of personal funds available before paid conversion is required.

### Post-validation (only if validation passes)

- Pick the stack: Next.js full-stack (API routes) vs Next.js + FastAPI. Decide once and document the decision in CLAUDE.md §8.
- Set up the repo skeleton: Next.js + Tailwind + auth + Postgres on Supabase or Neon.
- Build the Phase 1 MVP per PRD §6 — user-facing 5 features + therapist-facing 6 features.
- Onboard the first 10 anchor therapists (founder-led outreach, per PRD §15 Step 1).

## Done

*(none yet)*

## Issues / Technical Debt

*(none yet)*
