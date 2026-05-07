from datetime import time, timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from bookings.models import Booking, BookingState
from core.factories import UserFactory
from therapists.tests.factories import AvailabilityFactory, TherapistProfileFactory


def _next_weekday_at(hour: int = 10):
    """Return an aware datetime for the next occurrence of weekday=0 at `hour`."""
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


def test_full_booking_flow(client, patient, therapist_profile):
    client.login(email=patient.email, password="patient-pw-1!")

    slot = _next_weekday_at(10)

    # Step 1: create booking
    response = client.post(
        reverse("bookings:create", kwargs={"therapist_slug": therapist_profile.slug}),
        {
            "slot": slot.isoformat(),
            "user_notes": "Anxiété au travail",
            "accept_disclaimer": "on",
        },
        follow=False,
    )
    assert response.status_code == 302
    booking = Booking.objects.get(user=patient, therapist=therapist_profile)
    assert booking.state == BookingState.PENDING_PAYMENT

    # Step 2: user marks paid
    response = client.post(
        reverse("bookings:mark_paid", kwargs={"booking_id": booking.id}),
        {},
        follow=False,
    )
    assert response.status_code == 302
    booking.refresh_from_db()
    assert booking.state == BookingState.AWAITING_CONFIRMATION
    assert booking.user_marked_paid_at is not None

    # Step 3: therapist confirms
    therapist_user = therapist_profile.user
    therapist_user.set_password("therapist-pw-1!")
    therapist_user.save()
    client.logout()
    client.login(email=therapist_user.email, password="therapist-pw-1!")

    response = client.post(
        reverse("therapists:confirm_payment", kwargs={"booking_id": booking.id}),
        follow=False,
    )
    assert response.status_code == 302
    booking.refresh_from_db()
    assert booking.state == BookingState.CONFIRMED
    assert booking.therapist_confirmed_at is not None
    assert booking.daily_room_url  # stub URL is fine in test


def test_create_booking_rejects_past_slot(client, patient, therapist_profile):
    client.login(email=patient.email, password="patient-pw-1!")
    past = (timezone.now() - timedelta(hours=1)).isoformat()
    response = client.post(
        reverse("bookings:create", kwargs={"therapist_slug": therapist_profile.slug}),
        {"slot": past, "user_notes": "", "accept_disclaimer": "on"},
        follow=False,
    )
    # Redirected back to therapist detail; no booking created
    assert response.status_code == 302
    assert Booking.objects.count() == 0


def test_therapist_cannot_book(client, therapist_profile):
    therapist_profile.user.set_password("t-pw-1!")
    therapist_profile.user.save()
    client.login(email=therapist_profile.user.email, password="t-pw-1!")

    other = TherapistProfileFactory()
    response = client.post(
        reverse("bookings:create", kwargs={"therapist_slug": other.slug}),
        {"slot": _next_weekday_at(10).isoformat(), "accept_disclaimer": "on"},
    )
    assert response.status_code == 400
