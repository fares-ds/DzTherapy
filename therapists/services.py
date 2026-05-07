"""Slot generation and booking helpers for therapists."""

from datetime import datetime, timedelta

from django.utils import timezone

from bookings.models import ACTIVE_STATES
from therapists.models import TherapistProfile


def get_available_slots(
    therapist: TherapistProfile, days: int = 14
) -> list[tuple[datetime, datetime]]:
    """Return future bookable (start, end) pairs for the next ``days``.

    Subtracts blocked dates and existing active bookings.
    """
    if not therapist.is_approved:
        return []

    slot_minutes = therapist.session_duration_minutes
    now = timezone.localtime()
    today = now.date()

    weekly: dict[int, list[tuple]] = {}
    for av in therapist.availability_slots.all():
        weekly.setdefault(av.weekday, []).append((av.start_time, av.end_time))

    blocked_dates = set(
        therapist.availability_exceptions.values_list("date", flat=True)
    )

    booked_starts = set(
        therapist.bookings.filter(
            state__in=ACTIVE_STATES,
            slot_start__date__gte=today,
        ).values_list("slot_start", flat=True)
    )

    slots: list[tuple[datetime, datetime]] = []
    tz = timezone.get_current_timezone()

    for day_offset in range(days):
        date = today + timedelta(days=day_offset)
        if date in blocked_dates:
            continue
        for start_t, end_t in weekly.get(date.weekday(), []):
            slot_dt = datetime.combine(date, start_t, tzinfo=tz)
            window_end = datetime.combine(date, end_t, tzinfo=tz)
            while slot_dt + timedelta(minutes=slot_minutes) <= window_end:
                next_dt = slot_dt + timedelta(minutes=slot_minutes)
                if slot_dt > now and slot_dt not in booked_starts:
                    slots.append((slot_dt, next_dt))
                slot_dt = next_dt

    slots.sort()
    return slots
