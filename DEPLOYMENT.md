# DEPLOYMENT.md

How to take DzTherapy from a local clone to a live `dztherapy.example` URL. The hosting platform is deferred (per [PRD §13](./algeria_mental_health_saas_prd.md)) — this document covers the patterns that apply on **Railway**, **Fly.io**, and a **self-hosted VPS**.

## Prerequisites (one-time)

| What | Where | Notes |
|---|---|---|
| Algerian legal entity | SARL / SPA / auto-entrepreneur | Per PRD §11 q4 — answered before launch |
| Domain | dztherapy.example (or chosen) | Registrar + DNS access |
| Postgres 16 | Platform-managed or VPS-installed | 1 GB+ disk, automated backups |
| Resend account | resend.com | Free tier = 3k/mo; verify a sending domain |
| Sentry account | sentry.io | Free tier = 5k events/mo, one project |
| Daily.co account | daily.co | Free tier = enough for early bookings |
| GitHub repo + Actions enabled | for CI | Branch protection on `main` (CLAUDE.md §12) |

## Required env vars in production

Replicates [.env.example](./.env.example) but populated. Set all of these in the hosting platform's secret store — never commit.

```
DEBUG=False
SECRET_KEY=<long random secret; never commit>
DATABASE_URL=<platform-issued Postgres URL>
ALLOWED_HOSTS=dztherapy.example,www.dztherapy.example
ACCOUNT_EMAIL_VERIFICATION=mandatory     # default for non-DEBUG; set to "optional" only intentionally
DEFAULT_FROM_EMAIL=DzTherapy <hello@dztherapy.example>
RESEND_API_KEY=<your Resend key>
DAILY_API_KEY=<your Daily.co key>
DAILY_DOMAIN=<your-daily-subdomain>
SENTRY_DSN=<your Sentry project DSN>
```

## Build steps the platform must run on every deploy

```bash
pip install -e .                                    # install pinned-range deps
python manage.py migrate --noinput                   # apply schema
python manage.py collectstatic --noinput             # WhiteNoise reads from staticfiles/
python manage.py tailwind build                      # produces assets/css/tailwind.css before collectstatic in prod
```

**Run order matters:** `tailwind build` must run *before* `collectstatic` so the compiled CSS is in `assets/` when `collectstatic` copies static files into `staticfiles/`. If your platform runs in an order you can't control, run `tailwind build` in a build hook and `collectstatic` in a release hook.

## Static files — WhiteNoise

Already wired in [config/settings.py](./config/settings.py):
- WhiteNoise middleware is mounted right after `SecurityMiddleware`.
- `STORAGES.staticfiles` uses `whitenoise.storage.CompressedManifestStaticFilesStorage` when `DEBUG=False` — gzip + brotli + content-hashed filenames for long cache + cache-bust.

You don't need a separate CDN at MVP volume. Add Cloudflare in front later if egress cost becomes a concern.

## Periodic jobs

Two management commands need scheduling:

| Command | Cadence | Effect |
|---|---|---|
| `python manage.py send_reminders` | hourly | Sends T-24h reminder email to user + therapist for upcoming CONFIRMED bookings (idempotent — `Booking.reminder_sent_at` prevents repeats) |
| `python manage.py finalize_bookings` | nightly | Transitions CONFIRMED bookings whose slot ended ≥ 60 min ago to COMPLETED |

### On Railway / Fly.io / Render

Most platforms have a "Cron Jobs" or "Scheduled Tasks" feature. Configure two entries:

```
hourly:  python manage.py send_reminders
nightly: python manage.py finalize_bookings
```

Both are short (<5 s on small data sets) and idempotent — safe to retry.

### On a VPS

```cron
# /etc/cron.d/dztherapy
0 * * * *  appuser  cd /srv/dztherapy && /srv/dztherapy/.venv/bin/python manage.py send_reminders >> /var/log/dztherapy/reminders.log 2>&1
30 3 * * * appuser  cd /srv/dztherapy && /srv/dztherapy/.venv/bin/python manage.py finalize_bookings >> /var/log/dztherapy/finalize.log 2>&1
```

When Phase 2 brings Django-Q2 (per PRD §13), these become scheduled tasks managed in-process and the cron entries go away.

## Database

- **Backups:** verify the platform takes daily automated backups. Test a restore quarterly (RUNBOOK §database-backup).
- **Migrations:** every release must run `manage.py migrate` before serving traffic. Most platforms do this in a release hook.
- **Connection pooling:** at MVP volume, Django's default per-process pool is fine. Add PgBouncer if you ever spawn >10 workers.

## Resend (transactional email)

1. Create the Resend account, verify the sending domain (`dztherapy.example`).
2. Add SPF, DKIM, return-path DNS records as Resend instructs.
3. Test deliverability: `python manage.py shell` →

```python
from notifications.email import send
send(
    to="your-personal@gmail.com",
    subject="DzTherapy delivery test",
    template="booking_submitted",
    context={"booking": fake_booking},
)
```

4. Verify the email lands in **inbox**, not spam, on Gmail + Outlook + ProtonMail. SPF + DKIM + return-path is what gets you out of spam folders.

## Sentry

1. Create the Sentry project. Set the DSN as `SENTRY_DSN` env var.
2. Trigger a deliberate exception once after deploy:

```bash
ssh into-prod
python manage.py shell
>>> 1/0   # ZeroDivisionError → should appear in Sentry
```

3. Configure alert rule: "First seen exception in `prod` environment within last 5 min → email founder."
4. Set release tracking optional — not on free tier's quota.

## Branch protection

(Repeats CLAUDE.md §12 for completeness.)

After pushing the repo to GitHub: **Settings → Branches → Branch protection rules → Add rule** for `main`:
- Require status checks to pass before merging: select `lint` and `test`.
- Require branches to be up to date before merging.
- Optional: require a PR review for solo work, otherwise just self-merge.

Without this, the CI workflow runs but a red check doesn't block the merge button.

## Smoke test after deploy

```bash
# Anonymous probe of public surface
curl -I https://dztherapy.example/
curl -I https://dztherapy.example/therapeutes/
curl -I https://dztherapy.example/accounts/login/
curl -I https://dztherapy.example/manifest.webmanifest
curl -I https://dztherapy.example/admin/login/

# Then log in to /admin/, create one therapist, set availability, log out,
# sign up as a patient, walk the full booking flow end-to-end.
```

## Pre-launch checklist

- [ ] All §11 PRD lawyer questions have written answers.
- [ ] T&Cs and Privacy pages replaced with lawyer-reviewed copy (replace `templates/core/terms.html` and `privacy.html`).
- [ ] `RUNBOOK.md` Algerian crisis-line numbers verified current.
- [ ] At least 5 anchor therapists onboarded with availability set for the next 4 weeks.
- [ ] Daily.co tested on real Algerian 3G + 4G in two cities (PRD §22 A4).
- [ ] Founder runway commitment in writing (PRD §22 A5).
- [ ] Sentry alert delivery tested (real email arriving).
- [ ] Resend deliverability tested (inbox not spam, Gmail + Outlook).
- [ ] Backup → restore drill done at least once.
- [ ] Manual end-to-end booking smoke test on prod.
- [ ] PWA icons added to `assets/icons/` and referenced from `manifest.webmanifest`.

When the boxes are ticked, soft-launch via invite-only (TASKS.md I3).
