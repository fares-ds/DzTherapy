"""Periodic command — runs nightly via cron / Django-Q2 in Phase 2.

Transitions any CONFIRMED booking whose slot ended at least `--grace-minutes`
ago into COMPLETED. Therapists can flip individual bookings to NO_SHOW in
admin if the patient didn't attend; the default optimism reflects the
common case.

Run:
    python manage.py finalize_bookings
"""

from django.core.management.base import BaseCommand

from bookings.services import auto_finalize_bookings


class Command(BaseCommand):
    help = "Finalize past CONFIRMED bookings as COMPLETED."

    def add_arguments(self, parser):
        parser.add_argument(
            "--grace-minutes",
            type=int,
            default=60,
            help="Minutes after slot_end before auto-completing (default: 60).",
        )

    def handle(self, *args, **options):
        result = auto_finalize_bookings(grace_minutes=options["grace_minutes"])
        self.stdout.write(self.style.SUCCESS(f"Completed: {result['completed']}"))
