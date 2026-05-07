"""Tests for the new lifecycle actions: decline, user-cancel, auto-finalize, reminders."""

from datetime import time, timedelta
from unittest.mock import patch

import pytest
from django.urls import reverse
from django.utils import timezone

from bookings.models import Booking, BookingState
from bookings.services import (
    auto_finalize_bookings,
    send_session_reminders,
    therapist_decline,
    user_cancel,
)
from core.factories import UserFactory
from therapists.tests.factories import AvailabilityFactory, TherapistProfileFactory


def _next_weekday_at(hour: int = 10):
    today = timezone.localdate()
    delta = (0 - today.weekday()) % 7 or 7
    target_date = today + timedelta(days=delta)
    return timezone.make_aware(
        timezone.datetime.combine(target_date, time(hour, 0)),
        timezone.get_current_timezone(),
    )


@pytest.fixture
def patient(db):
    user = UserFactory(email="patient@example.test")
    user.set_password("patient-pw-1!")
    user.save()
    return user


@pytest.fixture
def therapist_profile(db):
    profile = TherapistProfileFactory()
    AvailabilityFactory(
        therapist=profile, weekday=0, start_time=time(9), end_time=time(12)
    )
    return profile


@pytest.fixture
def booking(db, patient, therapist_profile):
    slot = _next_weekday_at(10)
    return Booking.objects.create(
        user=patient,
        therapist=therapist_profile,
        slot_start=slot,
        slot_end=slot + timedelta(hours=1),
    )


# ---------------- Therapist decline ----------------


def test_therapist_decline_transitions_to_cancelled(booking):
    assert therapist_decline(booking, reason="Indisponible ce jour") is True
    booking.refresh_from_db()
    assert booking.state == BookingState.CANCELLED
    assert booking.cancelled_by == "therapist"
    assert booking.cancellation_reason == "Indisponible ce jour"


def test_therapist_decline_after_confirmed_is_noop(booking):
    booking.state = BookingState.CONFIRMED
    booking.save()
    assert therapist_decline(booking) is False
    booking.refresh_from_db()
    assert booking.state == BookingState.CONFIRMED


def test_decline_view_via_http(client, booking, therapist_profile):
    therapist_profile.user.set_password("t-pw-1!")
    therapist_profile.user.save()
    client.login(email=therapist_profile.user.email, password="t-pw-1!")

    response = client.post(
        reverse("therapists:decline_booking", kwargs={"booking_id": booking.id}),
        {"reason": "Surbooké"},
    )
    assert response.status_code == 302
    booking.refresh_from_db()
    assert booking.state == BookingState.CANCELLED
    assert booking.cancellation_reason == "Surbooké"


# ---------------- User cancel ----------------


def test_user_cancel_in_pending_payment(booking):
    assert user_cancel(booking, reason="Plus disponible") is True
    booking.refresh_from_db()
    assert booking.state == BookingState.CANCELLED
    assert booking.cancelled_by == "user"


def test_user_cancel_after_confirmed_is_blocked(booking):
    booking.state = BookingState.CONFIRMED
    booking.save()
    assert user_cancel(booking) is False
    booking.refresh_from_db()
    assert booking.state == BookingState.CONFIRMED


def test_cancel_view_via_http(client, booking, patient):
    client.login(email=patient.email, password="patient-pw-1!")
    response = client.post(
        reverse("bookings:cancel", kwargs={"booking_id": booking.id}),
        {"reason": "Empêchement"},
    )
    assert response.status_code == 302
    booking.refresh_from_db()
    assert booking.state == BookingState.CANCELLED


def test_user_cannot_cancel_other_users_booking(client, booking, db):
    other = UserFactory(email="other@example.test")
    other.set_password("o-pw!")
    other.save()
    client.login(email=other.email, password="o-pw!")
    response = client.post(
        reverse("bookings:cancel", kwargs={"booking_id": booking.id}),
    )
    assert response.status_code == 404
    booking.refresh_from_db()
    assert booking.state == BookingState.PENDING_PAYMENT


# ---------------- Auto-finalize ----------------


def test_auto_finalize_completes_past_confirmed(booking):
    booking.state = BookingState.CONFIRMED
    booking.slot_end = timezone.now() - timedelta(hours=2)
    booking.slot_start = booking.slot_end - timedelta(hours=1)
    booking.save()

    result = auto_finalize_bookings(grace_minutes=60)
    assert result["completed"] == 1
    booking.refresh_from_db()
    assert booking.state == BookingState.COMPLETED


def test_auto_finalize_skips_future_sessions(booking):
    booking.state = BookingState.CONFIRMED
    booking.save()
    result = auto_finalize_bookings(grace_minutes=60)
    assert result["completed"] == 0


# ---------------- Session reminders ----------------


def test_send_session_reminders_targets_t_minus_24h(booking):
    booking.state = BookingState.CONFIRMED
    soon = timezone.now() + timedelta(hours=23, minutes=30)
    booking.slot_start = soon
    booking.slot_end = soon + timedelta(hours=1)
    booking.save()

    with patch("notifications.email.send", return_value=True) as mock_send:
        sent = send_session_reminders(window_hours=24, lookahead_hours=25)

    assert sent == 1
    booking.refresh_from_db()
    assert booking.reminder_sent_at is not None
    # Two send() calls: one for user, one for therapist
    assert mock_send.call_count == 2


def test_send_session_reminders_idempotent(booking):
    booking.state = BookingState.CONFIRMED
    soon = timezone.now() + timedelta(hours=23, minutes=30)
    booking.slot_start = soon
    booking.slot_end = soon + timedelta(hours=1)
    booking.reminder_sent_at = timezone.now()  # already sent
    booking.save()

    with patch("notifications.email.send", return_value=True) as mock_send:
        sent = send_session_reminders()

    assert sent == 0
    assert mock_send.call_count == 0


# ---------------- Receipt validation ----------------


def test_mark_paid_rejects_oversize_receipt(client, booking, patient):
    from django.core.files.uploadedfile import SimpleUploadedFile

    client.login(email=patient.email, password="patient-pw-1!")
    big_file = SimpleUploadedFile(
        "huge.pdf",
        b"x" * (6 * 1024 * 1024),  # 6 MB > 5 MB limit
        content_type="application/pdf",
    )
    response = client.post(
        reverse("bookings:mark_paid", kwargs={"booking_id": booking.id}),
        {"receipt": big_file},
    )
    # Form re-renders with error → 200, no state change
    assert response.status_code == 200
    booking.refresh_from_db()
    assert booking.state == BookingState.PENDING_PAYMENT


def test_mark_paid_rejects_bad_content_type(client, booking, patient):
    from django.core.files.uploadedfile import SimpleUploadedFile

    client.login(email=patient.email, password="patient-pw-1!")
    bad_file = SimpleUploadedFile(
        "evil.exe",
        b"MZ\x90\x00",
        content_type="application/x-msdownload",
    )
    response = client.post(
        reverse("bookings:mark_paid", kwargs={"booking_id": booking.id}),
        {"receipt": bad_file},
    )
    assert response.status_code == 200
    booking.refresh_from_db()
    assert booking.state == BookingState.PENDING_PAYMENT


def test_mark_paid_accepts_pdf(client, booking, patient):
    from django.core.files.uploadedfile import SimpleUploadedFile

    client.login(email=patient.email, password="patient-pw-1!")
    good = SimpleUploadedFile(
        "receipt.pdf",
        b"%PDF-1.4 fake pdf",
        content_type="application/pdf",
    )
    response = client.post(
        reverse("bookings:mark_paid", kwargs={"booking_id": booking.id}),
        {"receipt": good},
    )
    assert response.status_code == 302
    booking.refresh_from_db()
    assert booking.state == BookingState.AWAITING_CONFIRMATION


# ---------------- Slot-collision constraint ----------------


def test_slot_collision_blocked_by_constraint(booking, db):
    from django.db import IntegrityError

    with pytest.raises(IntegrityError):
        Booking.objects.create(
            user=booking.user,
            therapist=booking.therapist,
            slot_start=booking.slot_start,
            slot_end=booking.slot_end,
        )
