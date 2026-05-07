"""Booking lifecycle helpers — Daily.co room creation, state transitions."""

from __future__ import annotations

import logging
from datetime import timedelta

import requests
from django.conf import settings
from django.utils import timezone

from bookings.models import ACTIVE_STATES, Booking, BookingState
from notifications import email as notify

log = logging.getLogger(__name__)


def create_daily_room(booking: Booking) -> str:
    """Provision a Daily.co room for the booking and return its URL.

    Falls back to a deterministic stub URL when ``DAILY_API_KEY`` is unset
    (dev / CI). Network failures also fall back gracefully so the booking
    can still complete — the operator can repair the link later.
    """
    if not settings.DAILY_API_KEY:
        return f"https://{settings.DAILY_DOMAIN}.daily.co/dz-dev-{booking.id}"

    try:
        # Room expires 4h after the session window so it can't be misused.
        expiry = int(booking.slot_end.timestamp() + 4 * 3600)
        response = requests.post(
            "https://api.daily.co/v1/rooms",
            headers={"Authorization": f"Bearer {settings.DAILY_API_KEY}"},
            json={
                "properties": {
                    "exp": expiry,
                    "max_participants": 2,
                    "enable_chat": True,
                }
            },
            timeout=10,
        )
        response.raise_for_status()
        return response.json()["url"]
    except Exception:
        log.exception("Daily.co room creation failed for booking %s", booking.id)
        return f"https://{settings.DAILY_DOMAIN}.daily.co/dz-fallback-{booking.id}"


def mark_user_paid(booking: Booking) -> None:
    """User-side: marks the booking as paid (pending therapist confirmation)."""
    if booking.state != BookingState.PENDING_PAYMENT:
        return
    booking.user_marked_paid_at = timezone.now()
    booking.state = BookingState.AWAITING_CONFIRMATION
    booking.save(update_fields=["state", "user_marked_paid_at", "updated_at"])
    notify.send_payment_marked(booking)


def confirm_payment(booking: Booking) -> None:
    """Therapist-side: confirms payment received, creates Daily.co room, notifies."""
    if booking.state != BookingState.AWAITING_CONFIRMATION:
        return
    booking.therapist_confirmed_at = timezone.now()
    booking.state = BookingState.CONFIRMED
    booking.daily_room_url = create_daily_room(booking)
    booking.save(
        update_fields=[
            "state",
            "therapist_confirmed_at",
            "daily_room_url",
            "updated_at",
        ]
    )
    notify.send_booking_confirmed(booking)


# Cancellable states — once the session is CONFIRMED we require manual mediation.
USER_CANCELLABLE = (BookingState.PENDING_PAYMENT, BookingState.AWAITING_CONFIRMATION)
THERAPIST_DECLINABLE = (
    BookingState.PENDING_PAYMENT,
    BookingState.AWAITING_CONFIRMATION,
)


def user_cancel(booking: Booking, reason: str = "") -> bool:
    """User-side cancellation. Returns True if the transition occurred."""
    if booking.state not in USER_CANCELLABLE:
        return False
    booking.state = BookingState.CANCELLED
    booking.cancellation_reason = reason[:255]
    booking.cancelled_by = "user"
    booking.save(
        update_fields=["state", "cancellation_reason", "cancelled_by", "updated_at"]
    )
    notify.send_booking_cancelled_by_user(booking)
    return True


def therapist_decline(booking: Booking, reason: str = "") -> bool:
    """Therapist-side decline. Returns True if the transition occurred."""
    if booking.state not in THERAPIST_DECLINABLE:
        return False
    booking.state = BookingState.CANCELLED
    booking.cancellation_reason = reason[:255]
    booking.cancelled_by = "therapist"
    booking.save(
        update_fields=["state", "cancellation_reason", "cancelled_by", "updated_at"]
    )
    notify.send_booking_declined(booking)
    return True


def auto_finalize_bookings(grace_minutes: int = 60) -> dict[str, int]:
    """Move CONFIRMED bookings whose slot ended >= grace_minutes ago to COMPLETED.

    Therapists can flip individual bookings to NO_SHOW manually in admin if a
    patient didn't attend. This is intentionally optimistic — the default is
    "the session happened" because that's the common case.
    """
    cutoff = timezone.now() - timedelta(minutes=grace_minutes)
    qs = Booking.objects.filter(state=BookingState.CONFIRMED, slot_end__lt=cutoff)
    count = qs.update(state=BookingState.COMPLETED, updated_at=timezone.now())
    return {"completed": count}


def send_session_reminders(window_hours: int = 24, lookahead_hours: int = 25) -> int:
    """Send T-24h reminders to both parties for upcoming CONFIRMED sessions.

    `reminder_sent_at` is set so a re-run inside the window doesn't double-send.
    """
    now = timezone.now()
    window_start = now + timedelta(hours=window_hours - 1)
    window_end = now + timedelta(hours=lookahead_hours)
    qs = Booking.objects.filter(
        state=BookingState.CONFIRMED,
        slot_start__gte=window_start,
        slot_start__lte=window_end,
        reminder_sent_at__isnull=True,
    )
    sent = 0
    for booking in qs.iterator():
        notify.send_session_reminder(booking)
        booking.reminder_sent_at = timezone.now()
        booking.save(update_fields=["reminder_sent_at", "updated_at"])
        sent += 1
    return sent


__all__ = [
    "ACTIVE_STATES",
    "auto_finalize_bookings",
    "confirm_payment",
    "create_daily_room",
    "mark_user_paid",
    "send_session_reminders",
    "therapist_decline",
    "user_cancel",
]
