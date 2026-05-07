"""Periodic command — runs hourly via cron / Django-Q2 in Phase 2.

Sends a T-24h reminder email to both parties for each upcoming CONFIRMED
booking. Idempotent: `Booking.reminder_sent_at` prevents double-sends.

Run:
    python manage.py send_reminders
    python manage.py send_reminders --window-hours 2   # T-2h reminder run
"""

from django.core.management.base import BaseCommand

from bookings.services import send_session_reminders


class Command(BaseCommand):
    help = "Send reminder emails for upcoming confirmed bookings."

    def add_arguments(self, parser):
        parser.add_argument(
            "--window-hours",
            type=int,
            default=24,
            help="Hours ahead of the slot to consider as the reminder window (default: 24).",
        )
        parser.add_argument(
            "--lookahead-hours",
            type=int,
            default=25,
            help="Upper bound of the reminder window (default: 25).",
        )

    def handle(self, *args, **options):
        sent = send_session_reminders(
            window_hours=options["window_hours"],
            lookahead_hours=options["lookahead_hours"],
        )
        self.stdout.write(self.style.SUCCESS(f"Reminders sent: {sent}"))
