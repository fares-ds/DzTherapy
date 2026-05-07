"""Booking lifecycle helpers — Daily.co room creation, state transitions."""

from __future__ import annotations

import logging

import requests
from django.conf import settings
from django.utils import timezone

from bookings.models import Booking, BookingState
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
