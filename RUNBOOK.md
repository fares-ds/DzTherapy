# RUNBOOK.md

Operational procedures for the DzTherapy founder team. Update as situations are encountered.

## Emergency: user signals self-harm or crisis

If you observe (in any channel — booking notes, email, social media) that a user is in immediate danger or expresses suicidal ideation:

1. **Do not delay.** Reply immediately, in French, with the local crisis-line numbers:
   - **SOS Algérie (écoute psychologique)** : 0560 001 555
   - **Numéro d'urgence général** : 14 (Algérie)
   - **SAMU** : 115
2. Forward the message to a clinical advisor (founder mental-health partner) for consultation.
3. Do **not** attempt to provide therapy yourself; we are not a healthcare provider (per [PRD §11](./algeria_mental_health_saas_prd.md) and the user-facing T&Cs).
4. Document the incident in `validation/incidents/<YYYY-MM-DD>-<short>.md` with: timestamp, what was observed, what we did, who we escalated to.
5. If a session is imminent, contact the assigned therapist directly (out-of-band) so they're aware before the call.

These numbers must be verified annually — local crisis lines change. Last verified: **(set on first launch)**.

## Therapist verification incident

If we discover after approval that a therapist's credentials were misrepresented:

1. Set `verification_status=rejected` in admin (this hides them from the public list immediately).
2. Notify all users with active bookings (state in `pending_payment`, `awaiting_confirmation`, `confirmed`) by email — apologize, refund instructions if any pre-payment occurred.
3. Document under `validation/incidents/`.
4. If the issue is criminal (impersonation, abuse), preserve all data and consult legal.

## Booking dispute (user paid, therapist denies receiving)

The pass-through payment model means **DzTherapy never holds money**, so we cannot refund. But:

1. Open the booking in admin (`/admin/bookings/booking/<id>/`).
2. Inspect `receipt` (uploaded by user) and `user_marked_paid_at` timestamp.
3. Mediate via email: ask therapist for their bank statement / Edahabia transaction history matching the receipt.
4. If unresolved, mark booking as `cancelled` with a note in `cancellation_reason`.
5. Repeat-offender therapists → escalate to verification review (above).

## Daily.co outage during a session

1. Check Daily.co status page.
2. If their service is degraded, message both parties via Resend with a fallback recommendation: WhatsApp video / Google Meet / phone.
3. Allow the booking to be marked `completed` even without using our video room; the value to the therapist is in lead generation, not the SFU.

## Database backup / restore

In production:
- Hosting platform (Railway / Fly.io) provides automated daily backups — verify they're enabled.
- Manual snapshot before any schema-affecting deploy: `pg_dump $DATABASE_URL > backups/<timestamp>.sql`.
- Restore drill: tested **(date the restore drill was done)**.

Locally:
- `make db-down` removes the volume (`-v` flag in compose) and wipes data.
- `make db-up && make migrate` recreates an empty schema.

## Account take-over / suspicious login

If a user reports their account was accessed without permission:

1. Force a password reset: `manage.py shell` → `user.set_unusable_password(); user.save()` — they'll need to use the password-reset flow.
2. Invalidate all sessions: `Session.objects.filter(...)`.
3. Check Sentry for unusual error patterns near the timestamp.
4. Document the incident.

## Sentry alert noise

If a deploy spikes the Sentry quota:
- Lower `traces_sample_rate` (already 0.0; this is for `error_sample_rate` if we add one).
- Use Sentry's filter rules to ignore expected exceptions.
- Don't disable Sentry to silence — root-cause the spike.

## What this RUNBOOK is NOT

- Not legal advice. The §11 questions in the PRD must be answered by an Algerian lawyer before launch (Track A3).
- Not a substitute for a clinical advisor. Crisis-handling procedures should be vetted by a licensed professional before launch (also Track A3 follow-up).
